import argparse
import re
from pathlib import Path

import pandas as pd

from etl.district_zones import resolve_district_classification

HA_TO_EKAD = 2.47105
COTTON_BALE_KG = 170.0

DISTRICT_BIFURCATION_NOTES = {
    "S.A.S Nagar": "Carved out of Rupnagar and Patiala in 2006 (series begins 2006-07)",
    "Tarn Taran": "Carved out of Amritsar in 2006 (series begins 2006-07)",
    "Barnala": "Carved out of Sangrur in 2006 (series begins 2007-08)",
    "Fazilka": "Carved out of Ferozepur in 2011 (series begins 2011-12)",
    "Pathankot": "Carved out of Gurdaspur in 2011 (series begins 2011-12)",
    "Malerkotla": "Carved out of Sangrur in 2021 (series begins 2021-22)",
}

CANONICAL_CROP_NAMES = {
    "Rapeseed &Mustard": "Rapeseed & Mustard",
    "other oilseeds": "Other Oilseeds",
}

WHOLE_YEAR_SEASON_MAP = {
    ("Cotton(lint)", "Whole Year"): "Kharif",
    ("Moong(Green Gram)", "Whole Year"): "Kharif",
    ("Guar seed", "Whole Year"): "Kharif",
}


def parse_des_crop_html(filepath: Path, out_dir: Path) -> pd.DataFrame:
    tables = pd.read_html(filepath)
    if not tables:
        raise ValueError(f"No HTML tables found in {filepath}")
    raw = tables[0]

    states = raw.iloc[:, 0].astype(str).str.replace(r"^\d+\.\s*", "", regex=True).str.strip()
    if not (states == "Punjab").all():
        raise ValueError("Expected all rows in DES report to belong to Punjab.")

    raw_districts = raw.iloc[:, 1].astype(str).str.replace(r"^\d+\.\s*", "", regex=True).str.strip()
    raw_years = raw.iloc[:, 2].astype(str).str.strip()

    year_starts = raw_years.str.extract(r"^(19\d{2}|20\d{2})")[0].astype(int)
    crop_years = year_starts.astype(str) + "-" + (year_starts + 1).astype(str).str[-2:]

    district_meta = {
        d: resolve_district_classification(d) for d in raw_districts.unique()
    }

    records = []
    for col_idx in range(3, raw.shape[1], 3):
        crop_raw, season_raw, _ = raw.columns[col_idx]
        _, _, prod_hdr = raw.columns[col_idx + 1]
        _, _, yld_hdr = raw.columns[col_idx + 2]

        crop_clean = CANONICAL_CROP_NAMES.get(str(crop_raw).strip(), str(crop_raw).strip())
        season_clean = str(season_raw).strip()
        season_canonical = WHOLE_YEAR_SEASON_MAP.get((crop_clean, season_clean), season_clean)

        area = pd.to_numeric(raw.iloc[:, col_idx], errors="coerce")
        prod = pd.to_numeric(raw.iloc[:, col_idx + 1], errors="coerce")
        yld = pd.to_numeric(raw.iloc[:, col_idx + 2], errors="coerce")

        valid_mask = area.notna() | prod.notna() | yld.notna()
        if not valid_mask.any():
            continue

        is_bales = "Bales" in str(prod_hdr)
        prod_unit = "Bales" if is_bales else "Tonnes"
        yld_unit = "Bales/Hectare" if is_bales else "Tonne/Hectare"

        for idx in raw.index[valid_mask]:
            r_dist = raw_districts.iat[idx]
            z = district_meta[r_dist]
            c_dist = z["district_nabard"]

            a_val = float(area.iat[idx]) if pd.notna(area.iat[idx]) else None
            p_val = float(prod.iat[idx]) if pd.notna(prod.iat[idx]) else None
            y_val = float(yld.iat[idx]) if pd.notna(yld.iat[idx]) else None

            if y_val is not None:
                if is_bales:
                    yld_quintal_ekad = round(((y_val * COTTON_BALE_KG) / 100.0) / HA_TO_EKAD, 2)
                else:
                    yld_quintal_ekad = round((y_val * 10.0) / HA_TO_EKAD, 2)
            else:
                yld_quintal_ekad = None

            q_flag = ""
            if a_val is not None and a_val > 0 and p_val == 0.0:
                q_flag = "zero_production_rounded_small_area"
            elif season_clean != season_canonical:
                q_flag = "whole_year_mapped_to_kharif"

            records.append(
                {
                    "district_nabard": c_dist,
                    "nabard_az_code": z["nabard_az_code"],
                    "nabard_az_name": z["nabard_az_name"],
                    "raw_district": r_dist,
                    "crop_year": crop_years.iat[idx],
                    "year_start": int(year_starts.iat[idx]),
                    "crop": crop_clean,
                    "season_canonical": season_canonical,
                    "season_raw": season_clean,
                    "area_ha": a_val,
                    "area_ekad": round(a_val * HA_TO_EKAD, 2) if a_val is not None else None,
                    "production": p_val,
                    "production_unit": prod_unit,
                    "yield_per_ha": y_val,
                    "yield_unit": yld_unit,
                    "yield_quintal_per_ekad": yld_quintal_ekad,
                    "data_quality_flag": q_flag,
                    "district_lineage_note": DISTRICT_BIFURCATION_NOTES.get(c_dist, ""),
                }
            )

    df_long = (
        pd.DataFrame(records)
        .sort_values(["district_nabard", "year_start", "crop", "season_canonical"])
        .reset_index(drop=True)
    )

    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / "des_punjab_crop_yield_1997_2023.csv"
    df_long.to_csv(out_path, index=False)
    return df_long


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Parse DES Punjab historical crop HTML report.")
    parser.add_argument(
        "--input-file",
        type=Path,
        default=Path("data/raw/horizontal_crop_vertical_year_report (1).xls"),
    )
    parser.add_argument("--out-dir", type=Path, default=Path("data/processed"))
    args = parser.parse_args()

    df_out = parse_des_crop_html(args.input_file, args.out_dir)
    print(f"Saved {len(df_out)} tidy DES crop records ({df_out['crop'].nunique()} crops).")
