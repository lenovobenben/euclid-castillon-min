"""Independent exact replay and symbolic checks for the proper-secant route."""

import json
from pathlib import Path

from sage.all import QQ, PolynomialRing, gcd, matrix, vector

from classify_sage import classify
from verify_sage import negative_controls, replays

if not __debug__:
    raise RuntimeError("exact verification requires Python assertions enabled")


def symbolic():
    ring = PolynomialRing(QQ, names=("u", "v", "a", "b", "cx", "cy"))
    u, v, a, b, cx, cy = ring.gens()

    def primitive(values):
        common = gcd(list(values))
        return vector(ring, [entry // common for entry in values])

    def circle(parameter):
        x, y = parameter
        return primitive((y * y - x * x, 2 * x * y, y * y + x * x))

    def join(first, second):
        return primitive(first.cross_product(second))

    def projection(center):
        x, y, z = center
        return matrix(ring, [[y, x - z], [x + z, -y]])

    up, vp = vector(ring, (u, 1)), vector(ring, (v, 1))
    uc, vc = circle(up), circle(vp)

    def on_chord(t):
        return vector(ring, (
            (1 - t) * uc[0] * vc[2] + t * vc[0] * uc[2],
            (1 - t) * uc[1] * vc[2] + t * vc[1] * uc[2],
            uc[2] * vc[2],
        ))

    ma, mb, mc = (projection(center) for center in (on_chord(a), on_chord(b), (cx, cy, 1)))
    for transform in (ma, mb):
        assert (transform * up)[0] * vp[1] - (transform * up)[1] * vp[0] == 0
        assert (transform * vp)[0] * up[1] - (transform * vp)[1] * up[0] == 0

    w, t = primitive(mc * up), primitive(mc * vp)
    r = primitive(mb * w)
    p = primitive(ma * r)
    composite = mc * mb * ma
    for start, image in ((up, w), (vp, t), (p, up)):
        result = composite * start
        assert result[0] * image[1] - result[1] * image[0] == 0
    uc, vc, wc, tc, pc = map(circle, (up, vp, w, t, p))
    j = join(join(uc, tc), join(vc, wc))
    h = join(join(uc, vc), join(tc, pc))
    axis = join(j, h)
    expected = vector(ring, (
        -composite[0, 1] - composite[1, 0],
        composite[1, 1] - composite[0, 0],
        composite[1, 0] - composite[0, 1],
    ))
    assert expected.dot_product(j) == 0
    assert expected.dot_product(h) == 0
    assert any(entry != 0 for entry in axis)
    assert axis.cross_product(expected) == vector(ring, (0, 0, 0))
    return {
        "coefficient_ring": str(ring),
        "seed_swapped_by_A_and_B": True,
        "three_image_pairs": True,
        "both_axis_witnesses": True,
        "generic_axis_nonzero": True,
        "axis_matches_composite": True,
    }


def domain_counterexample():
    points = ((10, 2), (11, 3), (12, 2))
    result = classify(points)
    assert result["solution_count"] == 2 and result["degenerate_count"] == 0
    for p, q in ((points[0], points[1]), (points[1], points[2]), (points[2], points[0])):
        a, b, c = p[1] - q[1], q[0] - p[0], p[0] * q[1] - p[1] * q[0]
        assert c * c > a * a + b * b
    return {
        "points": points, "K": str(result["K"]), "solution_count": 2,
        "all_three_joining_lines_miss_circle": True,
    }


def main():
    path = Path(__file__).resolve().parent / "results/secant-seed.json"
    print(json.dumps({
        "scope": "generic within the proper-AB-secant subdomain of D2",
        "symbolic": symbolic(),
        "independent_replays": replays(path),
        "negative_controls": negative_controls(path),
        "full_D2_counterexample_to_secant_coverage": domain_counterexample(),
        "global_minimality_proved": False,
        "full_domain_robustness_proved": False,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
