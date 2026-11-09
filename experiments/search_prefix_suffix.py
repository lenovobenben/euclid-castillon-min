"""Bounded exact search for cheaper axis preparation after a seven-line prefix.

This is not an exhaustive E-move search and establishes no lower bound.
It enumerates one line through two rational points in the seven-line closure.
Only its intersections with already drawn lines are considered as axis points.
Candidates must work on every fixture, with the same dependency addresses.
"""

from itertools import combinations
import json
from pathlib import Path

from castillon import FIXTURES, prefix, line, canonical, meet, on_line, encode


def search(extend_known=False):
    states = [prefix(*pts) for pts in FIXTURES.values()]
    if extend_known:
        for state in states:
            state.draw("l10", "S", "Up")
    closures = [s.closure() for s in states]
    names = sorted(set.intersection(*(set(c) for c in closures)))
    candidates = []
    seen = set()
    for p, q in combinations(names, 2):
        try:
            lines = [canonical(line(c[p], c[q])) for c in closures]
        except (ValueError, ZeroDivisionError):
            continue
        key = tuple(lines)
        if key in seen or all(l in state.lines.values() for l, state in zip(lines, states)):
            continue
        seen.add(key)
        for carrier in states[0].lines:
            intersections = []
            try:
                for state, l in zip(states, lines):
                    point = meet(l, state.lines[carrier])
                    if not on_line(point, state.axis):
                        break
                    intersections.append(point)
            except (ValueError, ZeroDivisionError):
                continue
            if len(intersections) == len(states):
                candidates.append(
                    {"points": [p, q], "carrier": carrier, "first_point": encode(intersections[0])}
                )
    distinct = {tuple(c["first_point"]) for c in candidates}
    old_axis_points = {tuple(encode(p)) for p in closures[0].values() if on_line(p, states[0].axis)}
    result = {
        "prefix_lines": 8 if extend_known else 7,
        "fixtures": list(FIXTURES),
        "point_addresses": len(names),
        "distinct_candidate_lines": len(seen),
        "successful_extensions": candidates,
        "distinct_axis_points": len(distinct),
        "already_present_axis_points": len(old_axis_points),
        "new_axis_points": len(distinct - old_axis_points),
        "scope": "one new line, rational prefix points, old line carriers only",
        "minimality_proved": False,
    }
    return result


def main():
    result = {"stages": [search(False), search(True)]}
    output = Path(__file__).resolve().parent / "results" / "prefix-suffix.json"
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
