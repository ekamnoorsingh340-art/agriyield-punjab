"""
AgriYield Punjab — ML Yield Prediction Model Trainer
Trains and validates a scikit-learn HistGradientBoostingRegressor pipeline on
the verified AgriYield Punjab master panel (yield in quintals/ekad) using a
strict temporal out-of-sample holdout (train < 2020, test >= 2020).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OrdinalEncoder


CATEGORICAL_FEATURES: List[str] = [
    "district_nabard",
    "nabard_az_code",
    "crop",
    "season_canonical",
]

NUMERIC_FEATURES: List[str] = [
    "year_start",
    "area_ekad",
    "baseline_tubewell_share_pct",
    "baseline_canal_share_pct",
    "baseline_irrigation_intensity_pct",
    "yield_q_ekad_lag1",
    "yield_q_ekad_roll3_mean",
]

TARGET_COL = "yield_quintal_per_ekad"


def build_pipeline() -> Pipeline:
    """Create scikit-learn preprocessing + gradient boosting regression pipeline."""
    preprocessor = ColumnTransformer(
        transformers=[
            (
                "cat",
                OrdinalEncoder(
                    handle_unknown="use_encoded_value",
                    unknown_value=-1,
                    encoded_missing_value=-2,
                ),
                CATEGORICAL_FEATURES,
            ),
            ("num", "passthrough", NUMERIC_FEATURES),
        ]
    )

    regressor = HistGradientBoostingRegressor(
        max_iter=300,
        learning_rate=0.05,
        max_leaf_nodes=31,
        min_samples_leaf=15,
        l2_regularization=1.0,
        categorical_features=[0, 1, 2, 3],
        random_state=42,
    )

    return Pipeline(
        steps=[
            ("preprocessor", preprocessor),
            ("regressor", regressor),
        ]
    )


def prepare_training_frame(master_csv_path: Path) -> pd.DataFrame:
    """Load master panel and filter to clean rows with valid target yield."""
    df = pd.read_csv(master_csv_path)
    df.columns = [c.strip().lower() for c in df.columns]

    # Exclude aggregate 'Total' season rows where specific seasons exist, and require valid target
    df = df[df[TARGET_COL].notna() & (df[TARGET_COL] > 0)].copy()

    # Exclude flagged quality anomalies if present
    if "data_quality_flag" in df.columns:
        flags = df["data_quality_flag"].fillna("").astype(str).str.strip()
        df = df[flags == ""].copy()

    for col in CATEGORICAL_FEATURES:
        df[col] = df[col].fillna("Unknown").astype(str).str.strip()

    for col in NUMERIC_FEATURES:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    return df.sort_values(
        ["district_nabard", "crop", "season_canonical", "year_start"]
    ).reset_index(drop=True)


def build_inference_lookup(df: pd.DataFrame) -> Dict[str, dict]:
    """
    Build latest per-(district, crop, season) state dictionary so the Streamlit
    frontend can populate lag features and structural irrigation automatically.
    """
    lookup: Dict[str, dict] = {}
    grouped = df.groupby(["district_nabard", "crop", "season_canonical"], sort=True)

    for (district, crop, season), grp in grouped:
        grp_sorted = grp.sort_values("year_start")
        latest = grp_sorted.iloc[-1]
        recent_3 = grp_sorted.tail(3)[TARGET_COL].mean()

        key = f"{district}||{crop}||{season}"
        lookup[key] = {
            "district_nabard": district,
            "nabard_az_code": str(latest["nabard_az_code"]),
            "nabard_az_name": str(latest.get("nabard_az_name", "")),
            "crop": crop,
            "season_canonical": season,
            "latest_observed_year": str(latest["crop_year"]),
            "latest_year_start": int(latest["year_start"]),
            "latest_area_ekad": float(latest["area_ekad"]) if pd.notna(latest["area_ekad"]) else 10000.0,
            "latest_yield_q_ekad": round(float(latest[TARGET_COL]), 2),
            "recent_3yr_mean_q_ekad": round(float(recent_3), 2),
            "baseline_tubewell_share_pct": (
                round(float(latest["baseline_tubewell_share_pct"]), 2)
                if pd.notna(latest["baseline_tubewell_share_pct"])
                else None
            ),
            "baseline_canal_share_pct": (
                round(float(latest["baseline_canal_share_pct"]), 2)
                if pd.notna(latest["baseline_canal_share_pct"])
                else None
            ),
            "baseline_irrigation_intensity_pct": (
                round(float(latest["baseline_irrigation_intensity_pct"]), 2)
                if pd.notna(latest["baseline_irrigation_intensity_pct"])
                else None
            ),
            "pau_crop_group": (
                str(latest["pau_crop_group"])
                if pd.notna(latest.get("pau_crop_group"))
                else None
            ),
        }
    return lookup


def train_and_evaluate(
    master_csv_path: Path,
    models_dir: Path,
    holdout_year_start: int = 2020,
) -> Tuple[Pipeline, dict]:
    """Evaluate temporally on holdout years, refit on full dataset, and export artifacts."""
    df = prepare_training_frame(master_csv_path)
    feature_cols = CATEGORICAL_FEATURES + NUMERIC_FEATURES

    train_df = df[df["year_start"] < holdout_year_start]
    test_df = df[df["year_start"] >= holdout_year_start]

    eval_pipeline = build_pipeline()
    eval_pipeline.fit(train_df[feature_cols], train_df[TARGET_COL])

    preds = eval_pipeline.predict(test_df[feature_cols])
    y_true = test_df[TARGET_COL].to_numpy()

    r2 = float(r2_score(y_true, preds))
    mae = float(mean_absolute_error(y_true, preds))
    rmse = float(np.sqrt(mean_squared_error(y_true, preds)))

    # Refit final production model on all verified historical records
    final_pipeline = build_pipeline()
    final_pipeline.fit(df[feature_cols], df[TARGET_COL])

    metrics = {
        "model_type": "HistGradientBoostingRegressor",
        "target_unit": "quintals_per_ekad",
        "total_clean_records": int(len(df)),
        "train_records_pre_2020": int(len(train_df)),
        "test_records_2020_plus": int(len(test_df)),
        "holdout_split_year_start": int(holdout_year_start),
        "temporal_holdout_r2": round(r2, 4),
        "temporal_holdout_mae_q_ekad": round(mae, 3),
        "temporal_holdout_rmse_q_ekad": round(rmse, 3),
        "categorical_features": CATEGORICAL_FEATURES,
        "numeric_features": NUMERIC_FEATURES,
    }

    models_dir.mkdir(parents=True, exist_ok=True)
    model_path = models_dir / "agriyield_punjab_model.joblib"
    metrics_path = models_dir / "model_metrics.json"
    lookup_path = models_dir / "inference_lookup.json"

    joblib.dump(final_pipeline, model_path)
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    lookup_path.write_text(
        json.dumps(build_inference_lookup(df), indent=2), encoding="utf-8"
    )

    return final_pipeline, metrics


def main() -> None:
    parser = argparse.ArgumentParser(description="Train AgriYield Punjab ML model.")
    parser.add_argument(
        "--master-csv",
        type=Path,
        default=Path("data/processed/agriyield_punjab_master_panel.csv"),
    )
    parser.add_argument(
        "--models-dir",
        type=Path,
        default=Path("models"),
    )
    parser.add_argument(
        "--holdout-year",
        type=int,
        default=2020,
    )
    args = parser.parse_args()

    _, metrics = train_and_evaluate(
        master_csv_path=args.master_csv,
        models_dir=args.models_dir,
        holdout_year_start=args.holdout_year,
    )
    print(
        f"Model trained ({metrics['total_clean_records']} rows) | "
        f"Temporal Holdout R2={metrics['temporal_holdout_r2']} | "
        f"RMSE={metrics['temporal_holdout_rmse_q_ekad']} q/ekad"
    )


if __name__ == "__main__":
    main()
