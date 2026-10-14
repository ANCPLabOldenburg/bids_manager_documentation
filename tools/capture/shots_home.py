"""The home page's four stages: the whole window at each one."""

from __future__ import annotations

import harness as H
import shots_converter as SC
import shots_editor as SE
import shots_viewers as SV
from harness import Shot


def home_scan():
    win, conv = SC._converter("scanned")
    SC.layout(conv, log=60)
    SC._expand_raw(conv, 1)
    row = SC._row(conv, sequence="ses-pre_T1w")
    SC._properties(conv, row)
    H.take(Shot("home-scan", "The Converter after scanning the multimodal sample: the raw folder on the left, "
                "the structure the scan found, the table of recordings with their proposed BIDS names, and the "
                "properties of the T1w row.", win, window=True,
                allow_elided=("QTreeView", "QTreeWidget", "QTableView")))
    win.close()


def home_curate():
    win, conv = SC._converter("curated")
    conv._filter_pane.set_mode("recordings")
    H.pump(settle=30)
    SC._properties(conv, SC._row(conv, bids_guess_suffix="bold"))
    SC.layout(conv, log=60)
    conv.set_inspection_view("overview", remember=False)
    SC._wait_overview(conv)
    H.take(Shot("home-curate", "The Converter after curation: the Recordings view lists each kind of recording, "
                "and the Overview counts one subject, one session and fifteen recordings, with nothing worth a "
                "look.", win, window=True, allow_elided=("QTreeView", "QTreeWidget", "QTableView")))
    conv.set_inspection_view("table", remember=False)
    win.close()


def home_convert():
    win, conv = SC._converter("described")
    fp = conv._filter_pane
    fp.set_mode("preview")
    SC._wait_preview(conv)
    fp.preview.select_path("sub-001/ses-01/pet/sub-001_ses-01_pet.json")
    H.pump(settle=10)
    SC._wait_preview(conv)
    row = SC._row(conv, bids_guess_suffix="pet")
    SC._properties(conv, row)
    SC.layout(conv, columns=(200, 520, 840), props=370, fold_trees=True, log=60)
    H.take(Shot("home-convert", "The Converter before the conversion: the BIDS preview shows the PET sidecar "
                "the conversion will write, each value coloured by where it comes from, and Properties shows "
                "the PET row.", win, window=True,
                allow_elided=("QTreeView", "QTreeWidget", "QTableView")))
    win.close()


def home_editor():
    win, ed, root, _ = SE._editor("edited")
    SE._expand(ed, 3)
    SE._splitter_sizes(ed, [230, 920, 450])
    v = SV._open_volume(ed, root, SV.BOLD)
    v.run("view.mode", mode="multi")
    v.run("view.graph", value=True)
    v.run("graph.set", scaling="percent", x_axis="seconds", physio=True, qc=False, scope=1)
    v.qstore.flush()
    g = v.presenter.graph
    H.pump(lambda: g._physio_src is not None, timeout=60, settle=30)
    H.wait(0.8)
    H.take(Shot("home-editor", "The Editor on the converted sample: the BIDS tree with its validation marks, "
                "the BOLD run in the viewer with its time course and physiological recordings, and the "
                "Validation panel.", win, window=True,
                allow_elided=("QTreeView", "QTreeWidget", "QTableView")))
    win.close()


GROUPS = {"home-scan": home_scan, "home-curate": home_curate, "home-convert": home_convert,
          "home-editor": home_editor}
