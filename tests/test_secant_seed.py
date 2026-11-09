"""Restricted proper-secant construction and its exact certificate."""

import json
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "experiments"))

from replay_secant_seed import build_certificate, secant_prefix


class SecantSeedTests(unittest.TestCase):
    def test_certificate_matches_exact_replay(self):
        saved = json.loads((ROOT / "experiments/results/secant-seed.json").read_text("utf-8"))
        self.assertEqual(saved, build_certificate())

    def test_all_fixture_scores_and_no_duplicate_draws(self):
        expected = {"axis": 9, "one_vertices": 11, "one_edges": 12,
                    "all_vertices": 13, "all_edges": 15}
        for report in build_certificate()["reports"]:
            for target, count in expected.items():
                with self.subTest(fixture=report["fixture"], target=target):
                    self.assertEqual(report["scores"][target], {
                        "lines": count, "circles": 0, "total": count, "duplicate_draws": 0,
                    })

    def test_nonsecant_and_tangent_inputs_are_rejected(self):
        inputs = [((10, 2), (11, 3), (12, 2)), ((2, 1), (3, 1), (0, 0))]
        for points in inputs:
            with self.subTest(points=points), self.assertRaisesRegex(ValueError, "two distinct"):
                secant_prefix(*points)


if __name__ == "__main__":
    unittest.main()
