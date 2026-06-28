"""
Renders a diff_traces() result as readable terminal output. No color
library dependency — uses plain ANSI codes, and falls back cleanly if the
terminal doesn't render them (they just print as harmless escape codes
most viewers ignore, but kept minimal on purpose either way).
"""

RED = "\033[31m"
GREEN = "\033[32m"
YELLOW = "\033[33m"
RESET = "\033[0m"
BOLD = "\033[1m"


def render(diff_result: dict) -> str:
    lines = []
    n_regressions = len(diff_result["regressions"])
    n_improvements = len(diff_result["improvements"])
    n_path_changed = len(diff_result["path_changed_same_grade"])
    n_total = len(diff_result["case_diffs"])

    lines.append(f"{BOLD}Trajectory diff: {n_total} shared case(s){RESET}")
    lines.append(
        f"  {RED}{n_regressions} regression(s){RESET}  "
        f"{GREEN}{n_improvements} improvement(s){RESET}  "
        f"{YELLOW}{n_path_changed} path-changed (same grade){RESET}"
    )

    if diff_result["only_in_baseline"]:
        lines.append(f"\n{YELLOW}Removed from candidate ({len(diff_result['only_in_baseline'])}):{RESET}")
        for cid in diff_result["only_in_baseline"]:
            lines.append(f"  - {cid}")

    if diff_result["only_in_candidate"]:
        lines.append(f"\n{YELLOW}Added in candidate ({len(diff_result['only_in_candidate'])}):{RESET}")
        for cid in diff_result["only_in_candidate"]:
            lines.append(f"  + {cid}")

    if diff_result["regressions"]:
        lines.append(f"\n{RED}{BOLD}Regressions:{RESET}")
        for d in diff_result["regressions"]:
            lines.append(_render_case(d, RED))

    if diff_result["improvements"]:
        lines.append(f"\n{GREEN}{BOLD}Improvements:{RESET}")
        for d in diff_result["improvements"]:
            lines.append(_render_case(d, GREEN))

    if diff_result["path_changed_same_grade"]:
        lines.append(f"\n{YELLOW}{BOLD}Path changed, same grade:{RESET}")
        for d in diff_result["path_changed_same_grade"]:
            lines.append(_render_case(d, YELLOW))

    return "\n".join(lines)


def _render_case(d: dict, color: str) -> str:
    parts = [f"  {color}[{d['case_id']}]{RESET} {d['baseline_grade']} -> {d['candidate_grade']}"]
    if d["sequence_changed"]:
        parts.append(f"      tools: {d['baseline_tool_sequence']} -> {d['candidate_tool_sequence']}")
    return "\n".join(parts)
