"""Geometric invariants and edge cases for the exact arithmetic kernel."""

import sys
import unittest
from fractions import Fraction as F
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from castillon import circle_meet, line, on_circle, on_line, other, square_root


class ExactGeometryTests(unittest.TestCase):
    def test_quadratic_sign_and_reciprocal(self):
        root = square_root(2)
        self.assertEqual((root - F(3, 2)).sign(), -1)
        self.assertEqual((root - F(7, 5)).sign(), 1)
        self.assertEqual((root - 1) * (root + 1), 1)
        self.assertEqual(1 / (root - 1), root + 1)
        with self.assertRaises(ZeroDivisionError):
            _ = root / (root - root)

    def test_circle_intersection_multiplicity(self):
        self.assertEqual(circle_meet((1, 0, -2)), [])
        self.assertEqual(circle_meet((1, 0, -1)), [(F(1), F(0))])
        roots = circle_meet((1, 0, -F(1, 3)))
        self.assertEqual(len(roots), 2)
        for point in roots:
            self.assertTrue(on_circle(point))
            self.assertTrue(on_line(point, (1, 0, -F(1, 3))))

    def test_projection_is_a_circle_involution(self):
        point = (F(3, 5), F(4, 5))
        for center in [(F(0), F(0)), (F(2), F(3)), (F(1, 5), -F(1, 3))]:
            with self.subTest(center=center):
                image = other(point, center)
                self.assertTrue(on_circle(image))
                self.assertTrue(on_line(image, line(point, center)))
                self.assertEqual(other(image, center), point)

    def test_tangent_is_a_repeated_intersection(self):
        point = (F(1), F(0))
        self.assertEqual(other(point, (F(1), F(1))), point)

    def test_invalid_defining_points_are_rejected(self):
        point = (F(1), F(0))
        with self.assertRaises(ValueError):
            line(point, point)
        with self.assertRaises(ValueError):
            other(point, point)


if __name__ == "__main__":
    unittest.main()
