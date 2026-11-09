"""Numerical discovery with up to two mixed moves after the 5 E secant prefix.

The point pool includes every finite real intersection of the displayed
primitives. A final line/circle is screened for any target vertex or edge.
Floating-point screening discovers candidates only. It proves no lower bound.
Requires NumPy, available in the project's Manim image.
"""

import argparse
from itertools import combinations, permutations
import json
import math
from pathlib import Path

import numpy as np

from castillon import FIXTURES, Q, finish
from replay_secant_seed import secant_baseline, secant_prefix

EPSILON = 2e-10


def approximate(value):
    if isinstance(value, Q):
        return float(value.a) + float(value.b) * math.sqrt(float(value.d))
    return float(value)


def normalized_line(first, second):
    a, b = first[1] - second[1], second[0] - first[0]
    norm = math.hypot(a, b)
    if norm < EPSILON:
        return None
    a, b = a / norm, b / norm
    c = -a * first[0] - b * first[1]
    if a < -EPSILON or abs(a) < EPSILON and b < 0:
        a, b, c = -a, -b, -c
    return np.array((a, b, c))


def intersections(first, second):
    kind, geometry = first
    other_kind, other = second
    if kind == "line" and other_kind == "line":
        a, b, c = geometry
        u, v, w = other
        denominator = a * v - b * u
        if abs(denominator) < EPSILON:
            return []
        return [np.array(((b * w - c * v) / denominator,
                          (c * u - a * w) / denominator))]
    if kind == "circle" and other_kind == "line":
        return intersections(second, first)
    if kind == "line":
        a, b, c = geometry
        center, radius_squared = other[:2], other[2]
        distance = a * center[0] + b * center[1] + c
        foot = center - distance * geometry[:2]
        remainder = radius_squared - distance * distance
        if remainder < -EPSILON:
            return []
        offset = math.sqrt(max(0, remainder)) * np.array((-b, a))
    else:
        center, radius_squared = geometry[:2], geometry[2]
        delta = other[:2] - center
        distance_squared = float(delta @ delta)
        if distance_squared < EPSILON**2:
            return []
        fraction = (distance_squared + radius_squared - other[2]) / (2 * distance_squared)
        foot = center + fraction * delta
        remainder = radius_squared / distance_squared - fraction * fraction
        if remainder < -EPSILON:
            return []
        offset = math.sqrt(max(0, remainder)) * np.array((-delta[1], delta[0]))
    if float(offset @ offset) < EPSILON**2:
        return [foot]
    return [foot + offset, foot - offset]


def same_geometry(first, second):
    return first[0] == second[0] and np.allclose(first[1], second[1], rtol=0, atol=EPSILON)


def available_points(points):
    names, values = [], []
    for name, point in points.items():
        if np.isfinite(point).all() and np.linalg.norm(point) < 1e5:
            if not any(np.linalg.norm(point - known) < EPSILON for known in values):
                names.append(name)
                values.append(point)
    return names, np.array(values)


def add_object(state, operation):
    points, objects = state
    p, q = (points[name] for name in operation["points"])
    if operation["op"] == "line":
        geometry = normalized_line(p, q)
        if geometry is None:
            return None
    else:
        radius_squared = float((q - p) @ (q - p))
        if radius_squared < EPSILON**2:
            return None
        geometry = np.array((*p, radius_squared))
    fresh = (operation["op"], geometry)
    if any(same_geometry(fresh, old) for old in objects.values()):
        return None
    result = dict(points)
    name = operation["id"]
    for parent, old in objects.items():
        for branch, point in enumerate(intersections(fresh, old)):
            result[f"{name}&{parent}:{branch}"] = point
    return result, {**objects, name: fresh}


def initial_state(inputs, stage=5):
    replay = secant_prefix(*inputs)
    additions = (("l6", "U", "T"), ("l7", "V", "W"), ("l8", "T", "P"))
    for name, p, q in additions[:stage - 5]:
        replay.draw(name, p, q)
    return replay_state(replay)


def replay_state(replay):
    points = {name: np.array(tuple(map(approximate, point)))
              for name, point in replay.points.items()}
    objects = {"Gamma": ("circle", np.array((0.0, 0.0, 1.0)))}
    for name, coefficients in replay.lines.items():
        values = np.array(tuple(map(approximate, coefficients)))
        values /= np.linalg.norm(values[:2])
        objects[name] = ("line", values)
    entries = list(objects.items())
    for index, (name, item) in enumerate(entries):
        for other_name, other in entries[:index]:
            for branch, point in enumerate(intersections(item, other)):
                points[f"{name}&{other_name}:{branch}"] = point
    return points, objects


def expected_targets(inputs):
    replay = finish(secant_baseline(*inputs), all_solutions=True)
    vertices, edges = [], []
    for index in range(2):
        triangle = [np.array(tuple(map(approximate, replay.points[f"{key}{index}"])))
                    for key in "XYZ"]
        vertices.extend(triangle)
        edges.extend(normalized_line(triangle[i], triangle[(i + 1) % 3]) for i in range(3))
    return np.array(vertices), np.array(edges)


