"""
Diffs two trace sets (baseline vs candidate) aligned by case_id.

Three things actually matter when you're comparing agent runs across two
versions of a prompt, model, or workflow:

1. Did the grade change? (regression or improvement)
2. Did the tool-call sequence change? (different path to the same or
   different answer — this is the thing final-answer-only evals miss)
3. Did a case disappear or get added? (someone changed the eval set
   itself, which should be visible, not silent)
"""

from .loader import index_by_case_id


def _tool_sequence(trajectory: list) -> list:
    """Extract just the ordered list of tool names called, ignoring args
    and results — that's the coarsest, most important signal: did the
    agent take a different path."""
    return [step.get("tool") for step in trajectory if isinstance(step, dict) and "tool" in step]


def diff_case(baseline: dict, candidate: dict) -> dict:
    base_seq = _tool_sequence(baseline.get("trajectory", []))
    cand_seq = _tool_sequence(candidate.get("trajectory", []))

    grade_changed = baseline.get("grade") != candidate.get("grade")
    sequence_changed = base_seq != cand_seq
    output_changed = baseline.get("output") != candidate.get("output")

    result = {
        "case_id": baseline["case_id"],
        "status": "unchanged",
        "grade_changed": grade_changed,
        "baseline_grade": baseline.get("grade"),
        "candidate_grade": candidate.get("grade"),
        "sequence_changed": sequence_changed,
        "baseline_tool_sequence": base_seq,
        "candidate_tool_sequence": cand_seq,
        "output_changed": output_changed,
    }

    if grade_changed:
        if baseline.get("grade") == "pass" and candidate.get("grade") == "fail":
            result["status"] = "regression"
        elif baseline.get("grade") == "fail" and candidate.get("grade") == "pass":
            result["status"] = "improvement"
        else:
            result["status"] = "grade_changed"
    elif sequence_changed:
        result["status"] = "path_changed_same_grade"

    return result


def diff_traces(baseline_records: list[dict], candidate_records: list[dict]) -> dict:
    baseline_index = index_by_case_id(baseline_records)
    candidate_index = index_by_case_id(candidate_records)

    baseline_ids = set(baseline_index.keys())
    candidate_ids = set(candidate_index.keys())

    shared_ids = baseline_ids & candidate_ids
    only_in_baseline = baseline_ids - candidate_ids
    only_in_candidate = candidate_ids - baseline_ids

    case_diffs = [diff_case(baseline_index[cid], candidate_index[cid]) for cid in sorted(shared_ids)]

    return {
        "case_diffs": case_diffs,
        "only_in_baseline": sorted(only_in_baseline),
        "only_in_candidate": sorted(only_in_candidate),
        "regressions": [d for d in case_diffs if d["status"] == "regression"],
        "improvements": [d for d in case_diffs if d["status"] == "improvement"],
        "path_changed_same_grade": [d for d in case_diffs if d["status"] == "path_changed_same_grade"],
    }
