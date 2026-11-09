"""A 9 E fixed-point axis when the input line AB is a proper secant.

This restricted construction requires two real AB/circle intersections and
generic intermediate incidences. It does not cover the full study domain D2.
"""

import argparse
import hashlib
import json
from pathlib import Path

from castillon import FIXTURES, Replay, circle_meet, encode, finish, other

ROOT = Path(__file__).resolve().parents[1]
PROFILE = ROOT / "profiles/castillon-d2-e-generic-v1.json"


def secant_prefix(a, b, c):
    replay = Replay(a, b, c)
    replay.draw("seed_AB", "A", "B")
    roots = circle_meet(replay.lines["seed_AB"])
    if len(roots) != 2:
        raise ValueError("AB must intersect Gamma in two distinct real points")
    for name, point in zip(("U", "V"), roots):
        replay.bind(name, point, ["seed_AB", "Gamma"])
    replay.project("W", "U", "C", "l2")
    replay.project("T", "V", "C", "l3")
    replay.project("R", "W", "B", "l4")
    replay.project("P", "R", "A", "l5")
    for start, image in (("U", "W"), ("V", "T"), ("P", "U")):
        point = replay.points[start]
        for center in "ABC":
            point = other(point, replay.points[center])
        assert point == replay.points[image]
    return replay


def secant_baseline(a, b, c):
    replay = secant_prefix(a, b, c)
    replay.draw("l6", "U", "T")
    replay.draw("l7", "V", "W")
    replay.intersection("J", "l6", "l7")
    replay.draw("l8", "T", "P")
    replay.intersection("H", "seed_AB", "l8")
    replay.draw("axis", "J", "H")
    assert replay.lines["axis"] == replay.axis
    return replay


def build_certificate():
    reports = []
    for name, inputs in FIXTURES.items():
        scores, programs = {}, {}
        for target, all_solutions, edges in (
            ("axis", False, False),
            ("one_vertices", False, False),
            ("one_edges", False, True),
            ("all_vertices", True, False),
            ("all_edges", True, True),
        ):
            replay = secant_baseline(*inputs)
            if target != "axis":
                finish(replay, all_solutions, edges)
            scores[target] = replay.score
            programs[target] = replay.program
        reports.append({
            "fixture": name, "input": encode(inputs), "scores": scores, "programs": programs,
        })
    profile = json.loads(PROFILE.read_text("utf-8"))
    profile_bytes = PROFILE.read_bytes().replace(b"\r\n", b"\n")
    return {
        "profile_id": profile["id"],
        "profile_sha256": hashlib.sha256(profile_bytes).hexdigest(),
        "metric": profile["metric"],
        "claim": "restricted upper bounds on the proper-AB-secant subdomain of D2",
        "restriction": "proper AB secant and generic intermediate incidences",
        "reports": reports,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    certificate = build_certificate()
    if args.output:
        rendered = json.dumps(certificate, ensure_ascii=False, indent=2) + "\n"
        args.output.write_text(rendered, "utf-8")
    print(json.dumps({"fixtures": len(certificate["reports"]),
                      "scores": certificate["reports"][0]["scores"]}, indent=2))


if __name__ == "__main__":
    main()
