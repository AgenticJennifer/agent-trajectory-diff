"""
Reads JSONL trace files in eval-lite's format (case_id, input, output,
expected, tags, trajectory, grade, grader_note — one JSON object per
line) and validates the minimum shape needed to diff them.

Not coupled to eval-lite as a package dependency — just the same file
format, so this tool works on any JSONL trace log that uses these field
names, including exports reshaped from other tools.
"""

import json
from pathlib import Path

REQUIRED_FIELDS = {"case_id"}


def load_jsonl(path) -> list[dict]:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(f"{path} does not exist")

    records = []
    with open(path) as f:
        for line_num, line in enumerate(f, start=1):
            line = line.strip()
            if not line:
                continue
            try:
                record = json.loads(line)
            except json.JSONDecodeError as e:
                raise ValueError(f"{path}:{line_num} is not valid JSON: {e}") from e

            missing = REQUIRED_FIELDS - record.keys()
            if missing:
                raise ValueError(f"{path}:{line_num} missing required field(s): {missing}")

            record.setdefault("trajectory", [])
            record.setdefault("grade", None)
            record.setdefault("output", None)
            records.append(record)

    return records


def index_by_case_id(records: list[dict]) -> dict:
    """
    Last write wins if case_id repeats (matches eval-lite's append-only
    log semantics, where re-running a case logs a new line rather than
    overwriting).
    """
    indexed = {}
    for record in records:
        indexed[record["case_id"]] = record
    return indexed
