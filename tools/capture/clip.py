"""Clips: a scripted timeline played on the real widgets, grabbed frame by frame.

Nothing is recorded from a screen. Each action happens at its time (a real
slot call, a real keystroke into a real field), the window is grabbed after
it, and a drawn cursor (a clean arrow, eased movement, a soft ring on each
click) is painted over the picture. A pause is one picture with a long
duration, so a clip costs only the pictures that differ.

    c = Clip("scan-run", win, crop_to=win.converter, alt="...")
    c.move_to(conv._scan_btn); c.click(conv._scan_btn, conv._on_scan_clicked)
    c.wait_until(lambda: ..., label="Scanning"); c.hold(1.5); c.finish()

``encode.py`` (docs environment) turns the pictures into MP4 and WebM.
"""

from __future__ import annotations

import json
import math
import shutil
import time
from pathlib import Path
from typing import Callable, Optional

import harness as H


def _ease(t: float) -> float:
    t = max(0.0, min(1.0, t))
    return 4 * t * t * t if t < 0.5 else 1 - pow(-2 * t + 2, 3) / 2


class Clip:
    def __init__(self, clip_id: str, root, *, crop=None, crop_to=None, margin: int = 0, fps: int = 30,
                 alt: str = "", start=None, sample: str = "multimodal v2", poster_at: float = -1.0,
                 popups: bool = True) -> None:
        from PyQt6.QtCore import QPointF

        self.id = clip_id
        self.root = root
        self.fps = fps
        self.alt = alt
        self.sample = sample
        self.poster_at = poster_at
        self.popups = popups
        self.folder = H.FRAMES / f"{clip_id}-{H.theme()}"
        if self.folder.exists():
            shutil.rmtree(self.folder)
        self.folder.mkdir(parents=True)
        self.items: list[tuple[str, float]] = []
        self.chapters: list[dict] = []
        self.t = 0.0
        shot = H.Shot(clip_id, alt, root, crop=crop, crop_to=crop_to, margin=margin)
        self.crop = H._crop_rect(shot)
        x, y, w, h = self.crop
        self.cursor = QPointF(*(start if start else (x + w * 0.62, y + h * 0.72)))
        self.rings: list[tuple[QPointF, float]] = []  # (where, time it started)
        self.base = None
        self.show_cursor = True
        self._guard_once()

    # -- the picture --------------------------------------------------------
    def _guard_once(self) -> None:
        shot = H.Shot(self.id, self.alt, self.root, crop=self.crop)
        H.guard(shot, self.crop)

    def _popups(self):
        from PyQt6.QtWidgets import QApplication
        win = H._win(self.root)
        out = []
        for w in QApplication.topLevelWidgets():
            if w is win or not w.isVisible():
                continue
            out.append(w)
        return out

    def refresh(self) -> None:
        """Grab the window again (after something changed)."""
        H.pump(settle=4)
        pops = self._popups() if self.popups else []
        H.guard_text([self.root, *pops])
        shot = H.Shot(self.id, self.alt, self.root, popups=pops)
        img = H.grab(shot)
        x, y, w, h = self.crop
        s = H.SCALE
        ratio = img.devicePixelRatio() or s
        if abs(ratio - s) > 0.01:
            # Cropped as if it were SCALE, a 1x grab lands in the corner of a
            # black frame: refuse it rather than encode it.
            raise H.ShotFailed(f"{self.id}: grabbed at {ratio:g}x, not {s}x")
        self.base = img.copy(x * s, y * s, w * s, h * s)
        self.base.setDevicePixelRatio(s)

    def _compose(self):
        from PyQt6.QtCore import QPointF, Qt
        from PyQt6.QtGui import QBrush, QColor, QImage, QPainter, QPainterPath, QPen

        if self.base is None:
            self.refresh()
        img = QImage(self.base)
        img.setDevicePixelRatio(H.SCALE)
        p = QPainter(img)
        p.setRenderHint(QPainter.RenderHint.Antialiasing, True)
        ox, oy = self.crop[0], self.crop[1]
        accent = QColor(H.manager().palette.get("accent", "#58a6ff"))
        for where, t0 in self.rings:
            age = (self.t - t0) / 0.42
            if 0 <= age <= 1:
                r = 7 + 17 * _ease(age)
                c = QColor(accent)
                c.setAlphaF(0.55 * (1 - age))
                p.setPen(QPen(c, 2.2))
                p.setBrush(Qt.BrushStyle.NoBrush)
                p.drawEllipse(QPointF(where.x() - ox, where.y() - oy), r, r)
                fill = QColor(accent)
                fill.setAlphaF(0.18 * (1 - age))
                p.setPen(Qt.PenStyle.NoPen)
                p.setBrush(QBrush(fill))
                p.drawEllipse(QPointF(where.x() - ox, where.y() - oy), r * 0.7, r * 0.7)
        if self.show_cursor:
            cx, cy = self.cursor.x() - ox, self.cursor.y() - oy
            path = QPainterPath()
            pts = [(0, 0), (0, 16.5), (4.1, 12.6), (6.9, 18.9), (9.4, 17.8), (6.7, 11.7), (12.2, 11.7)]
            path.moveTo(cx + pts[0][0], cy + pts[0][1])
            for px, py in pts[1:]:
                path.lineTo(cx + px, cy + py)
            path.closeSubpath()
            shadow = QColor(0, 0, 0, 60)
            p.setPen(Qt.PenStyle.NoPen)
            p.setBrush(shadow)
            p.drawPath(path.translated(0.8, 1.4))
            p.setBrush(QColor("#ffffff"))
            p.setPen(QPen(QColor("#111111"), 1.15))
            p.drawPath(path)
        p.end()
        return img

    def frame(self, seconds: Optional[float] = None) -> None:
        seconds = seconds if seconds is not None else 1.0 / self.fps
        img = self._compose()
        name = f"{len(self.items):05d}.png"
        img.save(str(self.folder / name), "PNG", 95)
        self.items.append((name, seconds))
        self.t += seconds

    # -- the timeline ----------------------------------------------------------
    def chapter(self, title: str) -> None:
        self.chapters.append({"t": round(self.t, 2), "title": title})

    def hold(self, seconds: float) -> None:
        self.refresh()
        self.frame(seconds)

    def _point(self, target, where: str = "c"):
        from PyQt6.QtCore import QPointF
        if isinstance(target, tuple):
            return QPointF(*target)
        same = H._win(target) is H._win(self.root)
        x, y, w, h = H._rect_in(target, self.root) if same else H._global_rect_in(target, self.root)
        fx = {"l": 0.2, "c": 0.5, "r": 0.8}.get(where[-1] if where else "c", 0.5)
        return QPointF(x + w * fx, y + h * 0.5)

    def move_to(self, target, dur: float = 0.65, where: str = "c") -> None:
        start = self.cursor
        end = self._point(target, where)
        n = max(2, int(dur * self.fps))
        dist = math.hypot(end.x() - start.x(), end.y() - start.y())
        # A gentle arc, as a hand moves.
        bend = min(40.0, dist * 0.12)
        for i in range(1, n + 1):
            u = _ease(i / n)
            x = start.x() + (end.x() - start.x()) * u
            y = start.y() + (end.y() - start.y()) * u - math.sin(math.pi * u) * bend * 0.4
            from PyQt6.QtCore import QPointF
            self.cursor = QPointF(x, y)
            self.frame()

    def click(self, target, action: Optional[Callable] = None, *, where: str = "c", move: float = 0.65,
              after: float = 0.35) -> None:
        if move:
            self.move_to(target, move, where)
        self.rings.append((self.cursor, self.t))
        for _ in range(3):
            self.frame()
        if action is not None:
            action()
        H.pump(settle=10)
        self.refresh()
        n = max(1, int(after * self.fps))
        for _ in range(n):
            self.frame()

    def type(self, edit, text: str, cps: float = 14.0, clear: bool = False) -> None:
        if clear:
            edit.clear()
        for ch in text:
            edit.insert(ch) if hasattr(edit, "insert") else edit.setText(edit.text() + ch)
            H.pump(settle=2)
            self.refresh()
            self.frame(1.0 / cps)

    def wait_until(self, cond: Callable[[], bool], timeout: float = 120.0, every: float = 0.25,
                   speed: float = 2.0) -> None:
        """Real waiting, shown faster: each grab stands for ``every`` seconds
        of work, played ``speed`` times faster."""
        t0 = time.time()
        while not cond() and time.time() - t0 < timeout:
            H.wait(every)
            self.refresh()
            self.frame(every / speed)
        H.pump(settle=20)
        self.refresh()

    def do(self, action: Callable, settle: float = 0.2) -> None:
        """Something that happens without the cursor (a result arriving)."""
        action()
        H.pump(settle=10)
        if settle:
            H.wait(settle)
        self.refresh()
        self.frame()

    def finish(self) -> dict:
        if not self.items:
            raise H.ShotFailed(f"{self.id}: no frames")
        lines = []
        for name, seconds in self.items:
            lines += [f"file '{name}'", f"duration {seconds:.4f}"]
        lines.append(f"file '{self.items[-1][0]}'")
        (self.folder / "list.txt").write_text("\n".join(lines) + "\n")
        x, y, w, h = self.crop
        poster = self.poster_at if self.poster_at >= 0 else self.t
        meta = {"id": self.id, "alt": self.alt, "width": w, "height": h, "scale": H.SCALE,
                "duration": round(self.t, 2), "chapters": self.chapters, "poster_at": poster,
                "source": {**H.source_info(), "sample": self.sample}}
        (self.folder / "clip.json").write_text(json.dumps(meta, indent=1))
        print(f"  clip {self.id} [{H.theme()}] {len(self.items)} pictures, {self.t:.1f} s")
        return meta
