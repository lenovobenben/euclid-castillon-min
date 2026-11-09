"""Certified Castillon constructions in the Euclid-CCC-Min visual style."""

from __future__ import annotations

import json
import math
from pathlib import Path

import numpy as np
from manim import (
    Circle, Create, Dot, FadeIn, FadeOut, Line, MovingCameraScene,
    Rectangle, Text, UpdateFromAlphaFunc, VGroup, Write,
    DOWN, LEFT, RIGHT, UP, config, linear,
)


FONT = "Noto Sans CJK SC"
BACKGROUND = "#07101F"
FOREGROUND = "#E8F0F7"
MUTED = "#8397A8"
INPUT = "#F45BFF"
GOLD = "#FFC857"
AUXILIARY = "#8AC6D9"
TARGET = "#5DE2A5"
GEOMETRY_SCALE = 2.55
OVERVIEW_WIDTH = 13.5
LABELS = {"Up": "U′", "Vp": "V′", "Sp": "S′"}
LABELS.update({
    f"{letter}{index}": f"{letter}{'₀₁'[index]}"
    for letter in "XYZ" for index in range(2)
})
PHASES = {
    1: "1–7 E · 取得三组对应点",
    8: "8–10 E · 找到轴上两点",
    11: "11 E · 画出不动点轴",
    12: "12–14 E · 恢复第一个三角形",
    15: "15–17 E · 恢复第二个三角形",
}


def logical_to_scene(point):
    return np.array([point[0], point[1], 0.0]) * GEOMETRY_SCALE


def clipped_line(coefficients, bounds):
    """Clip an infinite display line to a rectangle."""
    a, b, c = coefficients
    xmin, xmax, ymin, ymax = bounds
    candidates = []
    if abs(b) > 1e-12:
        for x in (xmin, xmax):
            y = (-a * x - c) / b
            if ymin - 1e-9 <= y <= ymax + 1e-9:
                candidates.append((x, y))
    if abs(a) > 1e-12:
        for y in (ymin, ymax):
            x = (-b * y - c) / a
            if xmin - 1e-9 <= x <= xmax + 1e-9:
                candidates.append((x, y))
    if len(candidates) < 2:
        raise ValueError("line lies outside the viewport")
    start, end = max(
        ((p, q) for p in candidates for q in candidates),
        key=lambda pair: math.dist(*pair),
    )
    if math.dist(start, end) < 1e-9:
        raise ValueError("line only touches a viewport corner")
    return logical_to_scene(start), logical_to_scene(end)


