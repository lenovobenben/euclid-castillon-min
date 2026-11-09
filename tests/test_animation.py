"""Certified animation snapshots, legal references, and display viewports."""

import importlib.util
import json
import tempfile
import unittest

from animations.castillon.export_geometry import MODES, OUTPUT_DIRECTORY, build_export

HAS_MANIM = importlib.util.find_spec("manim") is not None
if HAS_MANIM:
    from manim import tempconfig
    from animations.castillon.castillon_progress import (
        CastillonBoth, CastillonOne, GEOMETRY_SCALE, OVERVIEW_WIDTH, TARGET, clipped_line,
    )


class AnimationDataTests(unittest.TestCase):
    def test_snapshots_match_certified_replay(self):
        for mode in MODES:
            with self.subTest(mode=mode):
                saved = json.loads((OUTPUT_DIRECTORY / f"geometry_{mode}.json").read_text("utf-8"))
                self.assertEqual(saved, build_export(mode))
                self.assertEqual(
                    saved["source"]["certificate"], "experiments/results/secant-seed.json",
                )
                self.assertIn("proper AB secant", saved["result"]["restriction"])

    def test_every_draw_uses_existing_points_and_intersections(self):
        for mode, count in (("one", 12), ("both", 15)):
            with self.subTest(mode=mode):
                data = build_export(mode)
                available = {"Gamma", "O", "A", "B", "C"}
                self.assertEqual(len(data["events"]), count)
                for step, event in enumerate(data["events"], 1):
                    self.assertEqual(event["e_move"], step)
                    self.assertEqual(event["op"], "line")
                    self.assertEqual(len(event["references"]), 2)
                    self.assertNotEqual(*event["references"])
                    self.assertTrue(set(event["references"]) <= available)
                    available.add(event["id"])
                    for name in event["new_points"]:
                        point = data["points"][name]
                        self.assertEqual(point["available_after"], step)
                        self.assertTrue(set(point["parents"]) <= available)
                        self.assertIn("exact", point)
                        if "other_than" in point:
                            self.assertIn(point["other_than"], available)
                        available.add(name)
                self.assertEqual(set(data["points"]) - available, set())
                self.assertEqual(data["result"]["circles"], 0)
                self.assertEqual(data["result"]["duplicate_draws"], 0)

    def test_shared_prefix_and_actual_movie_milestones(self):
        one, both = (build_export(mode) for mode in MODES)
        self.assertEqual(one["events"], both["events"][:12])
        self.assertEqual(len(one["targets"]), 1)
        self.assertEqual(len(both["targets"]), 2)
        self.assertEqual([(t["vertices_at"], t["edges_at"]) for t in both["targets"]],
                         [(11, 12), (14, 15)])
        self.assertEqual(both["events"][8]["new_points"], ["X0", "X1"])
        self.assertEqual(both["events"][0]["references"], ["A", "B"])


@unittest.skipUnless(HAS_MANIM, "requires the Manim rendering environment")
class AnimationViewportTests(unittest.TestCase):
    def test_references_and_final_circle_fit_the_camera(self):
        with tempfile.TemporaryDirectory() as directory, tempconfig({
            "dry_run": True, "progress_bar": "none", "media_dir": directory,
        }):
            for scene_class in (CastillonOne, CastillonBoth):
                with self.subTest(scene=scene_class.__name__):
                    scene = scene_class(skip_animations=True)
                    scene.data = json.loads(scene.data_path.read_text("utf-8"))
                    scene.total_moves = scene.data["result"]["total"]
                    scene.setup_construction()
                    for event in scene.data["events"]:
                        scene.adjust_camera(event)
                        scene.assert_references_visible(event)
                        scene.make_line(event, scene.visible_bounds())
                        if event["e_move"] == 9:
                            scene.move_camera((0, 0), OVERVIEW_WIDTH)
                    self.assertGreater(scene.camera.frame.height / 2, GEOMETRY_SCALE + 0.5)
                    scene.current_step = scene.total_moves
                    scene.finish_construction()
                    for target in scene.data["targets"]:
                        for vertex in target["vertices"]:
                            label = scene.point_label(vertex, TARGET)
                            for backdrop in scene.hud[::2]:
                                horizontal_overlap = (
                                    label.get_left()[0] < backdrop.get_right()[0]
                                    and label.get_right()[0] > backdrop.get_left()[0]
                                )
                                vertical_overlap = (
                                    label.get_bottom()[1] < backdrop.get_top()[1]
                                    and label.get_top()[1] > backdrop.get_bottom()[1]
                                )
                                self.assertFalse(horizontal_overlap and vertical_overlap, vertex)

    def test_infinite_lines_clip_to_the_viewport(self):
        bounds = (-1, 1, -1, 1)
        for coefficients in ((1, 0, 0), (0, 1, 0), (1, 1, 0)):
            start, end = clipped_line(coefficients, bounds)
            self.assertGreater(sum((start - end) ** 2), 0)
            for point in (start, end):
                self.assertLessEqual(max(abs(point[:2])), GEOMETRY_SCALE)
                a, b, c = coefficients
                self.assertAlmostEqual(a * point[0] + b * point[1] + c * GEOMETRY_SCALE, 0)
        with self.assertRaises(ValueError):
            clipped_line((1, 0, 2), bounds)


if __name__ == "__main__":
    unittest.main()
