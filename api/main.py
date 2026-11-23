"""
AgriYield Punjab — FastAPI ML & Agronomic Advisory Backend
Serves verified Punjab district irrigation profiles, PAU Ludhiana Package of
Practices benchmarks, and live ML yield predictions (quintals/ekad) for
Cloudflare Pages and mobile clients.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Optional

import joblib
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field


BASE_DIR = Path(__file__).resolve().parent.parent
MODEL_PATH = BASE_DIR / "models" / "agriyield_punjab_model.joblib"
METRICS_PATH = BASE_DIR / "models" / "model_metrics.json"
LOOKUP_PATH = BASE_DIR / "models" / "inference_lookup.json"
PAU_PATH = BASE_DIR / "data" / "pau_benchmarks.json"

FEATURE_COLS: List[str] = [
    "district_nabard",
    "nabard_az_code",
    "crop",
    "season_canonical",
    "year_start",
    "area_ekad",
    "baseline_tubewell_share_pct",
    "baseline_canal_share_pct",
    "baseline_irrigation_intensity_pct",
    "yield_q_ekad_lag1",
    "yield_q_ekad_roll3_mean",
]

# Maps DES crop + season to PAU benchmark crop groups (including Basmati split)
PAU_GROUP_ALIASES: Dict[str, List[str]] = {
    "Rice": ["Paddy", "Basmati"],
    "Wheat": ["Wheat"],
    "Potato": ["Potato"],
    "Moong": ["Summer_Moong"],
}


def _load_artifacts() -> Dict[str, Any]:
    if not MODEL_PATH.exists():
        raise RuntimeError(f"Missing trained model artifact at {MODEL_PATH}")
    return {
        "model": joblib.load(MODEL_PATH),
        "metrics": json.loads(METRICS_PATH.read_text(encoding="utf-8")),
        "lookup": json.loads(LOOKUP_PATH.read_text(encoding="utf-8")),
        "pau": json.loads(PAU_PATH.read_text(encoding="utf-8")),
    }


ARTIFACTS = _load_artifacts()

app = FastAPI(
    title="AgriYield Punjab API",
    description="Open-source institutional crop yield prediction & PAU advisory API for Punjab farmers.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)


class PredictionRequest(BaseModel):
    district: str = Field(..., examples=["Bathinda"])
    crop: str = Field(..., examples=["Wheat"])
    season: str = Field(..., examples=["Rabi"])
    area_ekad: float = Field(default=1.0, gt=0, le=100000, examples=[5.0])
    variety: Optional[str] = Field(default=None, examples=["PBW 826"])
    target_year_start: int = Field(default=2026, ge=2024, le=2035)


@app.get("/health")
def health() -> Dict[str, Any]:
    return {
        "status": "ok",
        "service": "agriyield-punjab-api",
        "model_r2": ARTIFACTS["metrics"].get("temporal_holdout_r2"),
        "model_rmse_q_ekad": ARTIFACTS["metrics"].get("temporal_holdout_rmse_q_ekad"),
    }


@app.get("/metadata")
def get_metadata() -> Dict[str, Any]:
    """Return available districts, crops, seasons, PAU varieties, and model metrics."""
    lookup: Dict[str, dict] = ARTIFACTS["lookup"]
    districts_map: Dict[str, dict] = {}
    combinations: List[dict] = []

    for entry in lookup.values():
        d = entry["district_nabard"]
        if d not in districts_map:
            districts_map[d] = {
                "district": d,
                "nabard_az_code": entry["nabard_az_code"],
                "nabard_az_name": entry["nabard_az_name"],
                "baseline_tubewell_share_pct": entry["baseline_tubewell_share_pct"],
                "baseline_canal_share_pct": entry["baseline_canal_share_pct"],
                "baseline_irrigation_intensity_pct": entry["baseline_irrigation_intensity_pct"],
            }
        combinations.append(
            {
                "district": d,
                "crop": entry["crop"],
                "season": entry["season_canonical"],
                "latest_observed_year": entry["latest_observed_year"],
                "latest_yield_q_ekad": entry["latest_yield_q_ekad"],
            }
        )

    return {
        "districts": sorted(districts_map.values(), key=lambda x: x["district"]),
        "combinations": combinations,
        "pau_varieties": ARTIFACTS["pau"].get("varieties", {}),
        "pau_metadata": ARTIFACTS["pau"].get("metadata", {}),
        "model_metrics": ARTIFACTS["metrics"],
    }


@app.post("/predict")
def predict_yield(req: PredictionRequest) -> Dict[str, Any]:
    lookup: Dict[str, dict] = ARTIFACTS["lookup"]
    key = f"{req.district.strip()}||{req.crop.strip()}||{req.season.strip()}"

    if key not in lookup:
        raise HTTPException(
            status_code=404,
            detail=f"No historical baseline found for {req.district} / {req.crop} / {req.season}.",
        )

    state = lookup[key]
    features_df = pd.DataFrame(
        [
            {
                "district_nabard": state["district_nabard"],
                "nabard_az_code": state["nabard_az_code"],
                "crop": state["crop"],
                "season_canonical": state["season_canonical"],
                "year_start": req.target_year_start,
                "area_ekad": state["latest_area_ekad"],
                "baseline_tubewell_share_pct": state["baseline_tubewell_share_pct"],
                "baseline_canal_share_pct": state["baseline_canal_share_pct"],
                "baseline_irrigation_intensity_pct": state["baseline_irrigation_intensity_pct"],
                "yield_q_ekad_lag1": state["latest_yield_q_ekad"],
                "yield_q_ekad_roll3_mean": state["recent_3yr_mean_q_ekad"],
            }
        ]
    )[FEATURE_COLS]

    pred_q_ekad = round(float(ARTIFACTS["model"].predict(features_df)[0]), 2)
    total_quintals = round(pred_q_ekad * req.area_ekad, 2)

    # Resolve PAU variety benchmark & scaled fertilizer bag calculation
    varieties: Dict[str, dict] = ARTIFACTS["pau"].get("varieties", {})
    allowed_groups = PAU_GROUP_ALIASES.get(state["crop"], [])
    matching_varieties = {
        v_name: v_info
        for v_name, v_info in varieties.items()
        if v_info.get("crop") in allowed_groups
    }

    selected_variety_name: Optional[str] = None
    selected_variety_info: Optional[dict] = None
    scaled_fertilizer_bags: Optional[dict] = None
    scaled_fertilizer_kg: Optional[dict] = None
    benchmark_gap_q_ekad: Optional[float] = None

    if req.variety and req.variety in matching_varieties:
        selected_variety_name = req.variety
        selected_variety_info = matching_varieties[req.variety]
    elif matching_varieties:
        selected_variety_name = next(iter(matching_varieties))
        selected_variety_info = matching_varieties[selected_variety_name]

    if selected_variety_info:
        pau_bench = float(selected_variety_info["pau_avg_yield_q_ekad"])
        benchmark_gap_q_ekad = round(pau_bench - pred_q_ekad, 2)
        bags_per_ekad = selected_variety_info.get("recommended_bags_ekad", {})
        kg_per_ekad = selected_variety_info.get("recommended_fertilizer_kg_ekad", {})
        scaled_fertilizer_bags = {
            k: round(float(v) * req.area_ekad, 1) for k, v in bags_per_ekad.items()
        }
        scaled_fertilizer_kg = {
            k: round(float(v) * req.area_ekad, 1) for k, v in kg_per_ekad.items()
        }

    return {
        "district": state["district_nabard"],
        "nabard_agro_climatic_zone": {
            "code": state["nabard_az_code"],
            "name": state["nabard_az_name"],
        },
        "crop": state["crop"],
        "season": state["season_canonical"],
        "area_ekad": req.area_ekad,
        "prediction": {
            "expected_yield_q_ekad": pred_q_ekad,
            "total_expected_production_quintals": total_quintals,
            "latest_des_observed_year": state["latest_observed_year"],
            "latest_des_yield_q_ekad": state["latest_yield_q_ekad"],
            "recent_3yr_mean_q_ekad": state["recent_3yr_mean_q_ekad"],
        },
        "district_irrigation_profile": {
            "tubewell_share_pct": state["baseline_tubewell_share_pct"],
            "canal_share_pct": state["baseline_canal_share_pct"],
            "irrigation_intensity_pct": state["baseline_irrigation_intensity_pct"],
        },
        "pau_advisory": {
            "selected_variety": selected_variety_name,
            "variety_details": selected_variety_info,
            "available_varieties": list(matching_varieties.keys()),
            "yield_gap_vs_pau_q_ekad": benchmark_gap_q_ekad,
            "total_fertilizer_bags_for_area": scaled_fertilizer_bags,
            "total_fertilizer_kg_for_area": scaled_fertilizer_kg,
        },
    }
