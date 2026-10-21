from pathlib import Path

import pandas as pd
import pytest

from floodlab.data import FEATURES, ID_COLUMN, TARGET

ROOT = Path(__file__).resolve().parents[1]


def test_csv_headers_match_contract():
    raw = ROOT / "data" / "raw"
    if not (raw / "train.csv").exists():
        pytest.skip("Kaggle raw data is intentionally not stored in Git")
    assert list(pd.read_csv(raw / "train.csv", nrows=3).columns) == [ID_COLUMN, *FEATURES, TARGET]
    assert list(pd.read_csv(raw / "test.csv", nrows=3).columns) == [ID_COLUMN, *FEATURES]
    assert list(pd.read_csv(raw / "sample_submission.csv", nrows=3).columns) == [ID_COLUMN, TARGET]


def test_expected_feature_count_and_no_id_leakage():
    assert len(FEATURES) == 20
    assert ID_COLUMN not in FEATURES
    assert TARGET not in FEATURES
