from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.dummy import DummyRegressor
from sklearn.feature_selection import RFE, SelectKBest, f_regression
from sklearn.impute import SimpleImputer
from sklearn.linear_model import Lasso, LinearRegression, Ridge
from sklearn.model_selection import KFold, cross_validate
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

from .data import FEATURES


@dataclass(frozen=True)
class Candidate:
    model_id: str
    display_name: str
    family: str
    pipeline: Pipeline
    feature_count: int
    parameter: float | int | None = None


def build_candidates() -> list[Candidate]:
    candidates = [
        Candidate("dummy_mean", "Dummy Mean", "baseline", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", DummyRegressor(strategy="mean")),
        ]), 0),
        Candidate("ols_all", "OLS — All 20", "ols", Pipeline([
            ("imputer", SimpleImputer(strategy="median")),
            ("model", LinearRegression()),
        ]), 20),
    ]
    for k in range(1, 21):
        candidates.append(Candidate(
            f"selectkbest_{k}", f"SelectKBest + OLS (k={k})", "selectkbest",
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("selector", SelectKBest(score_func=f_regression, k=k)),
                ("model", LinearRegression()),
            ]), k, k,
        ))
    for k in (5, 10, 15, 20):
        candidates.append(Candidate(
            f"rfe_{k}", f"RFE + OLS (k={k})", "rfe",
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("selector", RFE(LinearRegression(), n_features_to_select=k, step=2)),
                ("model", LinearRegression()),
            ]), k, k,
        ))
    for alpha in (0.01, 0.1, 1.0, 10.0, 100.0):
        label = str(alpha).replace(".", "p")
        candidates.append(Candidate(
            f"ridge_{label}", f"Ridge (alpha={alpha:g})", "ridge",
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("model", Ridge(alpha=alpha)),
            ]), 20, alpha,
        ))
    for alpha in (0.0001, 0.001, 0.005, 0.01):
        label = str(alpha).replace(".", "p")
        candidates.append(Candidate(
            f"lasso_{label}", f"Lasso (alpha={alpha:g})", "lasso",
            Pipeline([
                ("imputer", SimpleImputer(strategy="median")),
                ("scaler", StandardScaler()),
                ("model", Lasso(alpha=alpha, max_iter=5000, tol=1e-6)),
            ]), 20, alpha,
        ))
    return candidates


def selected_features(pipeline: Pipeline) -> list[str]:
    selector = pipeline.named_steps.get("selector")
    if selector is None:
        return FEATURES.copy()
    return [name for name, keep in zip(FEATURES, selector.get_support()) if keep]


def evaluate_candidates(candidates, x_train, y_train, x_val, y_val, seed=42):
    cv = KFold(n_splits=5, shuffle=True, random_state=seed)
    scoring = {"rmse": "neg_root_mean_squared_error", "r2": "r2", "mae": "neg_mean_absolute_error"}
    rows, fitted = [], {}
    for idx, candidate in enumerate(candidates, start=1):
        print(f"[{idx:02d}/{len(candidates):02d}] {candidate.display_name}", flush=True)
        cv_result = cross_validate(candidate.pipeline, x_train, y_train, cv=cv, scoring=scoring, n_jobs=-1)
        candidate.pipeline.fit(x_train, y_train)
        pred = candidate.pipeline.predict(x_val)
        from .evaluation import regression_metrics
        feats = selected_features(candidate.pipeline) if candidate.family != "baseline" else []
        metrics = regression_metrics(y_val, pred, max(1, len(feats)))
        row = {
            "model_id": candidate.model_id,
            "display_name": candidate.display_name,
            "family": candidate.family,
            "parameter": candidate.parameter,
            "feature_count": len(feats),
            "features": "|".join(feats),
            "cv_rmse_mean": float(-cv_result["test_rmse"].mean()),
            "cv_rmse_std": float(cv_result["test_rmse"].std()),
            "cv_r2_mean": float(cv_result["test_r2"].mean()),
            "cv_mae_mean": float(-cv_result["test_mae"].mean()),
            **{f"validation_{k}": v for k, v in metrics.items()},
        }
        rows.append(row)
        fitted[candidate.model_id] = candidate.pipeline
    results = pd.DataFrame(rows).sort_values(["cv_rmse_mean", "feature_count"], kind="stable")
    return results, fitted


def linear_parameters(pipeline: Pipeline) -> dict:
    model = pipeline.named_steps["model"]
    feats = selected_features(pipeline)
    scaler = pipeline.named_steps.get("scaler")
    coefficients = np.asarray(model.coef_, dtype=float)
    intercept = float(model.intercept_)
    if scaler is None:
        return {"feature_order": feats, "coefficients": coefficients.tolist(), "intercept": intercept, "scaler": None}
    means = np.asarray(scaler.mean_, dtype=float)
    scales = np.asarray(scaler.scale_, dtype=float)
    raw_coef = coefficients / scales
    raw_intercept = intercept - float(np.dot(coefficients, means / scales))
    return {
        "feature_order": feats,
        "coefficients": raw_coef.tolist(),
        "intercept": raw_intercept,
        "scaler": {"mean": means.tolist(), "scale": scales.tolist()},
    }
