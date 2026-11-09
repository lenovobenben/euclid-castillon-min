"""Screen one legal line/circle for obtaining the two fixed circle points.

All rational line/line and known circle intersections of the chosen prefixes
are available. This bounded family is not the complete construction search.
"""

from itertools import combinations
import json
from pathlib import Path

from castillon import FIXTURES, prefix, canonical, line, dot


def state(points, stage):
    r = prefix(*points)
    if stage == "8H":
        r.draw("l10", "S", "Up")
    elif stage in (8, 9, 10):
        r.draw("l8", "U", "Vp")
        if stage >= 9:
            r.draw("l9", "V", "Up")
            r.intersection("J", "l8", "l9")
        if stage >= 10:
            r.draw("l10", "S", "Up")
            r.intersection("H", "l7", "l10")
    return r


def screen(stage):
    states = [state(points, stage) for points in FIXTURES.values()]
    closures = [r.closure() for r in states]
    names = sorted(set.intersection(*(set(c) for c in closures)))
    hits = []
    counts = {"line": 0, "circle": 0}
    for p, q in combinations(names, 2):
        try:
            axes = [canonical(line(c[p], c[q])) for c in closures]
        except ValueError:
            continue
        counts["line"] += 1
        if all(l == r.axis for l, r in zip(axes, states)):
            hits.append({"op": "line", "points": [p, q]})
    for center in names:
        for through in names:
            if center == through:
                continue
            axes = []
            try:
                for c in closures:
                    p, q = c[center], c[through]
                    if p == q or p == (0, 0):
                        break
                    # Radical axis of Circle(center=p,through=q) with Gamma.
                    axes.append(canonical((2 * p[0], 2 * p[1], dot(q, q) - 2 * dot(p, q) - 1)))
            except ValueError:
                continue
            if len(axes) != len(states):
                continue
            counts["circle"] += 1
            if all(l == r.axis for l, r in zip(axes, states)):
                hits.append({"op": "circle", "center": center, "through": through})
    return {
        "stage": stage,
        "prefix_e": states[0].score["total"],
        "addresses": len(names),
        "candidate_addresses": counts,
        "hits": hits,
    }


def main():
    result = {
        "fixtures": list(FIXTURES),
        "stages": [screen(k) for k in [7, 8, "8H", 9, 10]],
        "scope": "one move from selected exact rational prefixes",
        "minimality_proved": False,
    }
    p = Path(__file__).resolve().parent / "results" / "one-move-finish.json"
    p.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
