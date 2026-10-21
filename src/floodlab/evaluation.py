from __future__ import annotations

import math

import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


def adjusted_r2(r2: float, n: int, p: int) -> float | None:
    if n <= p + 1:
        return None
    return 1.0 - (1.0 - r2) * (n - 1) / (n - p - 1)


def regression_metrics(y_true, y_pred, p: int) -> dict[str, float | None]:
    mse = float(mean_squared_error(y_true, y_pred))
    r2 = float(r2_score(y_true, y_pred))
    return {
        "mae": float(mean_absolute_error(y_true, y_pred)),
        "mse": mse,
        "rmse": math.sqrt(mse),
        "r2": r2,
        "adjusted_r2": adjusted_r2(r2, len(y_true), p),
    }


def to_native(value):
    if value is None:
        return None
    if isinstance(value, (np.integer,)):
        return int(value)
    if isinstance(value, (np.floating,)):
        return None if not np.isfinite(value) else float(value)
    if isinstance(value, np.ndarray):
        return [to_native(v) for v in value.tolist()]
    if isinstance(value, dict):
        return {str(k): to_native(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [to_native(v) for v in value]
    return value
