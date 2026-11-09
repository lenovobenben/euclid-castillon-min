"""Exact rational/real-quadratic geometry for Castillon E-move experiments.

Only the Python standard library is required. A numerical approximation is
never used to decide equality, incidence, a branch, or a target hit.
"""

from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction as F
from itertools import combinations
from math import isqrt


@dataclass(frozen=True)
class Q:
    a: F
    b: F
    d: F

    def coerce(self, x):
        if isinstance(x, Q):
            if self.d != x.d:
                raise ValueError("different quadratic fields")
            return x
        return Q(F(x), F(0), self.d)

    def __add__(self, x):
        x = self.coerce(x)
        return simplify(Q(self.a + x.a, self.b + x.b, self.d))

    __radd__ = __add__

    def __neg__(self):
        return simplify(Q(-self.a, -self.b, self.d))

    def __sub__(self, x):
        return self + -self.coerce(x)

    def __rsub__(self, x):
        return self.coerce(x) + -self

    def __mul__(self, x):
        x = self.coerce(x)
        return simplify(
            Q(self.a * x.a + self.b * x.b * self.d, self.a * x.b + self.b * x.a, self.d)
        )

    __rmul__ = __mul__

    def __truediv__(self, x):
        x = self.coerce(x)
        denominator = x.a * x.a - x.b * x.b * self.d
        if denominator == 0:
            raise ZeroDivisionError("quadratic division by zero")
        return simplify(
            Q(
                (self.a * x.a - self.b * x.b * self.d) / denominator,
                (self.b * x.a - self.a * x.b) / denominator,
                self.d,
            )
        )

    def __rtruediv__(self, x):
        return self.coerce(x).__truediv__(self)

    def __eq__(self, x):
        if isinstance(x, Q):
            return self.d == x.d and self.a == x.a and self.b == x.b
        return self.b == 0 and self.a == x

    def __bool__(self):
        return self.a != 0 or self.b != 0

    def sign(self):
        if self.a == 0:
            return sign(self.b)
        if self.b == 0 or sign(self.a) == sign(self.b):
            return sign(self.a)
        return sign(self.a) * sign(self.a * self.a - self.b * self.b * self.d)


def simplify(x):
    return x.a if isinstance(x, Q) and x.b == 0 else x


def sign(x):
    return x.sign() if isinstance(x, Q) else (x > 0) - (x < 0)


def square_root(x):
    x = F(x)
    if x < 0:
        raise ValueError("negative square root")
    n, d = isqrt(x.numerator), isqrt(x.denominator)
    if n * n == x.numerator and d * d == x.denominator:
        return F(n, d)
    return Q(F(0), F(1), x)


def sub(p, q):
    return p[0] - q[0], p[1] - q[1]


def dot(p, q):
    return p[0] * q[0] + p[1] * q[1]


def cross(p, q):
    return p[0] * q[1] - p[1] * q[0]


def line(p, q):
    if p == q:
        raise ValueError("a line needs two different points")
    return p[1] - q[1], q[0] - p[0], p[0] * q[1] - p[1] * q[0]


def on_line(p, l):
    return l[0] * p[0] + l[1] * p[1] + l[2] == 0


def on_circle(p):
    return dot(p, p) == 1


def canonical(l):
    pivot = next(x for x in l if x != 0)
    return tuple(x / pivot for x in l)


def meet(l, m):
    denominator = l[0] * m[1] - m[0] * l[1]
    if denominator == 0:
        raise ValueError("no unique finite line intersection")
    return ((l[1] * m[2] - m[1] * l[2]) / denominator, (l[2] * m[0] - m[2] * l[0]) / denominator)


def other(p, center):
    """Other unit-circle intersection of the line through p and center."""
    if not on_circle(p):
        raise ValueError("first argument must be on the unit circle")
    direction = sub(center, p)
    denominator = dot(direction, direction)
    if denominator == 0:
        raise ValueError("point on circle used as projection center")
    t = -2 * dot(p, direction) / denominator
    return p[0] + t * direction[0], p[1] + t * direction[1]


def circle_meet(l):
    """Intersections of a rational line with the unit circle."""
    a, b, c = map(F, l)
    norm = a * a + b * b
    remainder = norm - c * c
    if remainder < 0:
        return []
    x, y = -a * c / norm, -b * c / norm
    root = square_root(remainder) / norm
    p = (x - b * root, y + a * root)
    if remainder == 0:
        return [p]
    return [p, (x + b * root, y - a * root)]


def product(a, b):
    return [[sum(a[i][k] * b[k][j] for k in range(2)) for j in range(2)] for i in range(2)]


def projection(p):
    x, y = p
    return [[y, x - 1], [x + 1, -y]]


def target_axis(a, b, c):
    m = product(projection(c), product(projection(b), projection(a)))
    return canonical((-(m[0][1] + m[1][0]), m[1][1] - m[0][0], m[1][0] - m[0][1]))


