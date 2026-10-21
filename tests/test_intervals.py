import json
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]


def test_ols_prediction_interval_is_sane():
    results = json.loads((ROOT / "web" / "data" / "model_results.json").read_text(encoding="utf-8"))
    diagnostics = results["ols_diagnostics"]
    assert 0.90 <= diagnostics["pi_coverage"] <= 0.99
    assert diagnostics["pi_mean_width"] > 0


def test_regularized_models_do_not_claim_ols_intervals():
    results = json.loads((ROOT / "web" / "data" / "model_results.json").read_text(encoding="utf-8"))
    for model in results["models"]:
        if model["family"] in {"ridge", "lasso"}:
            assert model["interval_method"] == "unavailable"
