import numpy as np

from floodlab.evaluation import adjusted_r2, regression_metrics


def test_regression_metrics_known_values():
    y = np.array([1.0, 2.0, 3.0])
    pred = np.array([1.0, 2.0, 4.0])
    result = regression_metrics(y, pred, p=1)
    assert np.isclose(result["mae"], 1 / 3)
    assert np.isclose(result["mse"], 1 / 3)
    assert np.isclose(result["rmse"], np.sqrt(1 / 3))
    assert np.isclose(result["r2"], 0.5)


def test_adjusted_r2_guard_and_formula():
    assert adjusted_r2(0.8, 3, 2) is None
    assert np.isclose(adjusted_r2(0.8, 100, 5), 1 - 0.2 * 99 / 94)