def encode(value):
    if isinstance(value, Q):
        return {"a": str(value.a), "b": str(value.b), "sqrt": str(value.d)}
    if isinstance(value, (list, tuple)):
        return [encode(x) for x in value]
    return str(value)


class Replay:
    def __init__(self, a, b, c):
        self.points = {
            "O": (F(0), F(0)),
            "A": tuple(map(F, a)),
            "B": tuple(map(F, b)),
            "C": tuple(map(F, c)),
        }
        self.lines = {}
        self.program = []
        self.axis = target_axis(*[self.points[k] for k in "ABC"])

    def draw(self, name, p, q):
        l = canonical(line(self.points[p], self.points[q]))
        duplicate = l in self.lines.values()
        self.lines[name] = l
        self.program.append(
            {
                "E": 1 + sum(x["op"] == "line" for x in self.program),
                "op": "line",
                "id": name,
                "points": [p, q],
                "duplicate": duplicate,
            }
        )
        return l

    def bind(self, name, p, parents):
        for parent in parents:
            if parent == "Gamma":
                assert on_circle(p)
            else:
                assert on_line(p, self.lines[parent])
        self.points[name] = p
        self.program.append({"op": "intersect", "id": name, "objects": parents, "value": encode(p)})

    @property
    def score(self):
        operations = [x for x in self.program if x["op"] == "line"]
        return {
            "lines": len(operations),
            "circles": 0,
            "total": len(operations),
            "duplicate_draws": sum(x["duplicate"] for x in operations),
        }

    def intersection(self, name, l, m):
        self.bind(name, meet(self.lines[l], self.lines[m]), [l, m])

    def project(self, name, known, center, lname):
        self.draw(lname, known, center)
        self.bind(name, other(self.points[known], self.points[center]), [lname, "Gamma"])

    def closure(self):
        """Rational intersection closure, for bounded prefix searches only."""
        result = dict(self.points)
        for l, m in combinations(self.lines, 2):
            try:
                p = meet(self.lines[l], self.lines[m])
            except ValueError:
                continue
            result.setdefault(f"meet:{l}:{m}", p)
        return result


def prefix(a, b, c):
    """Seven lines; three known input/output pairs for the composite map."""
    r = Replay(a, b, c)
    assert r.points["A"][1] == 0 and r.points["A"][0] > 0
    r.draw("l1", "O", "A")
    r.bind("U", (F(-1), F(0)), ["l1", "Gamma"])
    r.bind("V", (F(1), F(0)), ["l1", "Gamma"])
    r.project("W", "U", "B", "l2")
    r.project("Vp", "W", "C", "l3")
    r.project("R", "V", "B", "l4")
    r.project("Up", "R", "C", "l5")
    r.project("S", "W", "A", "l6")
    r.project("Sp", "U", "C", "l7")
    # f(U)=Up, f(V)=Vp, f(S)=Sp, f=I_C I_B I_A.
    for x, y in [("U", "Up"), ("V", "Vp"), ("S", "Sp")]:
        p = r.points[x]
        for key in "ABC":
            p = other(p, r.points[key])
        assert p == r.points[y]
    return r


def baseline(a, b, c):
    r = prefix(a, b, c)
    r.draw("l8", "U", "Vp")
    r.draw("l9", "V", "Up")
    r.intersection("J", "l8", "l9")
    r.draw("l10", "S", "Up")
    r.intersection("H", "l7", "l10")
    r.draw("axis", "J", "H")
    assert r.lines["axis"] == r.axis
    return r


FIXTURES = {
    "outside_1": ((F(7, 3), 0), (-2, F(4, 3)), (F(5, 4), -2)),
    "outside_2": ((F(9, 4), 0), (-F(7, 3), F(6, 5)), (F(4, 3), -F(9, 4))),
    "mixed": ((F(2, 5), 0), (-F(5, 2), F(4, 3)), (F(7, 3), F(6, 5))),
    "inside": ((F(4, 5), 0), (-F(3, 5), F(1, 2)), (-F(2, 5), -F(7, 10))),
}


def finish(r, all_solutions=False, edges=True):
    roots = circle_meet(r.lines["axis"])
    assert len(roots) == 2
    for index, x in enumerate(roots):
        r.bind(f"X{index}", x, ["axis", "Gamma"])
    for index in range(2 if all_solutions else 1):
        xname = f"X{index}"
        r.project(f"Y{index}", xname, "A", f"edge_A_{index}")
        r.project(f"Z{index}", f"Y{index}", "B", f"edge_B_{index}")
        x, y, z = [r.points[f"{key}{index}"] for key in "XYZ"]
        assert len({str(encode(p)) for p in (x, y, z)}) == 3
        assert on_line(r.points["C"], line(z, x))
        if edges:
            r.draw(f"edge_C_{index}", f"Z{index}", xname)
    return r
