"""The capture harness: the real application, driven by real calls, grabbed.

Every figure and clip on the site is a picture of BIDS Manager drawn by
BIDS Manager. This module creates the application the way ``bidsmgr`` does
(``gui.bootstrap.create_application``), at the app's own font scale of 1.15,
in an English locale, with settings isolated from the user's own, the full
colour logo in the header and the update check off. It opens windows,
restores prepared sample states, measures named widgets for the hotspots,
applies the guards that fail a shot, and hands the pictures to ``publish``.

Run through ``tools/capture/run.py``, with the BIDS Manager environment.
"""

from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Optional

HERE = Path(__file__).resolve().parent
SITE = HERE.parent.parent
sys.path.insert(0, str(HERE))

NATIVE = os.environ.get("BM_NATIVE") == "1"
if not NATIVE:
    # A large virtual screen: the default offscreen screen is 800 x 600, and
    # menus and popups are kept inside the screen, so on it they land in the
    # wrong place.
    _cfg = Path("/private/tmp/bm_docs/offscreen.json")
    if not _cfg.exists():
        _cfg.parent.mkdir(parents=True, exist_ok=True)
        _cfg.write_text('{"synchronousWindowSystemEvents": false, "windowFrameMargins": false, '
                        '"screens": [{"name": "Docs", "x": 0, "y": 0, "width": 5200, "height": 3400, '
                        '"logicalDpi": 96, "logicalBaseDpi": 96, "dpr": 1}]}')
    os.environ.setdefault("QT_QPA_PLATFORM", f"offscreen:configfile={_cfg}")
SCALE = int(os.environ.get("BM_CAPTURE_SCALE", "2"))
# On the native platform the screen brings its own device pixel ratio (2 on
# this Mac's display); the pictures are brought to SCALE after the grab.
os.environ["QT_SCALE_FACTOR"] = "1" if NATIVE else str(SCALE)
os.environ["BIDSMGR_NO_UPDATE_CHECK"] = "1"

FONT_SCALE = 1.15
WINDOW = (1440, 900)
EXPECTED_VERSION = "1.5.0"

WORK = Path("/private/tmp/bm_docs")
STUDIES_REAL = WORK / "studies"
STUDIES = Path("/tmp/studies")              # what the figures show (a link to the above)
STATES = WORK / "states"
PNG = WORK / "png"
FRAMES = WORK / "frames"
SETTINGS_ROOT = WORK / "settings" / "capture"

def _private_names() -> list:
    """Names that must never be published: the name of the home folder of the
    account doing the work, and any listed (comma-separated) in the environment
    variable BM_DOCS_PRIVATE_NAMES. Read at run time, so the source that guards
    against them does not publish them either."""
    names = {n.strip() for n in os.environ.get("BM_DOCS_PRIVATE_NAMES", "").split(",") if n.strip()}
    if not os.environ.get("CI"):
        home = Path.home().name
        if len(home) >= 4:
            names.add(home)
    return sorted(names)


_NAMES = "".join("|" + re.escape(n) for n in _private_names())

#: Text that must never appear in a figure.
FORBIDDEN = re.compile(r"/Users/(?!Shared)|/home/[a-z]|C:\\Users|bm_docs|/private/var|"
                       r"/private/tmp|Development/datasets" + _NAMES, re.I)

_app = None
_tm = None
_theme = "dark"


class ShotFailed(Exception):
    pass


