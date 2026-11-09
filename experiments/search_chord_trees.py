"""Enumerate pencil-chord trees, then minimize projectivity-axis cross joins.

Finite family only: initial OA chord, then A/B/C pencil chords. No arbitrary
joins, new circles, or unrelated line-intersection points in the tree prefix.
"""

from itertools import combinations
import json
from pathlib import Path

from castillon import FIXTURES, F, other, line, meet, on_line, target_axis


def step(word, label):
    return word[:-1] if word and word[-1] == label else word + (label,)


def image(word):
    for label in "ABC":
        word = step(word, label)
    return word


def edge(p, q):
    if p == q:
        return None
    return tuple(sorted((p, q)))


def wordname(w):
    return "U" if not w else "".join(w)


def geometry(vertices, points):
    centers = dict(zip("ABC", points))
    result = {(): (F(-1), F(0))}
    for w in sorted(vertices, key=lambda x: (len(x), x)):
        if w:
            result[w] = other(result[w[:-1]], centers[w[-1]])
    return result


def evaluate(vertices):
    pairs = [(w, image(w)) for w in sorted(vertices) if image(w) in vertices]
    if len(pairs) < 3:
        return None
    old = {edge(w, w[:-1]) for w in vertices if w}
    geometries = [geometry(vertices, pts) for pts in FIXTURES.values()]
    axes = [target_axis(*pts) for pts in FIXTURES.values()]
    witnesses = []
    for (u, up), (v, vp) in combinations(pairs, 2):
        p, q = edge(u, vp), edge(up, v)
        if p is None or q is None or p == q:
            continue
        values = []
        try:
            for g, axis in zip(geometries, axes):
                point = meet(line(g[p[0]], g[p[1]]), line(g[q[0]], g[q[1]]))
                if not on_line(point, axis):
                    break
                values.append(point)
        except (ValueError, ZeroDivisionError):
            continue
        if len(values) == len(geometries):
            witnesses.append((p, q, values, set((p, q)) - old))
    best = None
    for x, y in combinations(witnesses, 2):
        if any(p == q for p, q in zip(x[2], y[2])):
            continue
        extra = x[3] | y[3]
        cost = len(old) + len(extra) + 1
        if best is None or cost < best[0]:
            best = (cost, x, y, extra)
    if best is None:
        return None
    cost, x, y, extra = best

    def convert(e):
        return [wordname(w) for w in e]

    return {
        "axis_e": cost,
        "prefix_e": len(old),
        "vertices": [wordname(w) for w in sorted(vertices, key=lambda x: (len(x), x))],
        "new_chords": [convert(e) for e in sorted(extra)],
        "axis_witnesses": [[convert(w[0]), convert(w[1])] for w in (x, y)],
    }


def main():
    states = {frozenset([(), ("A",)])}
    statistics = []
    candidates = []
    for e in range(1, 9):
        eligible = [s for s in states if sum(image(w) in s for w in s) >= 3]
        statistics.append({"prefix_e": e, "trees": len(states), "three_pairs": len(eligible)})
        for s in sorted(eligible, key=lambda x: sorted(x)):
            result = evaluate(s)
            if result is not None:
                candidates.append(result)
        if e < 8:
            next_states = set()
            for s in states:
                for w in s:
                    for label in "ABC":
                        v = step(w, label)
                        if v not in s:
                            next_states.add(s | {v})
            states = next_states
    candidates.sort(key=lambda x: (x["axis_e"], x["prefix_e"], x["vertices"]))
    result = {
        "statistics": statistics,
        "fixtures": list(FIXTURES),
        "best_axis_e_in_family": candidates[0]["axis_e"],
        "candidates": candidates,
        "minimality_proved": False,
        "scope": "OA seed, at most eight pencil chords, two cross-join witnesses",
    }
    p = Path(__file__).resolve().parent / "results" / "chord-trees.json"
    p.write_text(json.dumps(result, indent=2) + "\n")
    print(
        json.dumps(
            {"statistics": statistics, "best": candidates[:5], "candidates": len(candidates)},
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
