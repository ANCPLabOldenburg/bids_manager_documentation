"""Turn a rendered PNG master into the site's image files and record.

Runs in either environment (needs Pillow with AVIF and WebP). A shot is
published as AVIF and WebP at 1x and 2x (3x masters also give a 3x), named
with a short hash of their content so a changed picture never hides behind a
browser's cached copy of the old one. The record ``media/<id>.json`` lists the
files per theme and the regions measured on the widgets.
"""

from __future__ import annotations

import hashlib
import json
import re
from pathlib import Path

from PIL import Image

SITE = Path(__file__).resolve().parent.parent.parent
MEDIA = SITE / "media"
AVIF_QUALITY = 62
WEBP_QUALITY = 84


def _hash(path: Path) -> str:
    return hashlib.sha1(path.read_bytes()).hexdigest()[:8]


def publish_still(shot_id: str, masters: dict, *, scale: int, regions: list, alt: str,
                  window: bool = False, title: str = "", kind: str = "figure",
                  source: dict | None = None) -> dict:
    """``masters``: theme -> PNG path (rendered at ``scale`` x the logical size)."""
    MEDIA.mkdir(parents=True, exist_ok=True)
    # Only this figure's own files: another id may start with this one
    # (l04-table and l04-table-after), and its files must stay.
    own = re.compile(re.escape(shot_id) + r"-(dark|light)-(poster-)?(\d+-)?[0-9a-f]{8}\.(avif|webp|mp4|webm)$")
    for old in MEDIA.iterdir():
        if own.match(old.name):
            old.unlink()
    files, size = {}, None
    for theme, png in masters.items():
        im = Image.open(png).convert("RGB")
        w, h = im.width // scale, im.height // scale
        if size and size != (w, h):
            raise ValueError(f"{shot_id}: themes differ in size {size} vs {(w, h)}")
        size = (w, h)
        files[theme] = {"avif": {}, "webp": {}}
        densities = [1, 2] if scale == 2 else [1, 2, 3] if scale == 3 else [1]
        for d in densities:
            px = w * d
            img = im if d == scale else im.resize((px, h * d), Image.LANCZOS)
            # AVIF at every density; WebP, the fallback for browsers without
            # AVIF, at 1x only (the budget: a 2x WebP is the largest file).
            formats = [("avif", "avif", {"quality": AVIF_QUALITY, "speed": 4})]
            if d == 1:
                formats.append(("webp", "webp", {"quality": WEBP_QUALITY, "method": 6}))
            for fmt, ext, kw in formats:
                tmp = MEDIA / f".{shot_id}-{theme}-{px}.{ext}"
                img.save(tmp, fmt.upper(), **kw)
                name = f"{shot_id}-{theme}-{px}-{_hash(tmp)}.{ext}"
                tmp.rename(MEDIA / name)
                files[theme][fmt][str(px)] = name
    rec = {"id": shot_id, "kind": kind, "width": size[0], "height": size[1], "scale": scale,
           "themes": list(masters), "files": files, "regions": regions, "alt": alt,
           "window": window, "title": title, "source": source or {}}
    (MEDIA / f"{shot_id}.json").write_text(json.dumps(rec, indent=1), encoding="utf-8")
    return rec
