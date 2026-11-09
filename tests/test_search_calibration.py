"""Keep a known constructive positive control for the bounded finish search."""

import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from search_one_move_finish import screen

HAS_NUMPY = importlib.util.find_spec("numpy") is not None


class SearchCalibrationTests(unittest.TestCase):
    def test_known_axis_is_found_after_ten_move_prefix(self):
        report = screen(10)
        lines = [set(hit["points"]) for hit in report["hits"] if hit["op"] == "line"]
        self.assertIn({"H", "J"}, lines)

    @unittest.skipUnless(HAS_NUMPY, "requires NumPy for the numerical discovery screen")
    def test_secant_screen_finds_axis_and_rejects_duplicate_input_circle(self):
        from castillon import FIXTURES
        from search_secant_mixed import (
            add_object, expected_targets, final_moves, initial_state, validate_finish,
        )

        for name, inputs in FIXTURES.items():
            with self.subTest(fixture=name):
                targets = expected_targets(inputs)
                state = initial_state(inputs, stage=8)
                hits = [hit for hit in final_moves(state, targets)
                        if hit["goal"] == "vertex_axis" and hit["target"] == 0]
                self.assertTrue(hits)
                self.assertTrue(all(validate_finish(state, targets, hit) for hit in hits))
                self.assertIsNone(add_object(initial_state(inputs), {
                    "id": "duplicate", "op": "circle", "points": ["O", "U"],
                }))


if __name__ == "__main__":
    unittest.main()
