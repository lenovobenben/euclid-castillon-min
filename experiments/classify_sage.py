"""Exact existence/solution-count classification, independently checked by roots.

The theorem is for real inputs. This implementation accepts rational or real
algebraic inputs through Sage AA; it does not use floating-point tolerances.
Classification is a verifier operation, not a zero-cost construction macro.
"""

from sage.all import AA, QQ, PolynomialRing, matrix
import json
from pathlib import Path

if not __debug__:
    raise RuntimeError("exact classification checks require Python assertions enabled")


def dot(p, q):
    return p[0] * q[0] + p[1] * q[1]


def sub(p, q):
    return p[0] - q[0], p[1] - q[1]


def det(p, q):
    return p[0] * q[1] - p[1] * q[0]


def line(p, q):
    return p[1] - q[1], q[0] - p[0], p[0] * q[1] - p[1] * q[0]


def tangent_contacts_on_opposite_line(a, b, c):
    """Count Gamma ∩ polar(a) ∩ line(b,c) for the unit circle."""
    if dot(a, a) < 1:
        return 0
    u, v, w = line(b, c)
    denominator = a[0] * v - a[1] * u
    if denominator != 0:
        x = (v + a[1] * w) / denominator
        y = (-a[0] * w - u) / denominator
        return int(x * x + y * y == 1)
    coincident = a[0] * w + u == 0 and a[1] * w + v == 0
    return 2 if coincident else 0


def normalized(points, origin, radius):
    if (
        isinstance(radius, float)
        or any(isinstance(x, float) for x in origin)
        or any(isinstance(x, float) for p in points for x in p)
    ):
        raise ValueError("use exact rational or real algebraic inputs, not floats")
    radius = AA(radius)
    origin = tuple(map(AA, origin))
    if radius <= 0:
        raise ValueError("radius must be positive")
    raw = [tuple(map(AA, p)) for p in points]
    a, b, c = [tuple((p[i] - origin[i]) / radius for i in range(2)) for p in raw]
    if det(sub(b, a), sub(c, a)) == 0:
        raise ValueError("this profile requires three distinct noncollinear points")
    if any(dot(p, p) == 1 for p in (a, b, c)):
        raise ValueError("this profile excludes given points on Gamma")
    return (a, b, c), radius


def classify(points, origin=(0, 0), radius=1):
    (a, b, c), radius = normalized(points, origin, radius)
    powers = [dot(p, p) - 1 for p in (a, b, c)]
    area2 = det(sub(b, a), sub(c, a))
    k = area2 * area2 + powers[0] * powers[1] * powers[2]
    self_polar = dot(a, b) == 1 and dot(b, c) == 1 and dot(c, a) == 1
    e_parts = [
        tangent_contacts_on_opposite_line(*triple) for triple in [(a, b, c), (b, c, a), (c, a, b)]
    ]
    e = sum(e_parts)
    if self_polar:
        assert k == 0
        count = "infinite"
        candidate_count = "infinite"
    else:
        candidate_count = 0 if k < 0 else 1 if k == 0 else 2
        assert 0 <= e <= candidate_count
        count = candidate_count - e
    return {
        "K": k * radius**6,
        "K_sign": int(k.sign()),
        "self_polar": bool(self_polar),
        "degenerate_by_repeated_edge": e_parts,
        "degenerate_count": e,
        "candidate_count": candidate_count,
        "solution_count": count,
    }


def circle_roots(coefficients):
    a, b, c = coefficients
    norm = a * a + b * b
    delta = norm - c * c
    if delta < 0:
        return []
    if norm == 0:
        raise ValueError("zero line cannot define isolated roots")
    x, y = -a * c / norm, -b * c / norm
    root = delta.sqrt() / norm
    roots = [(x - b * root, y + a * root)]
    if delta > 0:
        roots.append((x + b * root, y - a * root))
    return roots


def other(p, center):
    direction = sub(center, p)
    t = -2 * dot(p, direction) / dot(direction, direction)
    return p[0] + t * direction[0], p[1] + t * direction[1]


def direct_count(points, origin=(0, 0), radius=1):
    """Independent candidate recovery: solve fixed roots and reject coincidences."""
    centers, _ = normalized(points, origin, radius)
    composite = matrix(AA, [[1, 0], [0, 1]])
    for x, y in centers:
        composite = matrix(AA, [[y, x - 1], [x + 1, -y]]) * composite
    scalar = composite[0, 1] == 0 and composite[1, 0] == 0 and composite[0, 0] == composite[1, 1]
    if scalar:
        return "infinite"
    coefficients = (
        -composite[0, 1] - composite[1, 0],
        composite[1, 1] - composite[0, 0],
        composite[1, 0] - composite[0, 1],
    )
    count = 0
    for x in circle_roots(coefficients):
        y = other(x, centers[0])
        z = other(y, centers[1])
        assert other(z, centers[2]) == x
        if x != y and y != z and z != x:
            for center, p, q in zip(centers, (x, y, z), (y, z, x)):
                assert det(sub(center, p), sub(q, p)) == 0
            count += 1
    return count


