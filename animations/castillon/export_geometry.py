"""Export the certified 14/17 E programs for display in Manim."""

from __future__ import annotations

import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments"))

from castillon import FIXTURES, Q, baseline, circle_meet, encode, finish


OUTPUT_DIRECTORY = Path(__file__).parent
FIXTURE = "inside"
MODES = {"one": "one_edges", "both": "all_edges"}


def approximate(value):
    if isinstance(value, Q):
        return float(value.a) + float(value.b) * math.sqrt(float(value.d))
    return float(value)


def build_export(mode):
    target = MODES[mode]
    certificate = json.loads((ROOT / "experiments/results/baseline.json").read_text("utf-8"))
    profile_path = ROOT / "profiles/castillon-d2-e-generic-v1.json"
    profile_bytes = profile_path.read_bytes().replace(b"\r\n", b"\n")
    if certificate["profile_sha256"] != hashlib.sha256(profile_bytes).hexdigest():
        raise ValueError("certificate profile hash does not match")
    report = next(item for item in certificate["reports"] if item["fixture"] == FIXTURE)
    replay = finish(baseline(*FIXTURES[FIXTURE]), all_solutions=mode == "both")
    if (
        report["input"] != encode(FIXTURES[FIXTURE])
        or report["programs"][target] != replay.program
        or report["scores"][target] != replay.score
    ):
        raise ValueError("exact replay differs from the certified program")

    points = {
        name: {
            "at": list(map(approximate, replay.points[name])),
            "parents": [],
            "available_after": 0,
        }
        for name in ("O", "A", "B", "C")
    }
    events = []
    step = 0
    for entry in replay.program:
        name = entry["id"]
        if entry["op"] == "line":
            step = entry["E"]
            if any(points[key]["available_after"] >= step for key in entry["points"]):
                raise ValueError("a drawing references an unavailable point")
            events.append({
                "e_move": step,
                "id": name,
                "op": "line",
                "references": entry["points"],
                "geometry": list(map(approximate, replay.lines[name])),
                "new_points": [],
            })
        else:
            parents = entry["objects"]
            point = replay.points[name]
            record = {
                "at": list(map(approximate, point)),
                "exact": entry["value"],
                "parents": parents,
                "available_after": step,
            }
            if "Gamma" in parents:
                carrier = next(parent for parent in parents if parent != "Gamma")
                if any(isinstance(value, Q) for value in replay.lines[carrier]):
                    record["other_than"] = events[-1]["references"][0]
                else:
                    record["intersection_index"] = circle_meet(replay.lines[carrier]).index(point)
            points[name] = record
            events[-1]["new_points"].append(name)

    targets = []
    for index in range(2 if mode == "both" else 1):
        vertices = [f"{letter}{index}" for letter in "XYZ"]
        edges = [f"edge_{letter}_{index}" for letter in "ABC"]
        targets.append({
            "vertices": vertices,
            "edges": edges,
            "vertices_at": max(points[name]["available_after"] for name in vertices),
            "edges_at": max(event["e_move"] for event in events if event["id"] in edges),
        })
    trace_bytes = json.dumps(replay.program, sort_keys=True, separators=(",", ":")).encode()
    return {
        "schema": "euclid-castillon-min-manim/v1",
        "mode": mode,
        "source": {
            "certificate": "experiments/results/baseline.json",
            "fixture": FIXTURE,
            "profile_sha256": certificate["profile_sha256"],
            "trace_sha256": hashlib.sha256(trace_bytes).hexdigest(),
        },
        "result": {"target": target, "coverage": "gen", **replay.score},
        "initial": {"circle": {"id": "Gamma", "center": [0, 0], "radius": 1}},
        "points": points,
        "events": events,
        "targets": targets,
    }


def main():
    for mode in MODES:
        path = OUTPUT_DIRECTORY / f"geometry_{mode}.json"
        rendered = json.dumps(build_export(mode), ensure_ascii=False, indent=2) + "\n"
        path.write_text(rendered, "utf-8")
        print(path)


if __name__ == "__main__":
    main()
