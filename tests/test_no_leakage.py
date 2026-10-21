from sklearn.pipeline import Pipeline

from floodlab.modeling import build_candidates


def test_all_candidates_are_pipelines():
    assert all(isinstance(candidate.pipeline, Pipeline) for candidate in build_candidates())


def test_scaler_and_selector_are_inside_pipeline():
    candidates = build_candidates()
    ridge = next(c for c in candidates if c.family == "ridge")
    select = next(c for c in candidates if c.family == "selectkbest")
    assert "scaler" in ridge.pipeline.named_steps
    assert "selector" in select.pipeline.named_steps
