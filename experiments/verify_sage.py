"""Independent Sage verifier and general polynomial identities.

No import from castillon.py. Certificate point coordinates are only used to
select an independently computed intersection, never as new geometric data.
"""

from sage.all import AA, QQ, PolynomialRing, matrix, vector
import json
import hashlib
from copy import deepcopy
from pathlib import Path

if not __debug__:
    raise RuntimeError("exact verification requires Python assertions enabled")


def symbolic():
    ring = PolynomialRing(QQ, names=("a", "bx", "by", "cx", "cy"))
    a, bx, by, cx, cy = ring.gens()

    def m(x, y):
        return matrix(ring, [[y, x - 1], [x + 1, -y]])

    ma, mb, mc = m(a, 0), m(bx, by), m(cx, cy)

    def circle(p):
        u, v = p
        return vector(ring, [v * v - u * u, 2 * u * v, v * v + u * u])

    u = vector(ring, [1, 0])
    v = vector(ring, [0, 1])
    w = mb * u
    vp = mc * w
    r = mb * v
    up = mc * r
    s = ma * w
    sp = mc * u
    composite = mc * mb * ma
    for p, q in [(u, up), (v, vp), (s, sp)]:
        image = composite * p
        assert image[0] * q[1] - image[1] * q[0] == 0
    u, v, s, up, vp, sp = map(circle, (u, v, s, up, vp, sp))
    l8 = u.cross_product(vp)
    l9 = v.cross_product(up)
    l10 = s.cross_product(up)
    l7 = u.cross_product(sp)
    j = l8.cross_product(l9)
    h = l7.cross_product(l10)
    expected = vector(
        ring,
        [
            -composite[0, 1] - composite[1, 0],
            composite[1, 1] - composite[0, 0],
            composite[1, 0] - composite[0, 1],
        ],
    )
    assert expected.dot_product(j) == 0
    assert expected.dot_product(h) == 0
    area2 = (bx - a) * cy - by * (cx - a)
    powers = (a * a - 1) * (bx * bx + by * by - 1) * (cx * cx + cy * cy - 1)
    assert composite.trace() == 2 * area2
    assert composite.det() == -powers
    assert composite.trace() ** 2 - 4 * composite.det() == 4 * (area2**2 + powers)
    # Nonzero cross product means the two witness points are generically distinct.
    constructed = h.cross_product(j)
    assert any(x != 0 for x in constructed)
    assert constructed.cross_product(expected) == vector(ring, [0, 0, 0])
    return {
        "coefficient_ring": str(ring),
        "three_image_pairs": True,
        "both_axis_witnesses": True,
        "generic_axis_nonzero": True,
        "axis_matches_composite": True,
        "trace_determinant_identities": True,
    }


def decode(x):
    if isinstance(x, dict):
        return AA(QQ(x["a"])) + AA(QQ(x["b"])) * AA(QQ(x["sqrt"])).sqrt()
    if isinstance(x, list):
        return tuple(decode(v) for v in x)
    return AA(QQ(x))


def ln(p, q):
    if p == q:
        raise ValueError("equal defining points")
    return (p[1] - q[1], q[0] - p[0], p[0] * q[1] - p[1] * q[0])


def normalize(l):
    pivot = next(v for v in l if v != 0)
    return tuple(v / pivot for v in l)


def ll(l, m):
    d = l[0] * m[1] - m[0] * l[1]
    if d == 0:
        return []
    return [((l[1] * m[2] - m[1] * l[2]) / d, (l[2] * m[0] - m[2] * l[0]) / d)]


def lc(l):
    a, b, c = l
    norm = a * a + b * b
    rem = norm - c * c
    if rem < 0:
        return []
    x, y = -a * c / norm, -b * c / norm
    z = rem.sqrt() / norm
    return (
        [(x - b * z, y + a * z)] if rem == 0 else [(x - b * z, y + a * z), (x + b * z, y - a * z)]
    )


def second(p, center):
    dx, dy = center[0] - p[0], center[1] - p[1]
    t = -2 * (p[0] * dx + p[1] * dy) / (dx * dx + dy * dy)
    return p[0] + t * dx, p[1] + t * dy


