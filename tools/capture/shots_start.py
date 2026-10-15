"""Start pages and the window itself: Home, the header, the three views."""

from __future__ import annotations

import harness as H
from harness import Region, Shot


def home_window():
    from PyQt6.QtWidgets import QLabel

    """The window on its first launch: the Home view, nothing open yet."""
    win = H.main_window("welcome")
    w = win.welcome
    H.take(Shot(
        "window-home", "BIDS Manager's GUI on first launch, showing the Home view: a card to "
        "create a dataset, a card to open one, links to get started with a menu of sample "
        "datasets, What's new, and the list of recent projects.",
        win, window=True,
        regions=[
            Region("header", "The header: the views, the project, Settings and the theme", win._header, anchor="tl"),
            Region("views", "Home, Converter and Editor", H.find(win._header, name="nav-track")),
            Region("create", "Create a new dataset", H.ancestor(w._create_btn, "welcome-card"), anchor="tl"),
            Region("open", "Open an existing dataset", H.ancestor(w._open_btn, "welcome-card"), anchor="tl"),
            Region("samples", "Download a sample dataset", w._samples_button),
            Region("news", "What's new: this release, and the update notes",
                   H.ancestor(next(l for l in w.findChildren(QLabel)
                                   if l.property("link_url") == "#whats-new"), "welcome-card"),
                   anchor="tl"),
            Region("recent", "Recent projects", H.ancestor(w._recent, "welcome-card"), anchor="tl"),
            Region("settings", "Settings", win._header._settings_btn),
            Region("theme", "Theme", win._header._theme_btn),
            Region("status", "The status bar: messages, the version, Check updates", win.statusBar(), anchor="t"),
        ]))
    win.close()


def header():
    """The header with a project open: the project switcher appears."""
    root = H.restore("scanned")
    win = H.main_window("welcome")
    H.open_project(win, root, "converter")
    hd = win._header
    H.take(Shot(
        "header", "The header of the GUI with a project open: the logo, the Home, Converter and "
        "Editor views, the project switcher, Settings and the theme menu.",
        win, crop_to=hd,
        regions=[
            Region("logo", "The logo: opens About", hd._logo),
            Region("views", "The three views", H.find(hd, name="nav-track")),
            Region("project", "The project switcher", hd._project_btn),
            Region("settings", "Settings", hd._settings_btn),
            Region("theme", "The theme menu", hd._theme_btn),
        ]))
    win.close()


GROUPS = {"home-window": home_window, "header": header}


def projects():
    """Chapter 2: creating the project on Home, and what the window shows after."""
    import shutil
    win = H.main_window("welcome")
    w = win.welcome
    w._name_edit.setText("multimodal_study")
    H.pump(settle=20)
    card = H.ancestor(w._create_btn, "welcome-card")
    H.take(Shot("l02-create", "The Create a new dataset card on Home, with the name multimodal_study and "
                "the location /tmp/studies.", win, crop_to=card, margin=8,
                regions=[Region("name", "Dataset name", w._name_edit, anchor="l"),
                         Region("where", "Where it is created", w._location_edit, anchor="l"),
                         Region("browse", "Browse…", H.button(card, "Browse")),
                         Region("create", "Create dataset", w._create_btn)]))
    root = H.STUDIES_REAL / "multimodal_study"
    if root.exists():
        shutil.rmtree(root)
    w._on_inline_create()
    H.pump(settle=60)
    conv = win.converter
    H.take(Shot("l02-after-create", "The Converter right after the project was created: the project's name "
                "in the header, the BIDS output locked to /tmp/studies/multimodal_study, and the output tree "
                "with the files a new dataset starts with.", win, window=True,
                regions=[Region("switcher", "The project switcher", win._header._project_btn),
                         Region("output", "BIDS output: the project folder", conv._bids_pathbar, anchor="l"),
                         Region("tree", "The new dataset's files", conv._output_pane, anchor="tl"),
                         Region("raw", "Raw input: not chosen yet", conv._raw_pathbar, anchor="l")],
                allow_elided=("QTreeWidget", "QTreeView")))
    # The project menu of the header, opened.
    hd = win._header
    menu = hd._project_menu
    hd._rebuild_project_menu()
    from PyQt6.QtCore import QPoint
    menu.popup(hd._project_btn.mapToGlobal(QPoint(0, hd._project_btn.height() + 4)))
    H.pump(settle=30)
    x, y, ww, hh = H._rect_in(hd, win)
    H.take(Shot("l02-switcher", "The project switcher's menu: the open project with its folder, and the "
                "recent projects to switch to.", win, crop=(0, 0, 820, 260), popups=[menu]))
    menu.hide()


