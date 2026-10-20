"""Render the site's figures and clips from the real application.

    PY=environments/bids-manager/bin/python
    $PY tools/capture/run.py --states                 # build the course's sample states first
    $PY tools/capture/run.py --list                   # every shot group
    $PY tools/capture/run.py converter home           # these groups, both themes
    $PY tools/capture/run.py --all                    # everything (one process per group and theme)
    $PY tools/capture/run.py converter --theme dark   # one theme
    environments/docs/bin/python tools/capture/publish_all.py   # masters -> media/ (AVIF, WebP, records)
    environments/docs/bin/python tools/capture/encode.py        # clips -> media/ (MP4, WebM, posters)

Each group runs in its own process per theme, so one group's viewer memory or
window state cannot leak into the next group's pictures. A shot that fails a
guard stops its group with the reason; nothing is published from it.
"""

from __future__ import annotations

import argparse
import importlib
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

GROUP_MODULES = ["shots_start", "shots_converter", "shots_metadata", "shots_editor", "shots_viewers",
                 "shots_guides", "shots_tools", "shots_qc", "shots_reference", "shots_home", "clips", "clips_viewers", "clips_tour"]


def groups() -> dict:
    out = {}
    for name in GROUP_MODULES:
        try:
            mod = importlib.import_module(name)
        except ModuleNotFoundError:
            continue
        for gname, fn in getattr(mod, "GROUPS", {}).items():
            out[gname] = (name, fn, getattr(mod, "NATIVE", set()), getattr(mod, "SCALES", {}))
    return out


def run_group(name: str, theme: str) -> int:
    import harness as H
    reg = groups()
    _mod, fn, _native, _scales = reg[name]
    H.app(theme)
    t0 = time.time()
    try:
        fn()
    except H.ShotFailed as exc:
        print(f"FAILED [{theme}] {name}: {exc}", flush=True)
        os._exit(2)
    print(f"[{theme}] {name}: {time.time() - t0:.1f} s", flush=True)
    sys.stdout.flush()
    os._exit(0)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("groups", nargs="*")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--states", action="store_true", help="build the sample states")
    ap.add_argument("--states-after", action="store_true", help="build the states after the conversion only")
    ap.add_argument("--theme", choices=("dark", "light"), default=None)
    ap.add_argument("--child", nargs=2, metavar=("GROUP", "THEME"), help=argparse.SUPPRESS)
    args = ap.parse_args(argv)
    if args.child:
        return run_group(*args.child)
    if args.states or args.states_after:
        import harness as H  # noqa: F401
        import states
        if args.states:
            states.build_all("dark")
        states.build_after("dark")
        sys.stdout.flush()
        os._exit(0)
    reg = groups()
    if args.list:
        for g, (mod, _fn, native, scales) in reg.items():
            print(f"{g:32s} {mod}{'  (native GPU)' if g in native else ''}")
        return 0
    names = list(reg) if args.all else args.groups
    themes = [args.theme] if args.theme else ["dark", "light"]
    failed = []
    for g in names:
        if g not in reg:
            print(f"unknown group {g}")
            failed.append(g)
            continue
        _mod, _fn, native, scales = reg[g]
        env = dict(os.environ)
        if g in native:
            env["BM_NATIVE"] = "1"
            env.pop("QT_QPA_PLATFORM", None)  # set by importing the harness here
        if g in scales:
            env["BM_CAPTURE_SCALE"] = str(scales[g])
        for theme in themes:
            rc = subprocess.call([sys.executable, __file__, "--child", g, theme], env=env)
            if rc != 0:
                failed.append(f"{g} [{theme}]")
    if failed:
        print("FAILED:", ", ".join(failed))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
