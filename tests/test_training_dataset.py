from pathlib import Path
import pandas as pd
import pytest

from etl.build_training_dataset import build_master_training_panel


DES_PATH = Path("data/processed/des_punjab_crop_yield_1997_2023.csv")
IRR_PATH = Path("data/processed/punjab_district_irrigation_2020_2025.csv")
PAU_PATH = Path("data/pau_benchmarks.json")


@pytest.mark.skipif(
    not (DES_PATH.exists() and IRR_PATH.exists() and PAU_PATH.exists()),
    reason="Processed datasets not present yet",
)
def test_master_panel_integrity(tmp_path: Path) -> None:
    panel, pau_summary = build_master_training_panel(
        des_csv_path=DES_PATH,
        irr_csv_path=IRR_PATH,
        pau_json_path=PAU_PATH,
        out_dir=tmp_path,
    )

    des_raw = pd.read_csv(DES_PATH)
    # Row count must match DES source exactly (no cartesian duplicate rows)
    assert len(panel) == len(des_raw)

    # Pre-2020 rows must NEVER have fabricated yearly irrigation values
    pre_2020 = panel[panel["year_start"] < 2020]
    assert pre_2020["tubewell_share_net_pct"].isna().all()

    # Overlapping years (2020-21 to 2022-23) must have populated yearly irrigation
    overlap = panel[panel["year_start"] >= 2020]
    assert overlap["tubewell_share_net_pct"].notna().any()

    # Kapurthala structural baseline must fall back to 2023-24 due to 2024-25 portal anomaly
    kap = panel[panel["district_nabard"] == "Kapurthala"].iloc[0]
    assert kap["baseline_irrigation_year"] == "2023-24"
    assert bool(kap["baseline_irrigation_anomaly_fallback"]) is True
    assert set(pau_summary["pau_crop_group"]) == {"Basmati", "Paddy", "Wheat", "Potato", "Summer_Moong"}

    