def expected_targets(inputs):
    m = matrix(AA, [[1, 0], [0, 1]])
    for x, y in inputs:
        m = matrix(AA, [[y, x - 1], [x + 1, -y]]) * m
    axis = normalize((-m[0, 1] - m[1, 0], m[1, 1] - m[0, 0], m[1, 0] - m[0, 1]))
    roots = lc(axis)
    assert len(roots) == 2
    triangles = []
    for x in roots:
        y = second(x, inputs[0])
        z = second(y, inputs[1])
        assert x != y and y != z and z != x
        assert ln(z, x)[0] * inputs[2][0] + ln(z, x)[1] * inputs[2][1] + ln(z, x)[2] == 0
        triangles.append((x, y, z))
    return axis, triangles


def verify_program(inputs, program, target):
    names = {"O": (AA(0), AA(0)), **dict(zip("ABC", inputs))}
    lines = {}
    objects = []
    closure = list(names.values())
    axis, triangles = expected_targets(inputs)
    hits = {}
    count = duplicates = 0
    for entry in program:
        name = entry["id"]
        assert name not in names and name not in lines
        if entry["op"] == "line":
            p, q = [names[k] for k in entry["points"]]
            l = normalize(ln(p, q))
            count += 1
            assert entry["E"] == count
            duplicate = l in objects
            duplicates += duplicate
            assert entry["duplicate"] == duplicate
            lines[name] = l
            if not duplicate:
                fresh = lc(l)
                for old in objects:
                    fresh.extend(ll(l, old))
                objects.append(l)
                for point in fresh:
                    if point not in closure:
                        closure.append(point)
            vertices = [all(p in closure for p in t) for t in triangles]
            edges = [
                all(normalize(ln(t[i], t[(i + 1) % 3])) in objects for i in range(3))
                for t in triangles
            ]
            checks = {
                "axis": axis in objects,
                "one_vertices": any(vertices),
                "all_vertices": all(vertices),
                "one_edges": any(edges),
                "all_edges": all(edges),
            }
            for key, yes in checks.items():
                if yes and key not in hits:
                    hits[key] = count
        elif entry["op"] == "intersect":
            parents = entry["objects"]
            if "Gamma" in parents:
                candidates = lc(lines[next(k for k in parents if k != "Gamma")])
            else:
                candidates = ll(lines[parents[0]], lines[parents[1]])
            claimed = decode(entry["value"])
            matches = [p for p in candidates if p == claimed]
            assert len(matches) == 1 and matches[0] in closure
            names[name] = matches[0]
        else:
            raise ValueError("unsupported primitive")
    assert target in hits
    return {
        "valid": True,
        "lines": count,
        "circles": 0,
        "total": count,
        "duplicate_draws": duplicates,
        "first_target_e": hits[target],
    }


def replays(path):
    data = json.loads(path.read_text())
    profile_path = path.parents[2] / "profiles/castillon-d2-e-generic-v1.json"
    profile = json.loads(profile_path.read_text())
    assert data["profile_id"] == profile["id"]
    assert data["profile_sha256"] == hashlib.sha256(profile_path.read_bytes()).hexdigest()
    assert data["metric"] == profile["metric"] == "e_move"
    reports = []
    for report in data["reports"]:
        inputs = decode(report["input"])
        results = {}
        for target, program in report["programs"].items():
            result = verify_program(inputs, program, target)
            for key in ("lines", "circles", "total", "duplicate_draws"):
                assert result[key] == report["scores"][target][key]
            results[target] = result
        reports.append({"fixture": report["fixture"], "targets": results})
    return reports


def negative_controls(path):
    fixture = json.loads(path.read_text())["reports"][0]
    inputs = decode(fixture["input"])
    original = fixture["programs"]["one_edges"]
    corruptions = {}
    program = deepcopy(original)
    program[0]["E"] = 99
    corruptions["incorrect_step_number"] = program
    program = deepcopy(original)
    next(x for x in program if x["id"] == "W")["value"] = ["0", "0"]
    corruptions["unconstructed_point"] = program
    program = deepcopy(original)
    program[0]["points"][0] = "not_given"
    corruptions["unknown_defining_point"] = program
    corruptions["missing_final_edge"] = deepcopy(original[:-1])
    result = {}
    for name, program in corruptions.items():
        try:
            verify_program(inputs, program, "one_edges")
        except (AssertionError, ValueError, KeyError):
            result[name] = "rejected"
        else:
            raise AssertionError("negative control accepted: " + name)
    return result


def main():
    root = Path(__file__).resolve().parents[1]
    path = root / "experiments/results/baseline.json"
    report = {
        "symbolic": symbolic(),
        "independent_replays": replays(path),
        "negative_controls": negative_controls(path),
        "global_minimality_proved": False,
        "full_domain_robustness_proved": False,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