# --------------------------------------------------------------------- app
def app(theme: str = "dark"):
    """The QApplication, created once per process for one theme."""
    global _app, _tm, _theme
    if _app is not None:
        return _app
    _theme = theme
    from PyQt6.QtCore import QLocale, QSettings

    settings_dir = SETTINGS_ROOT / f"{os.getpid()}_{theme}"
    shutil.rmtree(settings_dir, ignore_errors=True)
    settings_dir.mkdir(parents=True)
    QSettings.setDefaultFormat(QSettings.Format.IniFormat)
    QSettings.setPath(QSettings.Format.IniFormat, QSettings.Scope.UserScope, str(settings_dir))
    QLocale.setDefault(QLocale(QLocale.Language.English, QLocale.Country.UnitedKingdom))
    import bidsmgr
    if bidsmgr.__version__ != EXPECTED_VERSION:
        raise SystemExit(f"BIDS Manager reports {bidsmgr.__version__}, not {EXPECTED_VERSION}: "
                         "refusing to publish figures of another version")
    from bidsmgr.gui.app_settings import AppSettings

    # The settings every figure is taken with, written before the app reads them.
    from PyQt6.QtCore import QCoreApplication
    QCoreApplication.setOrganizationName("bidsmgr")
    QCoreApplication.setApplicationName("bidsmgr")
    s = AppSettings.load()
    s.header_logo = "app_icon"
    s.font_scale = FONT_SCALE
    s.theme = theme
    s.bids_parent = str(STUDIES)
    s.raw_root = str(STUDIES)
    s.save()
    from bidsmgr.gui.bootstrap import create_application

    _app, _tm = create_application(theme)
    if abs(_tm.font_scale - FONT_SCALE) > 1e-6:
        _tm.set_font_scale(FONT_SCALE)
    from bidsmgr.gui.viz.bridge import ThemeHub
    ThemeHub.instance().publish(_tm.palette, _tm.name)
    return _app


def theme() -> str:
    return _theme


def manager():
    return _tm


def pump(until: Optional[Callable[[], bool]] = None, timeout: float = 30.0, settle: int = 20) -> bool:
    """Process events until ``until()`` holds (or ``timeout`` seconds), then
    ``settle`` more rounds. Without ``until``, only the settle rounds."""
    ok = True
    if until is not None:
        t0 = time.time()
        ok = until()
        while not ok and time.time() - t0 < timeout:
            _app.processEvents()
            time.sleep(0.004)
            ok = until()
    for _ in range(settle):
        _app.processEvents()
    return ok


def wait(seconds: float) -> None:
    t0 = time.time()
    while time.time() - t0 < seconds:
        _app.processEvents()
        time.sleep(0.004)


# ------------------------------------------------------------------ window
def main_window(view: str = "welcome", size=WINDOW):
    from bidsmgr.gui.main_window import MainWindow

    win = MainWindow(_tm)
    if NATIVE:
        # Rendered by the GPU, never mapped on the screen.
        from PyQt6.QtCore import Qt
        win.setAttribute(Qt.WidgetAttribute.WA_DontShowOnScreen, True)
    win.resize(*size)
    win.show()
    pump(settle=30)
    win._apply_active_view(view, persist=False)
    pump(settle=20)
    return win


def open_project(win, root: Path, view: str = "converter"):
    win.welcome.open_project(Path(root))
    pump(settle=40)
    win._apply_active_view(view, persist=False)
    pump(settle=30)


# ------------------------------------------------------------------ states
def restore(state: str, name: str = "multimodal_study") -> Path:
    """Put a prepared sample state in place under /tmp/studies (an APFS clone)."""
    src = STATES / state / name
    if not src.exists():
        raise ShotFailed(f"state {state!r} has not been prepared ({src})")
    dst = STUDIES_REAL / name
    if dst.exists():
        shutil.rmtree(dst)
    subprocess.run(["cp", "-c", "-R", str(src), str(dst)], check=True)
    return STUDIES / name


