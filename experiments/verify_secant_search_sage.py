"""Independently recheck every raw numerical hit from the secant searches."""

import json
from pathlib import Path

from sage.all import AA

from classify_sage import dot, sub
from verify_sage import decode, expected_targets, ln, normalize, second, verify_program

if not __debug__:
    raise RuntimeError("exact verification requires Python assertions enabled")

ROOT = Path(__file__).resolve().parents[1]


def unit_line(p, q):
    values = normalize(ln(p, q))
    norm = (values[0] ** 2 + values[1] ** 2).sqrt()
    return tuple(value / norm for value in values)


def intersections(first, second_object):
    kind, geometry = first
    other_kind, other = second_object
    if kind == "line" and other_kind == "line":
        a, b, c = geometry
        u, v, w = other
        denominator = a * v - b * u
        return [] if denominator == 0 else [
            ((b * w - c * v) / denominator, (c * u - a * w) / denominator)
        ]
    if kind == "circle" and other_kind == "line":
        return intersections(second_object, first)
    if kind == "line":
        a, b, c = geometry
        center, radius_squared = other[:2], other[2]
        distance = a * center[0] + b * center[1] + c
        foot = (center[0] - distance * a, center[1] - distance * b)
        remainder = radius_squared - distance * distance
        direction = (-b, a)
    else:
        center, radius_squared = geometry[:2], geometry[2]
        delta = sub(other[:2], center)
        distance_squared = dot(delta, delta)
        if distance_squared == 0:
            return []
        fraction = (distance_squared + radius_squared - other[2]) / (2 * distance_squared)
        foot = (center[0] + fraction * delta[0], center[1] + fraction * delta[1])
        remainder = radius_squared / distance_squared - fraction * fraction
        direction = (-delta[1], delta[0])
    if remainder < 0:
        return []
    if remainder == 0:
        return [foot]
    root = remainder.sqrt()
    return [(foot[0] + root * direction[0], foot[1] + root * direction[1]),
            (foot[0] - root * direction[0], foot[1] - root * direction[1])]


def populate_aliases(points, objects):
    entries = list(objects.items())
    for index, (name, item) in enumerate(entries):
        for other_name, other in entries[:index]:
            for branch, point in enumerate(intersections(item, other)):
                points[f"{name}&{other_name}:{branch}"] = point


def certified_prefix(report, stage=5):
    inputs = decode(report["input"])
    points = {"O": (AA(0), AA(0)), **dict(zip("ABC", inputs))}
    objects = {"Gamma": ("circle", (AA(0), AA(0), AA(1)))}
    for entry in report["programs"]["axis"]:
        name = entry["id"]
        if entry["op"] == "line":
            if entry["E"] > stage:
                break
            objects[name] = ("line", unit_line(*(points[key] for key in entry["points"])))
        else:
            first, other = (objects[key] for key in entry["objects"])
            claimed = decode(entry["value"])
            assert claimed in intersections(first, other)
            points[name] = claimed
    populate_aliases(points, objects)
    return points, objects


def add_object(state, operation):
    points, objects = state
    p, q = (points[key] for key in operation["points"])
    if p == q:
        raise ValueError("coincident defining points")
    fresh = (("line", unit_line(p, q)) if operation["op"] == "line"
             else ("circle", (*p, dot(sub(p, q), sub(p, q)))))
    if fresh in objects.values():
        raise ValueError("duplicate primitive")
    name = operation["id"]
    for parent, old in objects.items():
        for branch, point in enumerate(intersections(fresh, old)):
            points[f"{name}&{parent}:{branch}"] = point
    objects[name] = fresh
    return state


def chord_state(report, words):
    state = certified_prefix(report, stage=1)
    points, _ = state
    points["p_A"] = points["V"]
    for word in sorted(words, key=lambda value: (len(value), value)):
        if not word or word == ["A"]:
            continue
        parent = "p_" + "".join(word[:-1]) if len(word) > 1 else "U"
        name = "p_" + "".join(word)
        add_object(state, {"id": "chord_" + "".join(word), "op": "line",
                           "points": [parent, word[-1]]})
        points[name] = second(points[parent], points[word[-1]])
    return state


def exact_finish(state, final, triangles):
    points, objects = state
    p, q = (points[key] for key in final["points"])
    if p == q:
        return False
    index = final["target"] % 3
    if final["op"] == "circle":
        radius_squared = dot(sub(p, q), sub(p, q))
        if ("circle", (*p, radius_squared)) in objects.values():
            return False
        return any(dot(sub(p, triangle[index]), sub(p, triangle[index])) == radius_squared
                   for triangle in triangles)
    coefficients = unit_line(p, q)

    def contains(point):
        return coefficients[0] * point[0] + coefficients[1] * point[1] + coefficients[2] == 0

    if final["goal"] == "vertex_axis":
        return all(contains(triangle[index]) for triangle in triangles)
    return any(contains(triangle[index]) and contains(triangle[(index + 1) % 3])
               for triangle in triangles)


def main():
    certificate = json.loads((ROOT / "experiments/results/secant-seed.json").read_text("utf-8"))
    reports = certificate["reports"]
    calibrations = {}
    for report in reports:
        inputs = decode(report["input"])
        _, triangles = expected_targets(inputs)
        result = verify_program(inputs, report["programs"]["axis"], "axis")
        assert result["total"] == 9
        assert exact_finish(certified_prefix(report, stage=8), {
            "op": "line", "points": ["J", "H"], "goal": "vertex_axis", "target": 0,
        }, triangles)
        calibrations[report["fixture"]] = True
    records = []
    for name in ("secant-mixed", "secant-chords"):
        search = json.loads((ROOT / f"experiments/results/{name}.json").read_text("utf-8"))
        for candidate in search["raw_candidates"]:
            checks = {}
            for report in reports:
                _, triangles = expected_targets(decode(report["input"]))
                try:
                    if name == "secant-chords":
                        state = chord_state(report, candidate["words"])
                    else:
                        state = certified_prefix(report)
                        for action in candidate["prefix"]:
                            state = add_object(state, action)
                    hit = exact_finish(state, candidate["final"], triangles)
                    checks[report["fixture"]] = {"exact_target_hit": hit}
                except (ValueError, KeyError) as error:
                    checks[report["fixture"]] = {"exact_target_hit": False, "error": str(error)}
            records.append({"search": name, "candidate": candidate, "fixtures": checks})
    print(json.dumps({
        "calibration_nine_move_axis": calibrations,
        "raw_candidate_checks": records,
        "all_fixture_survivors": sum(all(check["exact_target_hit"]
                                          for check in record["fixtures"].values())
                                     for record in records),
        "minimality_proved": False,
    }, indent=2))


if __name__ == "__main__":
    main()
