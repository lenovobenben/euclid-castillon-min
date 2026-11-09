"""Screen all bounded AB-seed pencil-chord trees for a direct final move.

The AB chord is shared by the A and B involutions. Its quotient word tree
differs from the older OA-seed search. The numerical screen also allows
circles and line-line intersections in the final move. Requires NumPy.
"""

import argparse
from itertools import combinations
import json
from pathlib import Path

from castillon import FIXTURES, Replay, circle_meet
from search_secant_mixed import (
    expected_targets, final_moves, initial_state, replay_state, validate_finish,
)


def step(word, label):
    if not word and label in "AB":
        return ("A",)
    if word == ("A",) and label in "AB":
        return ()
    return word[:-1] if word and word[-1] == label else word + (label,)


def image(word):
    for label in "ABC":
        word = step(word, label)
    return word


def edge(first, second):
    return tuple(sorted((first, second))) if first != second else None


def formal_cost(vertices):
    pairs = [(point, image(point)) for point in sorted(vertices) if image(point) in vertices]
    if len(pairs) < 3:
        return None
    old = {edge(word, word[:-1]) for word in vertices if word}
    witnesses = []
    for (u, fu), (v, fv) in combinations(pairs, 2):
        first, second = edge(u, fv), edge(fu, v)
        if first is not None and second is not None and first != second:
            witnesses.append((frozenset((first, second)), {first, second} - old))
    costs = [len(old) + len(first[1] | second[1]) + 1
             for first, second in combinations(witnesses, 2) if first[0] != second[0]]
    return min(costs) if costs else None


def point_name(word):
    return "p_" + "".join(word) if word else "U"


def build_state(inputs, vertices):
    replay = Replay(*inputs)
    replay.draw("seed_AB", "A", "B")
    for word, point in zip(((), ("A",)), circle_meet(replay.lines["seed_AB"])):
        replay.bind(point_name(word), point, ["seed_AB", "Gamma"])
    for word in sorted(vertices, key=lambda item: (len(item), item)):
        if word in ((), ("A",)):
            continue
        replay.project(point_name(word), point_name(word[:-1]), word[-1],
                       "chord_" + "".join(word))
    return replay_state(replay)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-prefix", type=int, default=7)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    if not 1 <= args.max_prefix <= 8:
        parser.error("max-prefix must be between 1 and 8")
    discovery = FIXTURES["inside"]
    target = expected_targets(discovery)
    calibration = final_moves(initial_state(discovery, stage=8), target)
    assert any(item["goal"] == "vertex_axis" and item["target"] == 0 for item in calibration)
    states = {frozenset(((), ("A",)))}
    statistics, candidates, raw_candidates = [], [], []
    best_formal = None
    raw_hits = 0
    for paid in range(1, args.max_prefix + 1):
        eligible, best = 0, None
        for vertices in sorted(states, key=lambda value: sorted(value)):
            cost = formal_cost(vertices)
            if cost is not None:
                eligible += 1
                best = cost if best is None else min(best, cost)
                best_formal = cost if best_formal is None else min(best_formal, cost)
            for final in final_moves(build_state(discovery, vertices), target):
                raw_hits += 1
                raw_candidates.append({"prefix_e": paid, "words": sorted(vertices),
                                       "final": final})
                if all(
                    validate_finish(build_state(inputs, vertices), expected_targets(inputs), final)
                    for inputs in FIXTURES.values()
                ):
                    candidate = {"prefix_e": paid, "words": sorted(vertices), "final": final}
                    candidates.append(candidate)
                    print(json.dumps(candidate), flush=True)
        row = {"prefix_e": paid, "trees": len(states), "three_pairs": eligible,
               "best_formal_axis_candidate": best}
        statistics.append(row)
        print(json.dumps(row), flush=True)
        if paid < args.max_prefix:
            states = {vertices | {new} for vertices in states for word in vertices
                      for label in "ABC" if (new := step(word, label)) not in vertices}
    result = {
        "scope": "AB-seed pencil-chord trees and one arbitrary final line/circle",
        "max_prefix": args.max_prefix, "statistics": statistics,
        "discovery_fixture": "inside", "validation_fixtures": list(FIXTURES),
        "minimum_formal_axis_candidate": best_formal,
        "raw_hits": raw_hits, "raw_candidates": raw_candidates, "candidates": candidates,
        "calibration_nine_move_axis": True,
        "minimality_proved": False, "exact_validation_required": True,
    }
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n", "utf-8")
    print(json.dumps({"trees": sum(row["trees"] for row in statistics),
                      "candidates": len(candidates)}), flush=True)


if __name__ == "__main__":
    main()