def open_question():
    """Opening a folder that is not a BIDS dataset: the question Home asks."""
    from PyQt6.QtCore import QTimer
    from PyQt6.QtWidgets import QApplication
    win = H.main_window("welcome")
    folder = H.STUDIES / "BIDS_Manager_multimodal_sample_v2"
    got = {}

    def grab():
        box = QApplication.activeModalWidget()
        if box is None:
            QTimer.singleShot(100, grab)
            return
        H.pump(settle=20)
        box.grab().save("/private/tmp/bm_docs/scratch/not_bids_raw.png")
        try:
            H.take(Shot("l02-not-bids", "The question Home asks when the folder you open is not a BIDS dataset: "
                        "view it in the Editor, or make it a project.", box))
            got["ok"] = True
        except H.ShotFailed as exc:
            got["error"] = exc
        box.reject()
    QTimer.singleShot(300, grab)
    win.welcome.open_folder(folder)
    if "error" in got:
        raise got["error"]
    if not got:
        raise H.ShotFailed("l02-not-bids: the question did not appear")


GROUPS.update({"l02-projects": projects, "l02-open-question": open_question})


def first_launch():
    """Start > First launch: the theme menu and Settings > Display."""
    from PyQt6.QtCore import QPoint  # noqa: F401
    win = H.main_window("welcome")
    win._header._open_theme_menu()
    menu = win._header._theme_menu
    H.pump(settle=30)
    x, y, w, h = H._global_rect_in(menu, win)
    right = win.width()
    left = max(0, x - 4)
    H.take(Shot("theme-menu", "The theme menu, opened from the sun or moon button in the header: the "
                "themes in groups, each with its colours, and the current one ticked.",
                win, crop=(left, 0, right - left, min(win.height(), y + h + 16)), popups=[menu]))
    menu.hide()
    from bidsmgr.gui.app_settings import AppSettings
    from bidsmgr.gui.settings_dialog import SettingsDialog
    d = SettingsDialog(AppSettings.load(), win)
    d.resize(900, 760)
    d.show_page("Display")
    d.show()
    H.pump(settle=40)
    H.take(Shot("settings-display", "Settings, Display page: the theme, its appearance (accent, tint, "
                "icons, file colours), the font scale, the Log, the header logo, hidden files in the "
                "Editor tree and saving sidecar edits as you go.", d))
    d.close()
    win.close()


GROUPS.update({"first-launch": first_launch})


def quick_start_measure():
    """The Quick start's path, driven once, and its numbers recorded.

    Create, scan, one subject and one session, the PET dose sheet, convert
    with the default settings. Nothing else: the course does more.
    """
    import json
    import shutil
    import time

    import states as S
    from bidsmgr.gui.recording_meta_dialog import RecordingMetaDialog
    from bidsmgr.metadata.template_plan import blood_conditions, example_paths_for, pair_counts, present_pairs
    from bidsmgr.recording_meta import scaffold_sidecar_path

    S._fresh_sample()
    name = "quick_start"
    root = H.STUDIES_REAL / name
    if root.exists():
        shutil.rmtree(root)
    win = H.main_window("welcome")
    t0 = time.time()
    win.welcome.create_project(H.STUDIES, name)
    H.pump(settle=40)
    S.scan(win)
    conv = win.converter
    m = conv.model()
    df = m.dataframe()
    included = [r for r in range(m.rowCount()) if str(df.iloc[r]["include"]) in ("1", "True", "true")]
    with m.edit_group():
        m.bulk_set(included, "id", S.SUBJECT)
    with m.edit_group():
        m.bulk_set(included, "ses", S.SESSION)
    H.pump(settle=30)
    conv._on_revalidate_clicked()
    H.pump(settle=20)
    df = m.dataframe()
    dlg = RecordingMetaDialog(
        scaffold_sidecar_path(conv._output_tsv), conv._present_datatypes(), conv,
        montage_suggestions=conv._montage_suggestions(), scan_suggestions=conv._scan_suggestions(),
        present_pairs=present_pairs(df), example_paths=example_paths_for(df), pair_counts=pair_counts(df),
        also_ask={("pet", "blood"): blood_conditions(df)}, bids_root=conv._bids_root,
        eyetrack="modality" in df.columns and bool((df["modality"].astype(str) == "eyetrack").any()))
    dlg.show()
    H.pump(settle=30)
    dlg._import_pet_dose(S.SAMPLE / "dose_sheet.csv")
    H.pump(settle=20)
    dlg._on_save()
    H.pump(settle=30)
    conv._model.set_global_spec(conv._load_global_spec())
    names = [str(x) for x in m.dataframe()["bids_name"] if str(x)]
    rc = S.convert(win)
    from bidsmgr.editor.validator import validate
    files = [p for p in root.rglob("*") if p.is_file() and ".bidsmgr" not in p.parts]
    rep = validate(root, strict=False)
    record = {"rc": rc, "files": len(files), "validation": dict(rep.counts), "names": names,
              "seconds": round(time.time() - t0, 1),
              "errors": sorted({i.code for f in rep.files for i in f.issues if i.severity == "error"})
              if hasattr(rep, "files") else []}
    path = H.SITE / "content" / "_measured" / "multimodal.json"
    data = json.loads(path.read_text())
    data["quick_start"] = record
    path.write_text(json.dumps(data, indent=1) + "\n")
    print(json.dumps(record, indent=1))
    win.close()


GROUPS.update({"qs-measure": quick_start_measure})