def final_moves(state, targets):
    points, objects = state
    names, values = available_points(points)
    vertices, edges = targets
    found = []
    # Drawing a target edge exposes its two circle vertices at the same time.
    residual = values @ edges[:, :2].T + edges[:, 2]
    for target in range(len(edges)):
        indices = np.flatnonzero(np.abs(residual[:, target]) < EPSILON)
        for first, second in combinations(indices, 2):
            found.append({"op": "line", "points": [names[first], names[second]],
                          "goal": "edge", "target": target})
    # A line through both conjugate starts is also useful for all vertex labels.
    for first, second in ((0, 3), (1, 4), (2, 5)):
        axis = normalized_line(vertices[first], vertices[second])
        indices = np.flatnonzero(np.abs(values @ axis[:2] + axis[2]) < EPSILON)
        for p, q in combinations(indices, 2):
            found.append({"op": "line", "points": [names[p], names[q]],
                          "goal": "vertex_axis", "target": first})
    # Match squared radii for every existing center and through point.
    delta = values[:, None, :] - values[None, :, :]
    radii = np.sum(delta * delta, axis=2)
    to_targets = np.sum((values[:, None, :] - vertices[None, :, :]) ** 2, axis=2)
    for center, through, target in np.argwhere(
        np.abs(radii[:, :, None] - to_targets[:, None, :]) < EPSILON
    ):
        fresh = ("circle", np.array((*values[center], radii[center, through])))
        if center == through or any(same_geometry(fresh, old) for old in objects.values()):
            continue
        found.append({"op": "circle", "points": [names[center], names[through]],
                      "goal": "vertex", "target": int(target)})
    return found


def validate_finish(state, targets, final):
    try:
        p, q = (state[0][name] for name in final["points"])
    except KeyError:
        return False
    vertices, edges = targets
    index = final["target"] % 3
    if final["op"] == "line":
        candidate = normalized_line(p, q)
        if candidate is None:
            return False
        if final["goal"] == "edge":
            alternatives = (edges[index], edges[index + 3])
        else:
            alternatives = (normalized_line(vertices[index], vertices[index + 3]),)
        return any(np.allclose(candidate, target, rtol=0, atol=EPSILON)
                   for target in alternatives)
    radius_squared = float((p - q) @ (p - q))
    return any(abs(float((p - target) @ (p - target)) - radius_squared) < EPSILON
               for target in (vertices[index], vertices[index + 3]))


def validate_numeric(actions, final):
    for inputs in FIXTURES.values():
        state = initial_state(inputs)
        try:
            for operation in actions:
                state = add_object(state, operation)
                if state is None:
                    return False
        except KeyError:
            return False
        if not validate_finish(state, expected_targets(inputs), final):
            return False
    return True


def operations(state, step):
    names, _ = available_points(state[0])
    for kind in ("line", "circle"):
        pairs = combinations(names, 2) if kind == "line" else permutations(names, 2)
        seen = set()
        for pair in pairs:
            operation = {"id": f"s{step}", "op": kind, "points": list(pair)}
            following = add_object(state, operation)
            if following is None:
                continue
            fresh = following[1][operation["id"]]
            key = tuple(np.round(fresh[1], 9))
            if key in seen:
                continue
            seen.add(key)
            yield operation, following


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    parser.add_argument("--max-first", type=int)
    args = parser.parse_args()
    inputs = FIXTURES["inside"]
    targets = expected_targets(inputs)
    calibration = final_moves(initial_state(inputs, stage=8), targets)
    assert any(item["goal"] == "vertex_axis" and item["target"] == 0 for item in calibration)
    counts = {"first": 0, "second": 0, "raw_hits": 0}
    candidates, raw_candidates = [], []
    initial = initial_state(inputs)
    assert add_object(initial, {"id": "duplicate", "op": "circle",
                                "points": ["O", "U"]}) is None
    for first, state in operations(initial, 6):
        if args.max_first is not None and counts["first"] >= args.max_first:
            break
        counts["first"] += 1
        for second, following in operations(state, 7):
            counts["second"] += 1
            for final in final_moves(following, targets):
                counts["raw_hits"] += 1
                raw_candidates.append({"prefix": [first, second], "final": final})
                if validate_numeric([first, second], final):
                    candidate = {"prefix": [first, second], "final": final}
                    candidates.append(candidate)
                    print(json.dumps(candidate), flush=True)
        if counts["first"] % 20 == 0:
            print(json.dumps(counts), flush=True)
    result = {
        "scope": "two mixed moves after the fixed 5 E AB-secant prefix, then one finish",
        "discovery_fixture": "inside", "validation_fixtures": list(FIXTURES),
        "epsilon": EPSILON, "coordinate_bound": 1e5,
        "counts": counts, "raw_candidates": raw_candidates, "candidates": candidates,
        "calibration_nine_move_axis": True,
        "duplicate_input_circle_rejected": True,
        "max_first": args.max_first,
        "minimality_proved": False, "exact_validation_required": True,
    }
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n", "utf-8")
    print(json.dumps({"counts": counts, "candidates": len(candidates)}), flush=True)


if __name__ == "__main__":
    main()