def snapshot(state: str, name: str = "multimodal_study") -> None:
    src = STUDIES_REAL / name
    dst = STATES / state / name
    if dst.exists():
        shutil.rmtree(dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-c", "-R", str(src), str(dst)], check=True)


# ------------------------------------------------------------------- grabs
#: Text BIDS Manager 1.5.0 itself draws cut short at the 1.15 font scale,
#: whatever the window size: reported in DOCS_2_0_PROGRESS.md, accepted in
#: the pictures rather than hidden.
KNOWN_CUT = ("In file + declared", "findings in", "Click a row to mark it in the plots")


@dataclass
class Region:
    key: str
    label: str
    widget: object = None
    rect: Optional[tuple] = None        # (x, y, w, h) in the root's logical pixels
    anchor: str = "auto"                # where the marker sits: tl, tr, bl, br, c, l, r, t, b, auto
    pad: int = 3


@dataclass
class Shot:
    id: str
    alt: str
    root: object                        # the widget grabbed
    regions: list = field(default_factory=list)
    crop: Optional[tuple] = None        # (x, y, w, h) logical, within root
    crop_to: object = None              # a widget: crop to its rectangle (plus margin)
    margin: int = 0
    popups: list = field(default_factory=list)   # extra top-level widgets composited at their place
    window: bool = False                # draw a title bar around it on the page
    title: str = "BIDS-Manager"
    allow_elided: tuple = ()            # object names or classes whose elision is accepted, with a reason
    allow_cut: tuple = KNOWN_CUT        # texts the application itself cuts short (reported defects)
    expect: list = field(default_factory=list)   # (description, predicate) pairs that must hold
    anatomy_ok: bool = False            # shows an anatomical image of a consented participant
    kind: str = "figure"
    sample: str = "multimodal v2"


def _win(widget):
    """The widget's window (unbound: some widgets have a ``window`` attribute of their own)."""
    from PyQt6.QtWidgets import QWidget
    return QWidget.window(widget)


def _rect_in(widget, root):
    from PyQt6.QtCore import QPoint
    p = widget.mapTo(root, QPoint(0, 0)) if widget is not root else QPoint(0, 0)
    return (p.x(), p.y(), widget.width(), widget.height())


def _global_rect_in(widget, root):
    from PyQt6.QtCore import QPoint
    g = widget.mapToGlobal(QPoint(0, 0))
    r = root.mapToGlobal(QPoint(0, 0))
    return (g.x() - r.x(), g.y() - r.y(), widget.width(), widget.height())


def grab(shot: Shot):
    """The root drawn with its popups in place, as a QImage at SCALE."""
    from PyQt6.QtGui import QImage, QPainter

    root = shot.root
    base = root.grab().toImage()
    if not shot.popups:
        return base
    img = QImage(base)
    painter = QPainter(img)
    painter.setRenderHint(QPainter.RenderHint.Antialiasing, True)
    from PyQt6.QtCore import QRectF, Qt
    from PyQt6.QtGui import QColor, QPen
    from PyQt6.QtWidgets import QDialog
    for pop in shot.popups:
        if pop is None or not pop.isVisible():
            continue
        pix = pop.grab()
        x, y, w, h = _global_rect_in(pop, root)
        if isinstance(pop, QDialog):
            # A window floats over the window it belongs to: a soft shadow and
            # a hairline, as the operating system would draw them.
            dark = _tm.is_dark if hasattr(_tm, "is_dark") else True
            for i in range(14, 0, -1):
                c = QColor(0, 0, 0, int((70 if dark else 34) / 14))
                painter.setPen(Qt.PenStyle.NoPen)
                painter.setBrush(c)
                painter.drawRoundedRect(QRectF(x - i, y - i + 6, w + 2 * i, h + 2 * i), 10 + i, 10 + i)
            painter.drawPixmap(x, y, pix)
            painter.setBrush(Qt.BrushStyle.NoBrush)
            painter.setPen(QPen(QColor(_tm.palette.get("border", "#444")), 1))
            painter.drawRect(QRectF(x + 0.5, y + 0.5, w - 1, h - 1))
        else:
            painter.drawPixmap(x, y, pix)
    painter.end()
    return img


def _crop_rect(shot: Shot):
    root = shot.root
    if shot.crop_to is not None:
        x, y, w, h = _rect_in(shot.crop_to, root) if _win(shot.crop_to) is _win(root) \
            else _global_rect_in(shot.crop_to, root)
        m = shot.margin
        x, y = max(0, x - m), max(0, y - m)
        w = min(root.width() - x, w + 2 * m)
        h = min(root.height() - y, h + 2 * m)
        return (x, y, w, h)
    if shot.crop is not None:
        return shot.crop
    return (0, 0, root.width(), root.height())


def measure(shot: Shot, crop) -> list:
    cx, cy, cw, ch = crop
    out = []
    for r in shot.regions:
        if r.widget is not None:
            if not r.widget.isVisible():
                raise ShotFailed(f"{shot.id}: hotspot {r.key!r} is on a hidden widget")
            same = _win(r.widget) is _win(shot.root)
            x, y, w, h = _rect_in(r.widget, shot.root) if same else _global_rect_in(r.widget, shot.root)
        else:
            x, y, w, h = r.rect
        x, y, w, h = x - r.pad, y - r.pad, w + 2 * r.pad, h + 2 * r.pad
        # Clip to the crop.
        x0, y0 = max(x, cx), max(y, cy)
        x1, y1 = min(x + w, cx + cw), min(y + h, cy + ch)
        if x1 - x0 < 4 or y1 - y0 < 4:
            raise ShotFailed(f"{shot.id}: hotspot {r.key!r} falls outside the picture")
        fx, fy, fw, fh = (x0 - cx) / cw, (y0 - cy) / ch, (x1 - x0) / cw, (y1 - y0) / ch
        anchor = r.anchor
        if anchor == "auto":
            anchor = "c" if (x1 - x0) < 220 and (y1 - y0) < 90 else "tl"
        # Large regions: the marker sits on the region's corner, half outside
        # it, so it covers as little of what it points at as possible.
        inset_x, inset_y = 2 / cw, 2 / ch
        mx, my = {
            "c": (fx + fw / 2, fy + fh / 2),
            "tl": (fx + inset_x, fy + inset_y),
            "tr": (fx + fw - inset_x, fy + inset_y),
            "bl": (fx + inset_x, fy + fh - inset_y),
            "br": (fx + fw - inset_x, fy + fh - inset_y),
            "l": (fx + inset_x, fy + fh / 2),
            "r": (fx + fw - inset_x, fy + fh / 2),
            "t": (fx + fw / 2, fy + inset_y),
            "b": (fx + fw / 2, fy + fh - inset_y),
        }[anchor]
        out.append({"key": r.key, "label": r.label, "x": round(fx, 5), "y": round(fy, 5),
                    "w": round(fw, 5), "h": round(fh, 5), "mx": round(mx, 5), "my": round(my, 5)})
    return out


# ------------------------------------------------------------------ guards
def _visible_widgets(roots: Iterable):
    from PyQt6.QtWidgets import QWidget
    for root in roots:
        if root is None:
            continue
        yield root
        for w in root.findChildren(QWidget):
            if w.isVisible():
                yield w


def _texts(widget):
    from PyQt6.QtWidgets import (QAbstractButton, QAbstractItemView, QComboBox, QLabel, QLineEdit,
                                 QPlainTextEdit, QTextEdit)
    if isinstance(widget, QLabel):
        yield widget.text()
    elif isinstance(widget, QAbstractButton):
        yield widget.text()
    elif isinstance(widget, QLineEdit):
        yield widget.text()
        yield widget.placeholderText()
    elif isinstance(widget, QComboBox):
        yield widget.currentText()
    elif isinstance(widget, (QPlainTextEdit, QTextEdit)):
        # What is on screen: a scrolled text shows only part of itself (a
        # conversion log's first line names the folder the package runs from).
        from PyQt6.QtCore import QPoint
        vp = widget.viewport()
        top = widget.cursorForPosition(QPoint(0, 0)).position()
        bottom = widget.cursorForPosition(QPoint(vp.width() - 1, vp.height() - 1)).position()
        yield widget.toPlainText()[top:bottom + 1]
    elif isinstance(widget, QAbstractItemView):
        model = widget.model()
        if model is None:
            return
        from PyQt6.QtCore import QModelIndex, Qt

        def walk(parent, depth=0):
            try:
                rows = min(model.rowCount(parent), 400)
            except TypeError:
                return
            try:
                cols = min(model.columnCount(parent), 80)
            except TypeError:  # a list model keeps columnCount private
                cols = 1
            for r in range(rows):
                for c in range(cols):
                    idx = model.index(r, c, parent)
                    v = model.data(idx, Qt.ItemDataRole.DisplayRole)
                    if v is not None:
                        yield str(v)
                    if c == 0 and depth < 8:
                        try:
                            kids = model.rowCount(idx) > 0
                        except TypeError:
                            kids = False
                        if kids:
                            yield from walk(idx, depth + 1)
        yield from walk(QModelIndex())
    if hasattr(widget, "windowTitle") and widget.isWindow():
        yield widget.windowTitle()


def guard_text(roots) -> None:
    """Only the personal-path check, for every picture of a clip."""
    for w in _visible_widgets(roots):
        for text in _texts(w):
            if text and FORBIDDEN.search(text):
                raise ShotFailed(f"personal or internal path in {type(w).__name__} {w.objectName()!r}: "
                                 f"{FORBIDDEN.search(text).group(0)!r} in {text[:120]!r}")


def guard(shot: Shot, crop) -> list:
    """Fail the shot on anything the plan forbids; return warnings."""
    from PyQt6.QtCore import QLocale
    from PyQt6.QtWidgets import QAbstractButton, QLabel

    problems, warnings = [], []
    roots = [shot.root, *shot.popups]
    for w in _visible_widgets(roots):
        for text in _texts(w):
            if text and FORBIDDEN.search(text):
                problems.append(f"personal or internal path in {type(w).__name__} "
                                f"{w.objectName()!r}: {FORBIDDEN.search(text).group(0)!r} in {text[:120]!r}")
    if not QLocale().name().startswith("en"):
        problems.append(f"locale is {QLocale().name()}")
    # The version in the status bar of any main window in the picture.
    win = _win(shot.root)
    labels = [lab for lab in win.findChildren(QLabel) if lab.objectName() == "update-version-label"]
    for lab in labels:
        if lab.isVisible() and lab.text() != f"v{EXPECTED_VERSION}":
            problems.append(f"status bar reports {lab.text()}")
    # The full colour logo in the header.
    header = getattr(win, "_header", None) if type(win).__name__ == "MainWindow" else None
    if header is not None and header.isVisible():
        pix = header._logo.pixmap()
        if pix is None or pix.isNull() or _saturation(pix.toImage()) < 0.15:
            problems.append("the header shows the monochrome mark, not the colour app icon")
    # Text cut short: elided, clipped by its own box, or by the panel it sits in.
    cx, cy, cw, ch = crop
    allowed = set(shot.allow_elided)
    for w in _visible_widgets([shot.root]):
        if _allowed(w, allowed):
            continue
        if _win(w) is not _win(shot.root):
            continue
        x, y, ww, hh = _rect_in(w, shot.root)
        if x >= cx + cw or y >= cy + ch or x + ww <= cx or y + hh <= cy:
            continue
        msg = _cut_short(w)
        if msg and not any(t in msg for t in shot.allow_cut):
            problems.append(msg)
    for desc, pred in shot.expect:
        try:
            ok = pred()
        except Exception as exc:  # noqa: BLE001
            ok, desc = False, f"{desc} ({exc})"
        if not ok:
            problems.append(f"expected: {desc}")
    if problems:
        raise ShotFailed(f"{shot.id}:\n  - " + "\n  - ".join(problems))
    return warnings


def _allowed(w, allowed) -> bool:
    p = w
    while p is not None:
        if p.objectName() in allowed or type(p).__name__ in allowed:
            return True
        p = p.parentWidget()
    return False


def _cut_short(w) -> str:
    """Why ``w`` shows less text than it holds, or ""."""
    from PyQt6.QtGui import QTextDocument
    from PyQt6.QtWidgets import QAbstractButton, QAbstractScrollArea, QComboBox, QLabel, QLineEdit

    label = ""
    # Labels built to elide (a path in a status line, a readout): BIDS
    # Manager shortens them on purpose and shows the whole text on hover.
    if type(w).__name__ in ("ElidedLabel", "CappedLabel", "_Elided"):
        return ""
    if isinstance(w, QLabel) and w.text() and (w.pixmap() is None or w.pixmap().isNull()):
        text = w.text()
        label = text
        if not w.wordWrap():
            if "<" in text and ">" in text:
                doc = QTextDocument()
                doc.setDefaultFont(w.font())
                doc.setDocumentMargin(0)
                doc.setHtml(text)
                need = doc.idealWidth()
            else:
                need = w.fontMetrics().horizontalAdvance(text)
            if type(w).__name__ in ("ElidedLabel", "_Elided", "CappedLabel") or "<" not in text:
                pass
            if need > w.contentsRect().width() + 2:
                return f"label cut short: {_plain(text)!r} needs {need:.0f}px, has {w.contentsRect().width()}px"
        if re_elided(text):
            return f"elided label: {_plain(text)!r}"
    elif isinstance(w, QLineEdit) and w.text():
        need = w.fontMetrics().horizontalAdvance(w.text()) + 14
        # A long value in a field scrolls by nature (slice times, a path);
        # a field a little too narrow for a short value is a sizing fault.
        if w.width() + 1 < need <= w.width() * 1.4:
            return f"field cut short: {w.text()!r} needs {need}px, has {w.width()}px"
        label = w.text()
    elif isinstance(w, QComboBox) and w.currentText():
        need = w.fontMetrics().horizontalAdvance(w.currentText()) + 34
        if need > w.width() + 1:
            return f"dropdown cut short: {w.currentText()!r} needs {need}px, has {w.width()}px"
        label = w.currentText()
    elif isinstance(w, QAbstractButton) and w.text().strip():
        hint = w.sizeHint().width()
        if hint > w.width() + 3:
            return f"button cut short: {w.text()!r} needs {hint}px, has {w.width()}px"
        label = w.text()
    if not label:
        return ""
    # Clipped by a scrolling panel it sits in (a panel narrower than its content).
    p = w.parentWidget()
    while p is not None:
        if isinstance(p, QAbstractScrollArea):
            vp = p.viewport()
            if vp.isAncestorOf(w):
                from PyQt6.QtCore import QPoint
                left = w.mapTo(vp, QPoint(0, 0)).x()
                right = left + w.width()
                bar = p.horizontalScrollBar()
                if (right > vp.width() + 1 or left < -1) and not (bar and bar.isVisible()):
                    return f"clipped by its panel: {_plain(label)[:40]!r} ({left}..{right} of {vp.width()}px)"
            break
        p = p.parentWidget()
    return ""


def _plain(text: str) -> str:
    return re.sub(r"<[^>]+>", "", text)


def re_elided(text: str) -> bool:
    """An ellipsis Qt inserted: one in the middle of a word or a name."""
    plain = _plain(text)
    return bool(re.search(r"\w…\w|…\w", plain)) and not plain.strip().startswith("…")


def _saturation(img) -> float:
    from PyQt6.QtGui import QColor
    total, n = 0.0, 0
    for y in range(0, img.height(), max(1, img.height() // 24)):
        for x in range(0, img.width(), max(1, img.width() // 24)):
            c = QColor(img.pixelColor(x, y))
            if c.alpha() < 128:
                continue
            total += c.hsvSaturationF()
            n += 1
    return total / n if n else 0.0


# ----------------------------------------------------------------- publish
def take(shot: Shot) -> dict:
    """Guard, grab, crop, measure, and save the master for this theme."""
    pump(settle=30)
    crop = _crop_rect(shot)
    guard(shot, crop)
    img = grab(shot)
    x, y, w, h = crop
    ratio = img.devicePixelRatio() or SCALE
    img = img.copy(round(x * ratio), round(y * ratio), round(w * ratio), round(h * ratio))
    if abs(ratio - SCALE) > 0.01:
        from PyQt6.QtCore import Qt
        img = img.scaled(w * SCALE, h * SCALE, Qt.AspectRatioMode.IgnoreAspectRatio,
                         Qt.TransformationMode.SmoothTransformation)
    if img.hasAlphaChannel():
        # A window with a translucent background (a rounded dialog) grabs with
        # holes: flatten it onto the theme's window colour.
        from PyQt6.QtGui import QImage, QPainter
        from PyQt6.QtWidgets import QApplication
        flat = QImage(img.size(), QImage.Format.Format_RGB32)
        flat.setDevicePixelRatio(img.devicePixelRatio())
        flat.fill(QApplication.palette().window().color())
        p = QPainter(flat)
        p.drawImage(0, 0, img)
        p.end()
        img = flat
    PNG.mkdir(parents=True, exist_ok=True)
    out = PNG / f"{shot.id}-{_theme}.png"
    img.save(str(out))
    regions = measure(shot, crop)
    meta = {"id": shot.id, "alt": shot.alt, "regions": regions, "window": shot.window, "title": shot.title,
            "scale": SCALE, "kind": shot.kind, "size": [w, h], "source": {**source_info(), "sample": shot.sample}}
    (PNG / f"{shot.id}-{_theme}.json").write_text(json.dumps(meta, indent=1))
    print(f"  shot {shot.id} [{_theme}] {w}x{h} logical, {len(regions)} hotspots")
    return meta


def source_info() -> dict:
    import bidsmgr
    repo = Path(bidsmgr.__file__).resolve().parent.parent
    try:
        commit = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "--short", "HEAD"], text=True).strip()
        dirty = bool(subprocess.check_output(["git", "-C", str(repo), "status", "--porcelain", "--", "bidsmgr"],
                                             text=True).strip())
    except Exception:  # noqa: BLE001
        commit, dirty = "", False
    return {"bids_manager": bidsmgr.__version__, "commit": commit + ("+changes" if dirty else ""),
            "date": time.strftime("%Y-%m-%d")}


# ------------------------------------------------------------- utilities
def find(root, cls=None, name: str = None, text: str = None):
    """The first visible child matching a class, an object name and/or a text."""
    from PyQt6.QtWidgets import QWidget
    for w in root.findChildren(cls or QWidget):
        if name is not None and w.objectName() != name:
            continue
        if text is not None:
            t = w.text() if hasattr(w, "text") else ""
            if t.strip() != text.strip():
                continue
        return w
    return None


def ancestor(widget, name: str):
    """The nearest ancestor (or the widget itself) with this object name."""
    w = widget
    while w is not None:
        if w.objectName() == name:
            return w
        w = w.parentWidget()
    raise ShotFailed(f"no ancestor named {name!r}")


def find_all(root, cls=None, name: str = None):
    from PyQt6.QtWidgets import QWidget
    return [w for w in root.findChildren(cls or QWidget) if name is None or w.objectName() == name]


def button(root, text: str):
    from PyQt6.QtWidgets import QAbstractButton
    for b in root.findChildren(QAbstractButton):
        if b.text().strip().rstrip("…").rstrip(".") == text.strip().rstrip("…").rstrip("."):
            return b
    raise ShotFailed(f"no button {text!r}")
