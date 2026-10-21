from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.outliers_influence import variance_inflation_factor
from statsmodels.stats.stattools import durbin_watson, jarque_bera

from .data import FEATURES, ID_COLUMN, TARGET, load_competition_data, split_labeled_data
from .evaluation import regression_metrics, to_native
from .modeling import build_candidates, evaluate_candidates, linear_parameters, selected_features

SEED = 42
CV_SAMPLE_SIZE = 200_000


def _savefig(path: Path):
    plt.tight_layout()
    plt.savefig(path, dpi=150, bbox_inches="tight")
    plt.close()


def run(root: Path) -> dict:
    raw_dir = root / "data" / "raw"
    out = root / "outputs"
    fig_dir, table_dir, model_dir = out / "figures", out / "tables", out / "models"
    web_data = root / "web" / "data"
    for directory in (fig_dir, table_dir, model_dir, web_data):
        directory.mkdir(parents=True, exist_ok=True)

    print("Loading Kaggle data...", flush=True)
    train, competition_test, submission = load_competition_data(raw_dir)
    x_train, x_val, x_test, y_train, y_val, y_test = split_labeled_data(train, SEED)
    cv_n = min(CV_SAMPLE_SIZE, len(x_train))
    sample_idx = x_train.sample(n=cv_n, random_state=SEED).index
    x_cv, y_cv = x_train.loc[sample_idx], y_train.loc[sample_idx]

    print("Generating EDA...", flush=True)
    summary = train[[*FEATURES, TARGET]].describe().T
    summary["missing"] = train[[*FEATURES, TARGET]].isna().sum()
    summary.to_csv(table_dir / "data_summary.csv")
    corr = train[[*FEATURES, TARGET]].corr()
    corr.to_csv(table_dir / "correlation_matrix.csv")
    target_corr = corr[TARGET].drop(TARGET).sort_values(key=np.abs, ascending=False)
    target_corr.rename("correlation").to_csv(table_dir / "feature_target_correlations.csv")

    sns.set_theme(style="whitegrid")
    plt.figure(figsize=(8, 5)); sns.histplot(train[TARGET], bins=50, kde=True, color="#14b8a6")
    plt.title("FloodProbability Distribution"); _savefig(fig_dir / "target_distribution.png")
    plt.figure(figsize=(13, 10)); sns.heatmap(corr, cmap="vlag", center=0, square=True, cbar_kws={"shrink": .75})
    plt.title("Feature Correlation Matrix"); _savefig(fig_dir / "correlation_heatmap.png")
    plt.figure(figsize=(9, 7)); target_corr.sort_values().plot.barh(color="#0ea5e9")
    plt.title("Feature Correlation with FloodProbability"); plt.xlabel("Pearson correlation")
    _savefig(fig_dir / "feature_target_correlations.png")

    print(f"Evaluating candidates with 5-fold CV on {cv_n:,} training-only rows...", flush=True)
    results, fitted = evaluate_candidates(build_candidates(), x_cv, y_cv, x_val, y_val, SEED)
    results.to_csv(table_dir / "model_comparison.csv", index=False)
    results.to_csv(table_dir / "selection_runs.csv", index=False)
    best_row = results.iloc[0]
    best_id = str(best_row["model_id"])
    print(f"Selected by CV RMSE: {best_id}", flush=True)

    # Freeze the selected candidate, then fit once on the full 80% development set.
    final_model = fitted[best_id]
    x_dev = pd.concat([x_train, x_val]).sort_index()
    y_dev = pd.concat([y_train, y_val]).sort_index()
    final_model.fit(x_dev, y_dev)
    y_pred = final_model.predict(x_test)
    final_features = selected_features(final_model) if best_row["family"] != "baseline" else []
    test_metrics = regression_metrics(y_test, y_pred, max(1, len(final_features)))
    joblib.dump(final_model, model_dir / "recommended_model.joblib")

    params = linear_parameters(final_model)
    coef_df = pd.DataFrame({"feature": params["feature_order"], "coefficient": params["coefficients"]})
    coef_df["abs_coefficient"] = coef_df["coefficient"].abs()
    coef_df.sort_values("abs_coefficient", ascending=False).to_csv(table_dir / "coefficients.csv", index=False)

    # Statsmodels OLS is the inferential companion. If selection chooses a regularized model,
    # intervals remain explicitly tied to the all-feature OLS model.
    ols_features = FEATURES
    ols_sm = sm.OLS(y_dev.to_numpy(), sm.add_constant(x_dev[ols_features].to_numpy())).fit()
    ols_pred = ols_sm.get_prediction(sm.add_constant(x_test[ols_features].to_numpy())).summary_frame(alpha=0.05)
    ols_test_pred = np.asarray(ols_pred["mean"])
    ols_test_metrics = regression_metrics(y_test, ols_test_pred, len(ols_features))
    pi_coverage = float(np.mean((y_test.to_numpy() >= ols_pred["obs_ci_lower"].to_numpy()) & (y_test.to_numpy() <= ols_pred["obs_ci_upper"].to_numpy())))
    pi_mean_width = float(np.mean(ols_pred["obs_ci_upper"] - ols_pred["obs_ci_lower"]))
    residuals = y_test.to_numpy() - ols_test_pred

    exog_dev = sm.add_constant(x_dev[ols_features].to_numpy())
    vif = pd.DataFrame({
        "feature": ["const", *ols_features],
        "vif": [variance_inflation_factor(exog_dev, i) for i in range(exog_dev.shape[1])],
    })
    vif.to_csv(table_dir / "vif.csv", index=False)
    bp = het_breuschpagan(residuals, sm.add_constant(x_test[ols_features].to_numpy()))
    jb = jarque_bera(residuals)
    diagnostics = {
        "durbin_watson": float(durbin_watson(residuals)),
        "breusch_pagan_lm": float(bp[0]), "breusch_pagan_pvalue": float(bp[1]),
        "jarque_bera": float(jb[0]), "jarque_bera_pvalue": float(jb[1]),
        "residual_skew": float(stats.skew(residuals)),
        "residual_kurtosis": float(stats.kurtosis(residuals, fisher=True)),
        "max_feature_vif": float(vif.loc[vif.feature != "const", "vif"].max()),
        "pi_coverage": pi_coverage, "pi_mean_width": pi_mean_width,
        "interpretation_note": "Large-sample p-values can flag small deviations; inspect plots and effect size.",
    }
    pd.DataFrame([diagnostics]).to_csv(table_dir / "diagnostics.csv", index=False)

    comparison_plot = results.groupby("family", as_index=False).first().sort_values("validation_rmse")
    plt.figure(figsize=(9, 5)); sns.barplot(data=comparison_plot, x="validation_rmse", y="display_name", color="#14b8a6")
    plt.title("Best Validation RMSE by Model Family"); _savefig(fig_dir / "model_comparison.png")
    selection_plot = results[results.family.isin(["selectkbest", "rfe"])].sort_values(["family", "feature_count"])
    plt.figure(figsize=(9, 5)); sns.lineplot(data=selection_plot, x="feature_count", y="cv_rmse_mean", hue="family", marker="o")
    plt.title("Feature Count vs 5-fold CV RMSE"); _savefig(fig_dir / "cv_feature_count.png")
    coef_plot = coef_df.sort_values("coefficient")
    plt.figure(figsize=(9, 7)); plt.barh(coef_plot.feature, coef_plot.coefficient, color=np.where(coef_plot.coefficient >= 0, "#14b8a6", "#f97316"))
    plt.title("Recommended Model Coefficients"); _savefig(fig_dir / "coefficients.png")

    plot_n = 500
    order = np.argsort(ols_test_pred)[:]
    chosen = order[np.linspace(0, len(order) - 1, plot_n, dtype=int)]
    plot_df = pd.DataFrame({
        "predicted": ols_test_pred[chosen], "actual": y_test.to_numpy()[chosen],
        "ci_low": ols_pred["mean_ci_lower"].to_numpy()[chosen], "ci_high": ols_pred["mean_ci_upper"].to_numpy()[chosen],
        "pi_low": ols_pred["obs_ci_lower"].to_numpy()[chosen], "pi_high": ols_pred["obs_ci_upper"].to_numpy()[chosen],
    }).sort_values("predicted")
    plt.figure(figsize=(10, 6)); x_axis=np.arange(len(plot_df))
    plt.fill_between(x_axis, plot_df.pi_low, plot_df.pi_high, alpha=.18, color="#0ea5e9", label="95% prediction interval")
    plt.fill_between(x_axis, plot_df.ci_low, plot_df.ci_high, alpha=.35, color="#14b8a6", label="95% mean CI")
    plt.scatter(x_axis, plot_df.actual, s=7, alpha=.35, color="#334155", label="actual")
    plt.plot(x_axis, plot_df.predicted, color="#0f766e", lw=1.5, label="OLS prediction")
    plt.title("OLS Predictions with 95% Confidence and Prediction Intervals"); plt.legend()
    _savefig(fig_dir / "ols_prediction_intervals.png")
    plt.figure(figsize=(8, 5)); plt.scatter(ols_test_pred[::50], residuals[::50], s=8, alpha=.25, color="#0ea5e9"); plt.axhline(0, color="#ef4444")
    plt.xlabel("Predicted"); plt.ylabel("Residual"); plt.title("Residuals vs Predicted")
    _savefig(fig_dir / "residuals_vs_predicted.png")
    sm.qqplot(residuals[::10], line="45", fit=True); plt.title("Residual Q-Q Plot")
    _savefig(fig_dir / "residual_qq.png")

    # Compact web payloads — no million-row CSV shipped to the browser.
    feature_stats = {}
    for f in FEATURES:
        s = train[f]
        feature_stats[f] = {"min": float(s.min()), "q1": float(s.quantile(.25)), "median": float(s.median()), "q3": float(s.quantile(.75)), "max": float(s.max()), "mean": float(s.mean())}
    hist_counts, hist_edges = np.histogram(train[TARGET], bins=40)
    eda_payload = {
        "schema_version": "1.0", "rows": len(train), "feature_count": 20,
        "missing_total": int(train.isna().sum().sum()), "duplicate_ids": int(train[ID_COLUMN].duplicated().sum()),
        "target": {"name": TARGET, "min": float(train[TARGET].min()), "max": float(train[TARGET].max()), "mean": float(train[TARGET].mean()), "hist_counts": hist_counts.tolist(), "hist_edges": hist_edges.tolist()},
        "feature_schema": feature_stats,
        "feature_target_correlations": [{"feature": k, "correlation": float(v)} for k, v in target_corr.items()],
        "correlation_matrix": {"labels": [*FEATURES, TARGET], "values": corr.to_numpy().round(6).tolist()},
    }
    (web_data / "eda.json").write_text(json.dumps(to_native(eda_payload), ensure_ascii=False), encoding="utf-8")

    representative = results.groupby("family", as_index=False).first().sort_values("validation_rmse")
    model_list = []
    for _, row in representative.iterrows():
        model = fitted[row.model_id]
        lp = linear_parameters(model) if row.family != "baseline" else {"feature_order": [], "coefficients": [], "intercept": float(np.ravel(model.named_steps["model"].constant_)[0]), "scaler": None}
        model_list.append({
            "id": row.model_id, "display_name": row.display_name, "family": row.family,
            **lp,
            "cv_metrics": {"rmse": row.cv_rmse_mean, "rmse_std": row.cv_rmse_std, "r2": row.cv_r2_mean, "mae": row.cv_mae_mean},
            "validation_metrics": {k.removeprefix("validation_"): row[k] for k in row.index if k.startswith("validation_")},
            "test_metrics": test_metrics if row.model_id == best_id else None,
            "diagnostics": diagnostics if row.family == "ols" else None,
            "interval_method": "statsmodels OLS analytical" if row.family == "ols" else "unavailable",
        })
    model_payload = {
        "schema_version": "1.0", "dataset": "Kaggle Playground Series S4E5 — Predict the Flood", "seed": SEED,
        "splits": {"train": len(x_train), "validation": len(x_val), "test": len(x_test), "cv_sample": cv_n, "cv_folds": 5},
        "models": model_list,
        "selection_runs": results[["model_id", "display_name", "family", "feature_count", "cv_rmse_mean", "cv_r2_mean", "validation_rmse", "validation_r2", "features"]].to_dict("records"),
        "recommended_model_id": best_id,
        "recommended_test_metrics": test_metrics,
        "ols_test_metrics": ols_test_metrics,
        "ols_diagnostics": diagnostics,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "limitations": ["Competition target is not a real-world flood warning probability.", "Associations and coefficients are not causal effects.", "Candidate selection used a fixed 200,000-row training-only sample for computational efficiency.", "Only the frozen recommended model was evaluated on the final holdout test set."],
    }
    (web_data / "model_results.json").write_text(json.dumps(to_native(model_payload), ensure_ascii=False), encoding="utf-8")

    sample = x_test.sample(n=12, random_state=SEED)
    sample_pred = final_model.predict(sample)
    samples_payload = [{"features": {k: float(v) for k, v in row.items()}, "prediction": float(pred)} for (_, row), pred in zip(sample.iterrows(), sample_pred)]
    (web_data / "prediction_samples.json").write_text(json.dumps(samples_payload, ensure_ascii=False), encoding="utf-8")

    metadata = {
        "seed": SEED, "cv_sample_size": cv_n, "recommended_model_id": best_id,
        "recommended_test_metrics": test_metrics, "ols_test_metrics": ols_test_metrics,
        "ols_interval": {"coverage": pi_coverage, "mean_width": pi_mean_width},
        "train_rows": len(train), "competition_test_rows": len(competition_test),
    }
    (out / "run_metadata.json").write_text(json.dumps(to_native(metadata), indent=2), encoding="utf-8")
    print(json.dumps(to_native(metadata), indent=2), flush=True)
    return metadata
