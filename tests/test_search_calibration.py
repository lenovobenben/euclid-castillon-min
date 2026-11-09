"""Keep a known constructive positive control for the bounded finish search."""

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from search_one_move_finish import screen


class SearchCalibrationTests(unittest.TestCase):
    def test_known_axis_is_found_after_ten_move_prefix(self):
        report = screen(10)
        lines = [set(hit["points"]) for hit in report["hits"] if hit["op"] == "line"]
        self.assertIn({"H", "J"}, lines)


if __name__ == "__main__":
    unittest.main()
