import json
from pathlib import Path

import joblib
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def test_exported_coefficients_match_python_model():
    results = json.loads((ROOT / "web" / "data" / "model_results.json").read_text(encoding="utf-8"))
    samples = json.loads((ROOT / "web" / "data" / "prediction_samples.json").read_text(encoding="utf-8"))
    exported = next(m for m in results["models"] if m["id"] == results["recommended_model_id"])
    model = joblib.load(ROOT / "outputs" / "models" / "recommended_model.joblib")
    frame = pd.DataFrame([sample["features"] for sample in samples])[exported["feature_order"]]
    python_pred = model.predict(frame)
    js_equivalent = exported["intercept"] + frame.to_numpy() @ np.asarray(exported["coefficients"])
    assert np.max(np.abs(python_pred - js_equivalent)) < 1e-8
    assert np.max(np.abs(python_pred - np.asarray([s["prediction"] for s in samples]))) < 1e-12
