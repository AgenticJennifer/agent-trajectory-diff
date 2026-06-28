from pathlib import Path

from trajdiff.loader import load_jsonl
from trajdiff.differ import diff_traces, diff_case

FIXTURES = Path(__file__).parent / "fixtures"


def _load():
    baseline = load_jsonl(FIXTURES / "baseline.jsonl")
    candidate = load_jsonl(FIXTURES / "candidate.jsonl")
    return baseline, candidate


def test_regression_detected():
    baseline, candidate = _load()
    result = diff_traces(baseline, candidate)
    regression_ids = [d["case_id"] for d in result["regressions"]]
    assert "route_planner_01" in regression_ids


def test_improvement_detected():
    baseline, candidate = _load()
    result = diff_traces(baseline, candidate)
    improvement_ids = [d["case_id"] for d in result["improvements"]]
    assert "eta_estimate_03" in improvement_ids


def test_unchanged_case_not_flagged():
    baseline, candidate = _load()
    result = diff_traces(baseline, candidate)
    unchanged = [d for d in result["case_diffs"] if d["case_id"] == "inventory_check_02"]
    assert unchanged[0]["status"] == "unchanged"


def test_path_changed_same_grade_detected():
    baseline, candidate = _load()
    result = diff_traces(baseline, candidate)
    path_changed_ids = [d["case_id"] for d in result["path_changed_same_grade"]]
    assert "path_change_05" in path_changed_ids


def test_removed_case_flagged():
    baseline, candidate = _load()
    result = diff_traces(baseline, candidate)
    assert "removed_case_04" in result["only_in_baseline"]


def test_added_case_flagged():
    baseline, candidate = _load()
    result = diff_traces(baseline, candidate)
    assert "new_case_06" in result["only_in_candidate"]


def test_diff_case_pass_to_fail_is_regression():
    baseline_case = {"case_id": "x", "grade": "pass", "output": "a", "trajectory": []}
    candidate_case = {"case_id": "x", "grade": "fail", "output": "b", "trajectory": []}
    result = diff_case(baseline_case, candidate_case)
    assert result["status"] == "regression"


def test_diff_case_fail_to_pass_is_improvement():
    baseline_case = {"case_id": "x", "grade": "fail", "output": "a", "trajectory": []}
    candidate_case = {"case_id": "x", "grade": "pass", "output": "b", "trajectory": []}
    result = diff_case(baseline_case, candidate_case)
    assert result["status"] == "improvement"


def test_diff_case_identical_is_unchanged():
    case = {"case_id": "x", "grade": "pass", "output": "a", "trajectory": [{"tool": "t1"}]}
    result = diff_case(dict(case), dict(case))
    assert result["status"] == "unchanged"
    assert result["sequence_changed"] is False
