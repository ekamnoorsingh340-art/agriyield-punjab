"""
AgriYield Punjab — Unified ML Training Dataset Builder
Merges verified DES historical crop yields (1997-2023), district source-wise
irrigation panels (2020-2025), and PAU Package of Practices benchmarks into an
ML-ready master panel with strict temporal & institutional anomaly guards.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd


# Maps DES crop labels + canonical season to PAU benchmark crop groups
DES_TO_PAU_CROP_MAP: Dict[Tuple[str, str], str] = {
    ("Rice", "Kharif"): "Paddy",
    ("Rice", "Autumn"): "Paddy",
    ("Rice", "Winter"): "Paddy",
    ("Rice", "Total"): "Paddy",
    ("Wheat", "Rabi"): "Wheat",
    ("Wheat", "Total"): "Wheat",
    ("Potato", "Rabi"): "Potato",
    ("Potato", "Autumn"): "Potato",
    ("Potato", "Total"): "Potato",
    ("Moong", "Summer"): "Summer_Moong",
    ("Moong", "Zaid"): "Summer_Moong",
    ("Moong", "Total"): "Summer_Moong",
}


def build_pau_crop_summary(pau_json_path: Path) -> pd.DataFrame:
    """Aggregate variety-level PAU Package of Practices benchmarks to crop level."""
    payload = json.loads(pau_json_path.read_text(encoding="utf-8"))
    varieties = payload.get("varieties", {})
    rows: List[dict] = []

    for variety_name, info in varieties.items():
        npk = info.get("recommended_npk_kg_ekad", {})
        fert = info.get("recommended_fertilizer_kg_ekad", {})
        bags = info.get("recommended_bags_ekad", {})
        rows.append(
            {
                "pau_crop_group": info["crop"],
                "pau_season": info["season"],
                "variety_name": variety_name,
                "duration_days": float(info["duration_days"]),
                "pau_avg_yield_q_ekad": float(info["pau_avg_yield_q_ekad"]),
                "rec_n_kg_ekad": float(npk.get("N", 0.0)),
                "rec_p2o5_kg_ekad": float(npk.get("P2O5", 0.0)),
                "rec_k2o_kg_ekad": float(npk.get("K2O", 0.0)),
                "rec_urea_kg_ekad": float(fert.get("Urea", 0.0)),
                "rec_dap_kg_ekad": float(fert.get("DAP", 0.0)),
                "rec_mop_kg_ekad": float(fert.get("MOP", 0.0)),
                "rec_urea_bags_ekad": float(bags.get("Urea", 0.0)),
                "rec_dap_bags_ekad": float(bags.get("DAP", 0.0)),
                "rec_mop_bags_ekad": float(bags.get("MOP", 0.0)),
            }
        )

    var_df = pd.DataFrame(rows)
    if var_df.empty:
        return pd.DataFrame(columns=["pau_crop_group"])

    # Identify top-yielding benchmark variety per PAU crop group
    idx_top = var_df.groupby("pau_crop_group")["pau_avg_yield_q_ekad"].idxmax()
    top_df = var_df.loc[
        idx_top,
        [
            "pau_crop_group",
            "variety_name",
            "duration_days",
            "pau_avg_yield_q_ekad",
            "rec_n_kg_ekad",
            "rec_p2o5_kg_ekad",
            "rec_k2o_kg_ekad",
            "rec_urea_bags_ekad",
            "rec_dap_bags_ekad",
            "rec_mop_bags_ekad",
        ],
    ].rename(
        columns={
            "variety_name": "pau_top_variety",
            "duration_days": "pau_top_variety_duration_days",
            "pau_avg_yield_q_ekad": "pau_max_benchmark_q_ekad",
        }
    )

    agg_df = (
        var_df.groupby("pau_crop_group", as_index=False)
        .agg(
            pau_mean_benchmark_q_ekad=("pau_avg_yield_q_ekad", "mean"),
            pau_min_duration_days=("duration_days", "min"),
            pau_max_duration_days=("duration_days", "max"),
            pau_variety_count=("variety_name", "count"),
        )
        .merge(top_df, on="pau_crop_group", how="left")
    )
    agg_df["pau_mean_benchmark_q_ekad"] = agg_df["pau_mean_benchmark_q_ekad"].round(2)
    return agg_df


def build_structural_irrigation_baseline(irr_df: pd.DataFrame) -> pd.DataFrame:
    """
    Build a static per-district irrigation profile using the latest verified
    non-anomalous year (2024-25 for 22 districts; 2023-24 fallback for Kapurthala
    due to 2024-25 provisional net-area portal distortion).
    """
    df = irr_df.copy()
    df["portal_anomaly_flag"] = df["portal_anomaly_flag"].fillna("").astype(str).str.strip()

    clean_df = df[df["portal_anomaly_flag"] == ""].sort_values("year_start")
    latest_clean = clean_df.groupby("district_nabard", as_index=False).last()

    # Check if latest overall year had an anomaly for any district
    latest_overall = df.sort_values("year_start").groupby("district_nabard", as_index=False).last()
    anomalous_districts = set(
        latest_overall.loc[latest_overall["portal_anomaly_flag"] != "", "district_nabard"]
    )

    baseline = latest_clean[
        [
            "district_nabard",
            "crop_year",
            "tubewell_share_net_pct",
            "canal_share_net_pct",
            "irrigation_intensity_pct",
            "net_irrigated_total_ekad",
        ]
    ].rename(
        columns={
            "crop_year": "baseline_irrigation_year",
            "tubewell_share_net_pct": "baseline_tubewell_share_pct",
            "canal_share_net_pct": "baseline_canal_share_pct",
            "irrigation_intensity_pct": "baseline_irrigation_intensity_pct",
            "net_irrigated_total_ekad": "baseline_net_irrigated_ekad",
        }
    )
    baseline["baseline_irrigation_anomaly_fallback"] = baseline["district_nabard"].isin(
        anomalous_districts
    )
    return baseline


def build_master_training_panel(
    des_csv_path: Path,
    irr_csv_path: Path,
    pau_json_path: Path,
    out_dir: Path,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Merge DES yields, irrigation metrics, and PAU benchmarks into master panel."""
    des_df = pd.read_csv(des_csv_path)
    irr_df = pd.read_csv(irr_csv_path)

    des_df.columns = [c.strip().lower() for c in des_df.columns]
    irr_df.columns = [c.strip().lower() for c in irr_df.columns]

    # 1. Exact-year irrigation join (preserves NaN for pre-2020 historical years; zero fabrication)
    irr_yearly_cols = [
        "district_nabard",
        "crop_year",
        "net_canal_total_ha",
        "net_tubewell_ha",
        "net_irrigated_total_ha",
        "net_irrigated_total_ekad",
        "gross_irrigated_total_ekad",
        "tubewell_share_net_pct",
        "canal_share_net_pct",
        "irrigation_intensity_pct",
        "portal_anomaly_flag",
    ]
    irr_yearly = irr_df[irr_yearly_cols].rename(
        columns={"portal_anomaly_flag": "yearly_irrigation_anomaly_flag"}
    )

    panel = des_df.merge(
        irr_yearly,
        on=["district_nabard", "crop_year"],
        how="left",
        validate="many_to_one",
    )

    # 2. Static district irrigation structural baseline (2024-25 verified / 2023-24 fallback)
    baseline_irr = build_structural_irrigation_baseline(irr_df)
    panel = panel.merge(
        baseline_irr,
        on="district_nabard",
        how="left",
        validate="many_to_one",
    )

    # 3. Map DES crops to PAU Package of Practices benchmarks
    def _resolve_pau_group(row: pd.Series) -> Optional[str]:
        crop = str(row.get("crop", "")).strip()
        season = str(row.get("season_canonical", "")).strip()
        if (crop, season) in DES_TO_PAU_CROP_MAP:
            return DES_TO_PAU_CROP_MAP[(crop, season)]
        if (crop, "Total") in DES_TO_PAU_CROP_MAP:
            return DES_TO_PAU_CROP_MAP[(crop, "Total")]
        return None

    panel["pau_crop_group"] = panel.apply(_resolve_pau_group, axis=1)
    pau_summary = build_pau_crop_summary(pau_json_path)
    panel = panel.merge(pau_summary, on="pau_crop_group", how="left")

    # Compute PAU benchmark yield gap (%) where both observed yield and PAU benchmark exist
    valid_bench = panel["pau_mean_benchmark_q_ekad"].notna() & panel["yield_quintal_per_ekad"].notna()
    panel["yield_gap_vs_pau_mean_q_ekad"] = np.where(
        valid_bench,
        (panel["pau_mean_benchmark_q_ekad"] - panel["yield_quintal_per_ekad"]).round(2),
        np.nan,
    )
    panel["yield_attainment_vs_pau_pct"] = np.where(
        valid_bench & (panel["pau_mean_benchmark_q_ekad"] > 0),
        ((panel["yield_quintal_per_ekad"] / panel["pau_mean_benchmark_q_ekad"]) * 100.0).round(2),
        np.nan,
    )

    # 4. Leak-free historical yield lag features per (district_nabard, crop, season_canonical)
    panel = panel.sort_values(
        ["district_nabard", "crop", "season_canonical", "year_start"]
    ).reset_index(drop=True)

    grp = panel.groupby(["district_nabard", "crop", "season_canonical"], sort=False)
    panel["prev_year_start"] = grp["year_start"].shift(1)
    panel["yield_q_ekad_lag1"] = np.where(
        (panel["year_start"] - panel["prev_year_start"]) == 1,
        grp["yield_quintal_per_ekad"].shift(1),
        np.nan,
    )
    panel["yield_q_ekad_roll3_mean"] = (
        grp["yield_quintal_per_ekad"]
        .transform(lambda s: s.shift(1).rolling(window=3, min_periods=2).mean())
        .round(2)
    )
    panel = panel.drop(columns=["prev_year_start"])

    # Clean flag strings
    for flag_col in ["data_quality_flag", "district_lineage_note", "yearly_irrigation_anomaly_flag"]:
        if flag_col in panel.columns:
            panel[flag_col] = panel[flag_col].fillna("").astype(str).str.strip()

    out_dir.mkdir(parents=True, exist_ok=True)
    master_out = out_dir / "agriyield_punjab_master_panel.csv"
    pau_out = out_dir / "pau_crop_benchmarks_summary.csv"

    panel.to_csv(master_out, index=False)
    pau_summary.to_csv(pau_out, index=False)
    return panel, pau_summary


def main() -> None:
    parser = argparse.ArgumentParser(description="Build unified AgriYield Punjab ML dataset.")
    parser.add_argument(
        "--des-csv",
        type=Path,
        default=Path("data/processed/des_punjab_crop_yield_1997_2023.csv"),
    )
    parser.add_argument(
        "--irr-csv",
        type=Path,
        default=Path("data/processed/punjab_district_irrigation_2020_2025.csv"),
    )
    parser.add_argument(
        "--pau-json",
        type=Path,
        default=Path("data/pau_benchmarks.json"),
    )
    parser.add_argument(
        "--out-dir",
        type=Path,
        default=Path("data/processed"),
    )
    args = parser.parse_args()

    panel, pau_summary = build_master_training_panel(
        des_csv_path=args.des_csv,
        irr_csv_path=args.irr_csv,
        pau_json_path=args.pau_json,
        out_dir=args.out_dir,
    )
    print(
        f"Built master training panel: {len(panel)} rows x {len(panel.columns)} cols | "
        f"PAU benchmark groups: {len(pau_summary)}"
    )


if __name__ == "__main__":
    main()
