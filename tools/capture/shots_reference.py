"""Reference pages: the Settings pages the course does not show."""

from __future__ import annotations

import harness as H
from harness import Shot


def settings_pages():
    """One figure per remaining Settings page."""
    root = H.restore("converted")
    win = H.main_window("welcome")
    H.open_project(win, root, "converter")
    from bidsmgr.gui.app_settings import AppSettings
    from bidsmgr.gui.settings_dialog import SettingsDialog
    d = SettingsDialog(AppSettings.load(), win)
    d.resize(900, 760)
    d.show()
    H.pump(settle=40)
    pages = [
        ("settings-bids-version", "BIDS version", "Settings, BIDS version page: the version of the standard "
         "datasets are written and validated against."),
        ("settings-system", "System", "Settings, System page: the processor threads and memory BIDS Manager "
         "detected on this computer."),
        ("settings-classification", "Classification", "Settings, Classification page: how the parameter "
         "classifier names MRI series, the weight of each kind of evidence, and the first of its thresholds."),
        ("settings-validation", "Validation", "Settings, Validation page: the rows read per table, which "
         "findings the Editor shows, and TODO placeholders."),
        ("settings-viewer", "Viewer", "Settings, Viewer page: the crosshair, how images and signals open, "
         "and the 3-D view."),
        ("settings-shortcuts", "Viewer shortcuts", "Settings, Viewer shortcuts page: every key and mouse "
         "gesture of the viewers, each of which can be changed."),
    ]
    short = {"System", "BIDS version", "Validation"}
    for sid, title, alt in pages:
        d.resize(900, 520 if title in short else 760)
        d.show_page(title)
        H.pump(settle=30)
        H.take(Shot(sid, alt, d, allow_elided=("QTableView", "QTreeView", "QTreeWidget", "QTableWidget")))
    d.close()
    win.close()


#: The pages too long for the dialog, at the size of the figure that opens
#: their section on the Settings page (Scan and Scan rules come from chapter 3,
#: Quality control from chapter 13).
SCROLLED = {"Scan": 1040, "Scan rules": 1040, "Classification": 900, "Convert": 900,
            "Quality control": 960, "Viewer": 900}


def _slug(text: str) -> str:
    import re
    return re.sub(r"[^a-z0-9]+", "-", text.split("(")[0].lower()).strip("-")


def _screens(boxes, content: int, view: int, pad: int, shortest: int) -> list:
    """Plan a long page's screens: ``(top, extra height, boxes shown, first box)``.

    ``boxes`` are ``(y, height, title)`` in the page's content. A screen starts
    ``pad`` above a box, so it never opens on the cut-off end of the box
    before it; ``first box`` is the one not yet shown whole that the screen is
    there to show. A box taller than the view gets a taller dialog. The rest
    of the page, once it fits, is one last screen ending with the page,
    started at the earliest box from which it fits so the dialog keeps close
    to its usual height; if it would still be shorter than ``shortest`` view
    pixels, the screen before it grows to the end instead.
    """
    def whole(top, height):
        return [b for b in boxes if b[0] >= top and b[0] + b[1] <= top + height]

    def start(b):
        # ``pad`` above the box, but never on the border of the box above it.
        above = [o[0] + o[1] for o in boxes if o[0] < b[0]]
        return max(0, b[0] - pad, max(above, default=0))

    covered = set(whole(0, view))
    plan = []
    for box in boxes:
        if box in covered:
            continue
        need = max(view, box[1] + 2 * pad)
        top = start(box)
        if top + need <= content:
            shown = whole(top, need)
            plan.append((top, need - view, shown, box))
            covered.update(shown)
            continue
        after = plan[-1][0] if plan else 0
        top = min(t for t in (start(b) for b in boxes)
                  if content - need <= t <= top and (t > after or not plan))
        extra = (content - top) - view
        if view + extra < shortest and plan:
            top, _extra, _shown, box = plan.pop()
            extra = (content - top) - view
        plan.append((top, extra, whole(top, view + extra), box))
        break
    return plan


def settings_scrolled():
    """What a long page shows only when scrolled: one figure per screen.

    The page opens at the top, as its first figure shows it; every group box
    not wholly visible there is shown in a later screen (:func:`_screens`).
    Each screen is named after its first box, and the Settings page puts it
    under that box's heading. No project is opened: the pages do not depend
    on one, and the sample state stays free for the groups that do.
    """
    win = H.main_window("welcome")
    from PyQt6.QtWidgets import QGroupBox, QScrollArea
    from bidsmgr.gui.app_settings import AppSettings
    from bidsmgr.gui.settings_dialog import SettingsDialog
    d = SettingsDialog(AppSettings.load(), win)
    height, pad, shortest = 760, 8, 460
    for title, width in SCROLLED.items():
        d.resize(width, height)
        d.show_page(title)
        d.show()
        H.pump(settle=40)
        page = d._stack.currentWidget()
        area = max((a for a in page.findChildren(QScrollArea) if a.isVisible() and a.widget() is not None),
                   key=lambda a: a.widget().height())
        widgets = sorted((b for b in area.widget().findChildren(QGroupBox)
                          if b.isVisible() and b.parentWidget() is area.widget()), key=lambda b: b.y())
        boxes = [(b.y(), b.height(), b.title()) for b in widgets]
        view, content = area.viewport().height(), area.widget().height()
        plan = _screens(boxes, content, view, pad, shortest)
        if not plan:
            raise H.ShotFailed(f"Settings > {title} no longer scrolls at {width}x{height}: drop it from SCROLLED")
        for top, extra, shown, first in plan:
            d.resize(width, height + extra)
            H.pump(settle=30)
            if area.viewport().height() != view + extra:
                raise H.ShotFailed(f"Settings > {title}: the view did not follow the dialog's height")
            area.verticalScrollBar().setValue(top)
            H.pump(settle=20)
            if area.verticalScrollBar().value() != top:
                raise H.ShotFailed(f"Settings > {title}: could not scroll to {top}")
            names = [b[2] for b in shown]
            sid = f"settings-{_slug(title)}-{_slug(first[2])}"
            listed = ", ".join(names[:-1]) + (" and " if len(names) > 1 else "") + names[-1]
            H.take(Shot(sid, f"Settings, {title} page, scrolled down: {listed}.", d,
                        allow_elided=("QTableView", "QTreeView", "QTreeWidget", "QTableWidget")))
            print(f"  screen {sid} ({width}x{height + extra}): {' | '.join(names)}", flush=True)
    d.close()
    win.close()


GROUPS = {"reference-settings": settings_pages, "reference-settings-scrolled": settings_scrolled}