def symbolic():
    ring = PolynomialRing(QQ, names=("ax", "ay", "bx", "by", "cx", "cy"))
    ax, ay, bx, by, cx, cy = ring.gens()
    a, b, c = (ax, ay), (bx, by), (cx, cy)

    def m(p):
        x, y = p
        return matrix(ring, [[y, x - 1], [x + 1, -y]])

    ma, mb, mc = map(m, (a, b, c))
    composite = mc * mb * ma

    def power(p):
        return dot(p, p) - 1

    area2 = det(sub(b, a), sub(c, a))
    assert composite.trace() == 2 * area2
    assert composite.det() == -power(a) * power(b) * power(c)
    assert composite.trace() ** 2 - 4 * composite.det() == 4 * (
        area2**2 + power(a) * power(b) * power(c)
    )
    polar_ideal = ring.ideal([dot(a, b) - 1, dot(b, c) - 1, dot(c, a) - 1])
    for expression in (composite[0, 1], composite[1, 0], composite[0, 0] - composite[1, 1]):
        assert polar_ideal.reduce(expression) == 0
    # Converse: scalar composite and invertible M_P force every pair polar.
    for p, q, r in [(ma, mb, mc), (mb, mc, ma), (mc, ma, mb)]:
        product = r * q * p
        assert (r * product).trace() == r.det() * (-1) * (q * p).trace()
    return {
        "trace_identity_six_parameters": True,
        "determinant_identity": True,
        "discriminant_identity": True,
        "self_polar_implies_scalar": True,
        "scalar_converse_trace_identities": True,
    }


F = QQ
FIXTURES = [
    ("no_real_fixed_point", [(0, 0), (F(1) / 2, 0), (0, F(1) / 2)], 0, -1, 0),
    (
        "one_proper_double_root",
        [(F(1) / 2, F(1) / 2), (-F(3) / 10, F(1) / 10), (F(1) / 5, -F(2) / 5)],
        1,
        0,
        0,
    ),
    ("two_proper", [(2, 0), (0, 3), (-2, -2)], 2, 1, 0),
    ("two_candidates_one_degenerate", [(1, 1), (2, 0), (0, 0)], 1, 1, 1),
    ("two_candidates_both_degenerate", [(2, 0), (F(1) / 2, 0), (F(1) / 2, 1)], 0, 1, 2),
    ("double_root_degenerate", [(1, 1), (2, 0), (F(1) / 2, 0)], 0, 0, 1),
    (
        "self_polar_infinite",
        [(F(3) / 5, 0), (F(5) / 3, F(4) / 3), (F(5) / 3, -F(4) / 3)],
        "infinite",
        0,
        4,
    ),
]


def report_value(value):
    if isinstance(value, dict):
        return {k: report_value(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [report_value(x) for x in value]
    if isinstance(value, (str, int, bool)):
        return value
    # All fixture report scalars are rational, including transformed K.
    return str(QQ(value))


def main():
    rows = []
    # Reflection, rotation, translation and scaling check coordinate invariance.
    transforms = [
        ("unit", lambda p: p, (0, 0), 1),
        ("scaled_shifted", lambda p: (3 - 2 * p[1], -4 + 2 * p[0]), (3, -4), 2),
        ("reflected_scaled", lambda p: (-5 + 3 * p[0], 7 - 3 * p[1]), (-5, 7), 3),
    ]
    for name, points, expected, k_sign, e in FIXTURES:
        for transform, apply, origin, radius in transforms:
            transformed = [apply(p) for p in points]
            result = classify(transformed, origin, radius)
            assert result["solution_count"] == expected
            assert result["K_sign"] == k_sign
            assert result["degenerate_count"] == e
            assert direct_count(transformed, origin, radius) == expected
            rows.append(
                {
                    "fixture": name,
                    "transform": transform,
                    "points": report_value(transformed),
                    "origin": report_value(origin),
                    "radius": radius,
                    **report_value(result),
                }
            )
    rejected = {}
    for name, points in {
        "collinear": [(0, 0), (F(1) / 3, 0), (F(1) / 2, 0)],
        "point_on_circle": [(1, 0), (0, 0), (0, F(1) / 2)],
    }.items():
        try:
            classify(points)
        except ValueError:
            rejected[name] = True
        else:
            raise AssertionError("invalid input accepted")
    baseline_domain_checks = []
    root = Path(__file__).resolve().parents[1]
    for fixture in json.loads((root / "experiments/results/baseline.json").read_text())["reports"]:
        points = [tuple(QQ(v) for v in p) for p in fixture["input"]]
        result = classify(points)
        assert result["solution_count"] == 2 and result["K_sign"] > 0
        assert result["degenerate_count"] == 0
        baseline_domain_checks.append({"fixture": fixture["fixture"], **report_value(result)})
    print(
        json.dumps(
            {
                "symbolic": symbolic(),
                "exact_examples": rows,
                "cross_checked_examples": len(rows),
                "excluded_inputs_rejected": rejected,
                "baseline_domain_checks": baseline_domain_checks,
            },
            ensure_ascii=False,
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
