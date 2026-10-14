"""Publish every rendered master into the site's media folder.

    environments/docs/bin/python tools/capture/publish_all.py            # every shot with both themes
    environments/docs/bin/python tools/capture/publish_all.py ID ...     # only these

Reads ``/private/tmp/bm_docs/png/<id>-<theme>.png`` and the matching JSON the
harness wrote, checks the two themes agree (size and hotspot positions), and
writes AVIF at 1x and 2x (and 3x for close-ups) with a WebP fallback, plus the
record ``media/<id>.json``. A manifest lists every asset with its source.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from publish import MEDIA, publish_still  # noqa: E402

PNG = Path("/private/tmp/bm_docs/png")
SOURCE = PNG / "source.json"


def main(argv=None) -> int:
    ids = sys.argv[1:] if argv is None else argv
    metas = {}
    for p in sorted(PNG.glob("*-dark.json")):
        sid = p.name[:-len("-dark.json")]
        if ids and sid not in ids:
            continue
        light = PNG / f"{sid}-light.json"
        if not light.exists() or not (PNG / f"{sid}-dark.png").exists() or not (PNG / f"{sid}-light.png").exists():
            print(f"  skipped {sid}: one theme is missing")
            continue
        metas[sid] = (json.loads(p.read_text()), json.loads(light.read_text()))
    source = json.loads(SOURCE.read_text()) if SOURCE.exists() else {}
    manifest_path = MEDIA / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {"assets": {}}
    for sid, (dark, light) in metas.items():
        if dark["size"] != light["size"]:
            print(f"  WARNING {sid}: the themes differ in size {dark['size']} / {light['size']}")
        for a, b in zip(dark["regions"], light["regions"]):
            if abs(a["x"] - b["x"]) > 0.01 or abs(a["y"] - b["y"]) > 0.01:
                print(f"  WARNING {sid}: hotspot {a['key']} moved between themes")
        rec = publish_still(sid, {"dark": PNG / f"{sid}-dark.png", "light": PNG / f"{sid}-light.png"},
                            scale=dark["scale"], regions=dark["regions"], alt=dark["alt"],
                            window=dark["window"], title=dark["title"], kind=dark.get("kind", "figure"),
                            source=dark.get("source") or source)
        size = sum((MEDIA / n).stat().st_size for t in rec["files"].values() for f in t.values() for n in f.values())
        manifest["assets"][sid] = {"kind": "still", "files": rec["files"], "bytes": size,
                                   "source": rec["source"], "published": time.strftime("%Y-%m-%d")}
        print(f"  published {sid}: {rec['width']}x{rec['height']}, {size // 1024} KB")
    manifest_path.write_text(json.dumps(manifest, indent=1) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
