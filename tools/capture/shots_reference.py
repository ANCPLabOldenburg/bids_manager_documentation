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


GROUPS = {"reference-settings": settings_pages}
