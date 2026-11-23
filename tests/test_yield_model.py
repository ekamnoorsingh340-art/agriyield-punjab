from pathlib import Path
import pandas as pd
import pytest

from ml.train_yield_model import (
    CATEGORICAL_FEATURES,
    NUMERIC_FEATURES,
    train_and_evaluate,
)


MASTER_CSV = Path("data/processed/agriyield_punjab_master_panel.csv")


@pytest.mark.skipif(not MASTER_CSV.exists(), reason="Master panel CSV not built yet")
def test_yield_model_training_and_prediction(tmp_path: Path) -> None:
    pipeline, metrics = train_and_evaluate(
        master_csv_path=MASTER_CSV,
        models_dir=tmp_path,
        holdout_year_start=2020,
    )

    # Verify artifacts were saved
    assert (tmp_path / "agriyield_punjab_model.joblib").exists()
    assert (tmp_path / "model_metrics.json").exists()
    assert (tmp_path / "inference_lookup.json").exists()

    # Temporal out-of-sample R2 should be strongly positive (> 0.85)
    assert metrics["temporal_holdout_r2"] > 0.85
    assert metrics["temporal_holdout_rmse_q_ekad"] > 0

    # Verify single-row inference for Wheat in Bathinda
    sample = pd.DataFrame(
        [
            {
                "district_nabard": "Bathinda",
                "nabard_az_code": "AZ13",
                "crop": "Wheat",
                "season_canonical": "Rabi",
                "year_start": 2024,
                "area_ekad": 600000.0,
                "baseline_tubewell_share_pct": 45.0,
                "baseline_canal_share_pct": 55.0,
                "baseline_irrigation_intensity_pct": 185.0,
                "yield_q_ekad_lag1": 21.5,
                "yield_q_ekad_roll3_mean": 21.0,
            }
        ]
    )[CATEGORICAL_FEATURES + NUMERIC_FEATURES]

    pred = float(pipeline.predict(sample)[0])
    assert 12.0 <= pred <= 32.0
