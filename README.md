# agent-trajectory-diff

Diffs two agent trace logs by `case_id` and tells you three things a
final-answer-only eval misses: did the grade change, did the tool-call
*sequence* change, and did cases get silently added or removed from the
eval set itself.

Built to read JSONL traces in [eval-lite](https://github.com/agenticjennifer/eval-lite)'s
format — `case_id`, `input`, `output`, `grade`, `trajectory` — but it
isn't coupled to eval-lite as a dependency. Any JSONL log using those
field names works, including reshaped exports from other tools.

## Why this exists

A final answer can be right by luck. An agent that succeeds after six
wrong tool calls and an agent that succeeds in two calls both show
"pass" if you only grade the final output. This tool diffs the actual
*path* — which tools got called, in what order — between a baseline run
and a candidate run, so a path regression shows up even when the grade
doesn't change.

## Usage

```bash
python cli.py baseline.jsonl candidate.jsonl
python cli.py baseline.jsonl candidate.jsonl --json diff.json
```

Exits with code `2` if any regressions are found — wire it into CI as a
quality gate:

```yaml
- name: Check for agent regressions
  run: python cli.py baseline.jsonl candidate.jsonl
```

## What counts as a diff

For every `case_id` present in both files:

- **regression** — graded `pass` in baseline, `fail` in candidate
- **improvement** — graded `fail` in baseline, `pass` in candidate
- **path_changed_same_grade** — same grade, different tool-call sequence
  (worth knowing even when nothing "broke" — a quieter or more expensive
  path to the same answer is still a change worth seeing)
- **unchanged** — same grade, same tool sequence

Cases present in only one file are reported separately as
`only_in_baseline` / `only_in_candidate` — useful for catching when
someone silently dropped or added eval cases between runs.

## Example output

```
Trajectory diff: 4 shared case(s)
  1 regression(s)  1 improvement(s)  1 path-changed (same grade)

Removed from candidate (1):
  - removed_case_04

Added in candidate (1):
  + new_case_06

Regressions:
  [route_planner_01] pass -> fail

Improvements:
  [eta_estimate_03] fail -> pass
      tools: ['eta_calc'] -> ['eta_calc', 'traffic_check']

Path changed, same grade:
  [path_change_05] pass -> pass
      tools: ['carrier_lookup', 'price_compare'] -> ['price_compare', 'carrier_lookup']
```

## Run tests

```bash
pip install pytest
pytest tests/ -v
```

15 tests against hand-written fixtures (`tests/fixtures/baseline.jsonl`,
`tests/fixtures/candidate.jsonl`) with deliberately known diffs — a
regression, an improvement, a path-change, an added case, and a removed
case — so the test suite is checking against ground truth you can read
yourself, not just "the code agrees with itself."

## License

MIT
