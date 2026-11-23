import argparse
import re
from pathlib import Path
from typing import Iterable, List

import pandas as pd

from etl.district_zones import resolve_district_classification

HA_TO_EKAD = 2.47105


def _extract_reporting_year(table_title: str) -> tuple[str, int]:
    match = re.search(r"(20\d{2})\s*-\s*(20\d{2})", table_title)
    if not match:
        raise ValueError(f"Could not extract reporting year from title: '{table_title}'")
    year_start = int(match.group(1))
    year_end = int(match.group(2))
    return f"{year_start}-{str(year_end)[-2:]}", year_start


def parse_single_irrigation_html(filepath: Path) -> pd.DataFrame:
    tables = pd.read_html(filepath)
    if not tables:
        raise ValueError(f"No HTML tables found in {filepath}")
    raw = tables[0]
    if raw.shape != (25, 20):
        raise ValueError(f"Expected shape (25, 20) in {filepath}, got {raw.shape}")

    title = str(raw.columns[0][0])
    crop_year, year_start = _extract_reporting_year(title)

    banner_cell = str(raw.iloc[0, 1]).strip()
    total_cell = str(raw.iloc[24, 1]).strip()
    if banner_cell != "State: Punjab" or total_cell != "Total of Punjab":
        raise ValueError(
            f"Unexpected row layout in {filepath}: row0='{banner_cell}', row24='{total_cell}'"
        )

    sub = raw.iloc[1:24].copy()
    for col_idx in range(2, 20):
        sub.iloc[:, col_idx] = pd.to_numeric(
            sub.iloc[:, col_idx].astype(str).str.strip().replace("-", "0"),
            errors="raise",
        )

    # Verify internal row arithmetic (0.00 ha tolerance)
    net_sum = sub.iloc[:, 4] + sub.iloc[:, 5] + sub.iloc[:, 8] + sub.iloc[:, 9]
    gross_sum = sub.iloc[:, 13] + sub.iloc[:, 14] + sub.iloc[:, 17] + sub.iloc[:, 18]
    if (net_sum - sub.iloc[:, 10]).abs().max() > 1e-6:
        raise ValueError(f"Net irrigated area row sum mismatch in {filepath}")
    if (gross_sum - sub.iloc[:, 19]).abs().max() > 1e-6:
        raise ValueError(f"Gross irrigated area row sum mismatch in {filepath}")

    rows = []
    for _, row in sub.iterrows():
        raw_dist = str(row.iloc[1]).strip()
        zone_info = resolve_district_classification(raw_dist)

        net_canal_govt = float(row.iloc[2])
        net_canal_priv = float(row.iloc[3])
        net_canal_tot = float(row.iloc[4])
        net_tank = float(row.iloc[5])
        net_tw = float(row.iloc[6])
        net_other_well = float(row.iloc[7])
        net_well_tot = float(row.iloc[8])
        net_other_src = float(row.iloc[9])
        net_tot = float(row.iloc[10])

        gross_canal_govt = float(row.iloc[11])
        gross_canal_priv = float(row.iloc[12])
        gross_canal_tot = float(row.iloc[13])
        gross_tank = float(row.iloc[14])
        gross_tw = float(row.iloc[15])
        gross_other_well = float(row.iloc[16])
        gross_well_tot = float(row.iloc[17])
        gross_other_src = float(row.iloc[18])
        gross_tot = float(row.iloc[19])

        tw_share_pct = round((net_tw / net_tot) * 100, 2) if net_tot > 0 else 0.0
        canal_share_pct = round((net_canal_tot / net_tot) * 100, 2) if net_tot > 0 else 0.0
        intensity_pct = round((gross_tot / net_tot) * 100, 2) if net_tot > 0 else 0.0

        anomaly_flag = ""
        if zone_info["district_nabard"] == "Kapurthala" and crop_year == "2024-25":
            anomaly_flag = "provisional_net_area_drop_865pct_intensity"
        elif zone_info["district_nabard"] == "Sri Muktsar Sahib" and year_start >= 2022:
            anomaly_flag = "source_reclassified_canal_to_tubewell_from_2022_23"

        rows.append(
            {
                "district_nabard": zone_info["district_nabard"],
                "nabard_az_code": zone_info["nabard_az_code"],
                "nabard_az_name": zone_info["nabard_az_name"],
                "raw_district": raw_dist,
                "crop_year": crop_year,
                "year_start": year_start,
                "net_canal_govt_ha": net_canal_govt,
                "net_canal_private_ha": net_canal_priv,
                "net_canal_total_ha": net_canal_tot,
                "net_tank_ha": net_tank,
                "net_tubewell_ha": net_tw,
                "net_other_well_ha": net_other_well,
                "net_well_total_ha": net_well_tot,
                "net_other_source_ha": net_other_src,
                "net_irrigated_total_ha": net_tot,
                "net_irrigated_total_ekad": round(net_tot * HA_TO_EKAD, 2),
                "gross_canal_govt_ha": gross_canal_govt,
                "gross_canal_private_ha": gross_canal_priv,
                "gross_canal_total_ha": gross_canal_tot,
                "gross_tank_ha": gross_tank,
                "gross_tubewell_ha": gross_tw,
                "gross_other_well_ha": gross_other_well,
                "gross_well_total_ha": gross_well_tot,
                "gross_other_source_ha": gross_other_src,
                "gross_irrigated_total_ha": gross_tot,
                "gross_irrigated_total_ekad": round(gross_tot * HA_TO_EKAD, 2),
                "tubewell_share_net_pct": tw_share_pct,
                "canal_share_net_pct": canal_share_pct,
                "irrigation_intensity_pct": intensity_pct,
                "portal_anomaly_flag": anomaly_flag,
                "source_file": filepath.name,
            }
        )

    return pd.DataFrame(rows)


def build_irrigation_panel(input_files: Iterable[Path], out_dir: Path) -> pd.DataFrame:
    frames: List[pd.DataFrame] = [parse_single_irrigation_html(Path(f)) for f in input_files]
    panel = (
        pd.concat(frames, ignore_index=True)
        .drop_duplicates(subset=["district_nabard", "crop_year"])
        .sort_values(["year_start", "district_nabard"])
        .reset_index(drop=True)
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    panel_path = out_dir / "punjab_district_irrigation_2020_2025.csv"
    panel.to_csv(panel_path, index=False)

    latest_yr = panel["crop_year"].max()
    latest_df = panel[panel["crop_year"] == latest_yr].reset_index(drop=True)
    latest_path = out_dir / f"punjab_district_irrigation_{latest_yr.replace('-', '_')}.csv"
    latest_df.to_csv(latest_path, index=False)
    return panel


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse Punjab source-wise irrigation HTML reports.")
    parser.add_argument("--raw-dir", type=Path, default=Path("data/raw"))
    parser.add_argument("--out-dir", type=Path, default=Path("data/processed"))
    args = parser.parse_args()

    files = sorted(args.raw_dir.glob("source_irrigated_area_report*.xls"))
    if not files:
        raise FileNotFoundError(f"No source_irrigated_area_report*.xls files found in {args.raw_dir}")
    df_out = build_irrigation_panel(files, args.out_dir)
    print(f"Saved {len(df_out)} irrigation records across {df_out['crop_year'].nunique()} years.")