class CastillonConstruction(MovingCameraScene):
    mode = "one"

    def construct(self):
        config.background_color = BACKGROUND
        self.data = json.loads(self.data_path.read_text("utf-8"))
        self.total_moves = self.data["result"]["total"]
        self.play_intro()
        self.setup_construction()
        self.play_construction()
        self.finish_construction()

    @property
    def data_path(self):
        return Path(__file__).with_name(f"geometry_{self.mode}.json")

    def text(self, content, **kwargs):
        return Text(content, font=FONT, color=kwargs.pop("color", FOREGROUND), **kwargs)

    def play_intro(self):
        title = self.text("圆内接三角形的尺规构造", font_size=48, weight="MEDIUM")
        title.move_to(UP * 2.4)
        subtitle = self.text("Cramer–Castillon 问题", font_size=28, color=GOLD)
        subtitle.next_to(title, DOWN, buff=0.3)
        problem = self.text(
            "给定圆、圆心与三个点 A、B、C\n"
            "使三角形三边所在直线分别经过这三个点",
            font_size=26, line_spacing=1.25,
        ).move_to(UP * 0.15)
        count = self.text(
            f"{'一个完整三角形' if self.mode == 'one' else '两个完整三角形'} · {self.total_moves} 条直线",
            font_size=35, color=TARGET,
        ).move_to(DOWN * 1.25)
        rules = self.text(
            "画一条直线计 1 E · 已有对象的交点免费\n"
            "一般位置下的已验证上界",
            font_size=21, color=MUTED, line_spacing=1.2,
        ).move_to(DOWN * 2.3)
        page = VGroup(title, subtitle, problem, count, rules)
        self.play(Write(title), FadeIn(subtitle), run_time=1.0)
        self.play(FadeIn(problem), FadeIn(count), FadeIn(rules), run_time=0.8)
        self.wait(2.5)
        self.play(FadeOut(page), run_time=0.5)

    def point_at(self, name):
        return logical_to_scene(self.data["points"][name]["at"])

    def setup_construction(self):
        self.camera.frame.set(width=OVERVIEW_WIDTH).move_to(np.zeros(3))
        self.lines = {}
        self.point_dots = {}
        self.point_labels = {}
        self.temporary_labels = VGroup()
        self.triangles = VGroup()
        self.screen_strokes = []
        self.screen_markers = []
        self.viewport_key = None
        self.phase_text = "免费输入 · Γ、O、A、B、C"
        self.detail_text = "洋红为输入 · 金色为当前一笔 · 淡蓝为辅助 · 绿色为目标"
        self.current_step = 0
        self.hud = VGroup()
        self.rebuild_hud()
        circle = Circle(radius=GEOMETRY_SCALE, color=INPUT, stroke_width=0.95)
        self.screen_strokes.append([circle, 0.95])
        self.add(self.hud)
        self.play(Create(circle), run_time=1.0)
        for name in ("O", "A", "B", "C"):
            self.reveal_point(name, color=INPUT, permanent=True)
        gamma = self.text("Γ", font_size=22, color=INPUT)
        gamma.move_to(logical_to_scene((0.78, 0.78)))
        self.screen_markers.append([gamma, gamma.get_center().copy(), 1.0])
        self.play(FadeIn(gamma), run_time=0.2)
        self.wait(1.0)

    def rebuild_hud(self):
        self.remove(self.hud)
        frame = self.camera.frame
        scale = frame.width / OVERVIEW_WIDTH
        phase = self.text(self.phase_text, font_size=25, weight="MEDIUM")
        phase.scale(scale).move_to(
            frame.get_corner(UP + LEFT) + RIGHT * (phase.width / 2 + 0.32 * scale)
            + DOWN * (phase.height / 2 + 0.28 * scale)
        )
        counter = self.text(
            f"{self.current_step:02d} / {self.total_moves}", font_size=42, color=GOLD,
        ).scale(scale)
        counter.move_to(
            frame.get_corner(UP + RIGHT) + LEFT * (counter.width / 2 + 0.32 * scale)
            + DOWN * (counter.height / 2 + 0.22 * scale)
        )
        detail = self.text(self.detail_text, font_size=22, line_spacing=1.15).scale(scale)
        detail.move_to(
            frame.get_corner(DOWN + LEFT) + RIGHT * (detail.width / 2 + 0.32 * scale)
            + UP * (detail.height / 2 + 0.30 * scale)
        )
        self.hud = VGroup()
        for label in (phase, counter, detail):
            backdrop = Rectangle(
                width=label.width + 0.24 * scale, height=label.height + 0.18 * scale,
                stroke_width=0, fill_color=BACKGROUND, fill_opacity=0.94,
            ).move_to(label)
            self.hud.add(backdrop, label)
        self.hud.set_z_index(30)
        self.add(self.hud)
        self.hud_frame_width = frame.width
        self.hud_frame_center = frame.get_center().copy()

    def update_mobjects(self, dt):
        super().update_mobjects(dt)
        if not hasattr(self, "screen_strokes"):
            return
        frame = self.camera.frame
        key = (frame.width, *frame.get_center())
        if key == self.viewport_key:
            return
        self.viewport_key = key
        scale = frame.width / OVERVIEW_WIDTH
        for drawable, width in self.screen_strokes:
            drawable.set_stroke(width=width * scale)
        for record in self.screen_markers:
            marker, anchor, old_scale = record
            marker.scale(scale / old_scale, about_point=anchor)
            record[2] = scale
        self.hud.scale(frame.width / self.hud_frame_width, about_point=self.hud_frame_center)
        self.hud.shift(frame.get_center() - self.hud_frame_center)
        self.hud_frame_width = frame.width
        self.hud_frame_center = frame.get_center().copy()

    def move_camera(self, center, width):
        frame = self.camera.frame
        start = frame.get_center().copy()
        end = logical_to_scene(center)
        start_width = frame.width
        zoom = math.log(width / start_width)

        def interpolate(camera_frame, alpha):
            camera_frame.set(width=start_width * math.exp(zoom * alpha))
            camera_frame.move_to(start * (1 - alpha) + end * alpha)

        self.play(UpdateFromAlphaFunc(frame, interpolate), run_time=1.1)

    def adjust_camera(self, event):
        if event["e_move"] == 11:
            j, h = (self.data["points"][name]["at"] for name in ("J", "H"))
            self.move_camera(((j[0] + h[0]) / 2, (j[1] + h[1]) / 2), 4.4)

    def assert_references_visible(self, event):
        frame = self.camera.frame
        for name in event["references"]:
            point = self.point_at(name) - frame.get_center()
            if abs(point[0]) > frame.width * 0.43 or abs(point[1]) > frame.height * 0.36:
                raise ValueError(
                    f"E{event['e_move']} reference {name} is outside the safe viewport"
                )

    def label_direction(self, name):
        special = {"O": DOWN + RIGHT, "A": UP + RIGHT, "B": LEFT, "C": DOWN + RIGHT,
                   "J": DOWN + LEFT, "H": UP + RIGHT}
        point = self.point_at(name)
        return special.get(name, point / max(np.linalg.norm(point), 1e-6))

    def point_label(self, name, color):
        scale = self.camera.frame.width / OVERVIEW_WIDTH
        label = self.text(LABELS.get(name, name), font_size=19, color=color).scale(scale)
        label.next_to(self.point_at(name), self.label_direction(name), buff=0.10 * scale)
        # A dark outline keeps labels readable over the accumulated auxiliary lines.
        label.set_stroke(BACKGROUND, width=2.0 * scale, background=True)
        return label.set_z_index(15)

    def reveal_point(self, name, color=FOREGROUND, permanent=False):
        scale = self.camera.frame.width / OVERVIEW_WIDTH
        dot = Dot(self.point_at(name), radius=0.017 * scale, color=color).set_z_index(12)
        label = self.point_label(name, color)
        self.point_dots[name] = dot
        self.screen_markers.append([dot, self.point_at(name), scale])
        if permanent:
            self.point_labels[name] = label
            self.screen_markers.append([label, self.point_at(name), scale])
        else:
            self.temporary_labels.add(label)
        self.play(FadeIn(dot), FadeIn(label), run_time=0.22)

    def show_references(self, event):
        scale = self.camera.frame.width / OVERVIEW_WIDTH
        markers = VGroup()
        for name in event["references"]:
            ring = Circle(radius=0.055 * scale, color=GOLD, stroke_width=0.75 * scale)
            ring.move_to(self.point_at(name))
            markers.add(ring)
            if name not in self.point_labels:
                markers.add(self.point_label(name, GOLD))
        markers.set_z_index(18)
        self.play(FadeIn(markers), run_time=0.25)
        self.wait(0.20)
        return markers

    def make_line(self, event, bounds):
        start, end = clipped_line(event["geometry"], bounds)
        return Line(
            start, end, color=GOLD,
            stroke_width=0.95 * self.camera.frame.width / OVERVIEW_WIDTH,
        ).set_z_index(5)

    def visible_bounds(self):
        frame = self.camera.frame
        x, y = frame.get_center()[:2] / GEOMETRY_SCALE
        dx = frame.width * 0.51 / GEOMETRY_SCALE
        dy = frame.height * 0.51 / GEOMETRY_SCALE
        return x - dx, x + dx, y - dy, y + dy

    def complete_triangle(self, target):
        vertices = target["vertices"]
        triangle = VGroup(*(
            Line(self.point_at(vertices[i]), self.point_at(vertices[(i + 1) % 3]),
                 color=TARGET, stroke_width=1.2).set_z_index(8)
            for i in range(3)
        ))
        self.triangles.add(triangle)
        for edge in triangle:
            self.screen_strokes.append([edge, 1.2])
        # These segments highlight parts of already drawn complete lines.
        self.play(FadeIn(triangle), run_time=0.5)

    def play_construction(self):
        for event in self.data["events"]:
            step = event["e_move"]
            if len(self.temporary_labels):
                self.play(FadeOut(self.temporary_labels), run_time=0.18)
                self.temporary_labels = VGroup()
            self.phase_text = PHASES.get(step, self.phase_text)
            names = "、".join(LABELS.get(name, name) for name in event["references"])
            self.detail_text = f"经过 {names} 画直线"
            self.rebuild_hud()
            self.adjust_camera(event)
            self.assert_references_visible(event)
            references = self.show_references(event)
            visible = self.make_line(event, self.visible_bounds())
            self.current_step = step
            self.rebuild_hud()
            self.play(Create(visible, rate_func=linear), run_time=1.1)
            self.remove(visible)
            full = self.make_line(event, (-4, 4, -4, 4))
            self.lines[event["id"]] = full
            self.add(full)
            self.play(FadeOut(references), run_time=0.2)
            if step == 11:
                self.move_camera((0, 0), OVERVIEW_WIDTH)
            width = 0.4
            self.screen_strokes.append([full, width])
            self.play(full.animate.set_stroke(color=AUXILIARY, width=width, opacity=0.30),
                      run_time=0.25)
            for name in event["new_points"]:
                is_target = any(name in target["vertices"] for target in self.data["targets"])
                self.reveal_point(name, TARGET if is_target else FOREGROUND, permanent=is_target)
            if step == 7:
                self.detail_text = (
                    "依次经过 A、B、C 取另一圆交点，记复合映射为 f\n"
                    "f(U)=U′    f(V)=V′    f(S)=S′"
                )
                self.rebuild_hud()
                self.wait(1.7)
            if step == 11:
                self.detail_text = "JH 为不动点轴 · 与 Γ 的两个交点给出 X₀、X₁"
                self.rebuild_hud()
                self.wait(1.6)
            for target in self.data["targets"]:
                if target["vertices_at"] == step:
                    self.detail_text = f"{step} E · 三个顶点就绪，下一笔补齐第三条边"
                    self.rebuild_hud()
                    self.wait(0.9)
                if target["edges_at"] == step:
                    self.complete_triangle(target)
                    self.detail_text = f"{step} E · {'第一个' if step == 14 else '第二个'}完整三角形"
                    self.rebuild_hud()
                    self.wait(1.1)
            self.wait(0.25)

    def finish_construction(self):
        auxiliaries = VGroup(*self.lines.values())
        for record in self.screen_strokes:
            if record[0] in self.lines.values():
                record[1] = 0.3
        self.play(auxiliaries.animate.set_stroke(width=0.3, opacity=0.055), run_time=0.7)
        hidden = VGroup(*(
            dot for name, dot in self.point_dots.items()
            if name not in self.point_labels
        ))
        self.play(FadeOut(hidden), run_time=0.3)
        self.phase_text = f"{'一个' if self.mode == 'one' else '两个'}完整三角形 · 一般位置"
        self.detail_text = (
            "三个顶点 13 E · 完整三角形 14 E" if self.mode == "one"
            else "第一完整三角形 14 E · 两个完整三角形 17 E"
        )
        self.rebuild_hud()
        self.wait(4.0)


class CastillonOne(CastillonConstruction):
    """One complete triangle, 14 E."""


class CastillonBoth(CastillonConstruction):
    """Both complete triangles, 17 E."""

    mode = "both"
