from pathlib import Path
import pytest

from trajdiff.loader import load_jsonl, index_by_case_id

FIXTURES = Path(__file__).parent / "fixtures"


def test_load_jsonl_parses_all_lines():
    records = load_jsonl(FIXTURES / "baseline.jsonl")
    assert len(records) == 5
    assert records[0]["case_id"] == "route_planner_01"


def test_load_jsonl_missing_file_raises():
    with pytest.raises(FileNotFoundError):
        load_jsonl(FIXTURES / "does_not_exist.jsonl")


def test_load_jsonl_rejects_missing_case_id(tmp_path):
    bad_file = tmp_path / "bad.jsonl"
    bad_file.write_text('{"input": "no case_id here"}\n')
    with pytest.raises(ValueError, match="missing required field"):
        load_jsonl(bad_file)


def test_load_jsonl_rejects_invalid_json(tmp_path):
    bad_file = tmp_path / "bad.jsonl"
    bad_file.write_text('{"case_id": "ok"}\nnot json at all\n')
    with pytest.raises(ValueError, match="not valid JSON"):
        load_jsonl(bad_file)


def test_load_jsonl_skips_blank_lines(tmp_path):
    f = tmp_path / "blanks.jsonl"
    f.write_text('{"case_id": "a"}\n\n{"case_id": "b"}\n')
    records = load_jsonl(f)
    assert len(records) == 2


def test_index_by_case_id_last_write_wins():
    records = [{"case_id": "x", "grade": "fail"}, {"case_id": "x", "grade": "pass"}]
    indexed = index_by_case_id(records)
    assert indexed["x"]["grade"] == "pass"
