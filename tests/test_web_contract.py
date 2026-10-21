import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def test_required_web_files_and_json_contract():
    web = ROOT / "web"
    for relative in ["index.html", "style.css", "app.js", "data/model_results.json", "data/eda.json", "data/prediction_samples.json", "assets/chart.min.js"]:
        assert (web / relative).is_file(), relative
    results = json.loads((web / "data" / "model_results.json").read_text(encoding="utf-8"))
    assert results["schema_version"] == "1.0"
    assert results["recommended_model_id"]
    assert len(results["selection_runs"]) == 35


def test_all_local_web_references_exist():
    html = (ROOT / "web" / "index.html").read_text(encoding="utf-8")
    required = ["style.css", "app.js", "assets/chart.min.js", "data/model_comparison.csv", "data/diagnostics.csv"]
    for ref in required:
        assert ref in html
        assert (ROOT / "web" / ref).is_file(), ref
