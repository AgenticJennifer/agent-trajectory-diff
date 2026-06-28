#!/usr/bin/env python3
"""
agent-trajectory-diff: diff two JSONL trace logs by case_id.

Usage:
    python cli.py baseline.jsonl candidate.jsonl
    python cli.py baseline.jsonl candidate.jsonl --json out.json
"""

import argparse
import json
import sys
from pathlib import Path

from trajdiff import load_jsonl, diff_traces, render


def main():
    parser = argparse.ArgumentParser(description="Diff two agent trace logs by case_id, tool sequence, and grade.")
    parser.add_argument("baseline", type=str, help="Path to the baseline JSONL trace file.")
    parser.add_argument("candidate", type=str, help="Path to the candidate JSONL trace file.")
    parser.add_argument("--json", type=str, default=None, help="Also write the raw diff result as JSON to this path.")
    args = parser.parse_args()

    try:
        baseline_records = load_jsonl(args.baseline)
        candidate_records = load_jsonl(args.candidate)
    except (FileNotFoundError, ValueError) as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

    result = diff_traces(baseline_records, candidate_records)
    print(render(result))

    if args.json:
        Path(args.json).write_text(json.dumps(result, indent=2))
        print(f"\nJSON diff written to {args.json}", file=sys.stderr)

    # Exit non-zero on regressions so this is usable as a CI gate.
    if result["regressions"]:
        sys.exit(2)


if __name__ == "__main__":
    main()
