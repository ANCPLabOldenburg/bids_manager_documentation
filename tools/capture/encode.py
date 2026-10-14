"""Encode the recorded clips into the site's videos and posters.

    environments/docs/bin/python tools/capture/encode.py            # every clip with both themes
    environments/docs/bin/python tools/capture/encode.py ID ...     # only these

For each clip (``/private/tmp/bm_docs/frames/<id>-<theme>/``): an H.264 MP4
(yuv420p, BT.709 tagged, CRF 20, fast start, no audio) at twice the displayed
size (at most 2200 px wide), an AV1 WebM kept only where it is smaller, and a
poster (WebP and AVIF) from the frame the clip names. Writes ``media/<id>.json``
in the shape the site's clip component reads.
"""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

import imageio_ffmpeg
from PIL import Image

HERE = Path(__file__).resolve().parent
SITE = HERE.parent.parent
MEDIA = SITE / "media"
FRAMES = Path("/private/tmp/bm_docs/frames")
MAX_W = 2200
CRF = 20


def _hash(p: Path) -> str:
    return hashlib.sha1(p.read_bytes()).hexdigest()[:8]


def _poster_frame(folder: Path, at: float) -> Path:
    lines = (folder / "list.txt").read_text().splitlines()
    t, last = 0.0, None
    pairs = []
    for i in range(0, len(lines) - 1, 2):
        name = lines[i].split("'")[1]
        dur = float(lines[i + 1].split()[1])
        pairs.append((name, t, dur))
        t += dur
    for name, start, dur in pairs:
        last = name
        if start <= at < start + dur:
            return folder / name
    return folder / (last or pairs[-1][0])


def encode_one(clip_id: str) -> dict:
    ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    files, meta = {}, None
    # Only this figure's own files: another id may start with this one
    # (l04-table and l04-table-after), and its files must stay.
    own = re.compile(re.escape(clip_id) + r"-(dark|light)-(poster-)?(\d+-)?[0-9a-f]{8}\.(avif|webp|mp4|webm)$")
    for old in MEDIA.iterdir():
        if own.match(old.name):
            old.unlink()
    for theme in ("dark", "light"):
        folder = FRAMES / f"{clip_id}-{theme}"
        meta = json.loads((folder / "clip.json").read_text())
        w = min(MAX_W, meta["width"] * 2)
        w -= w % 2
        tmp_mp4 = MEDIA / f".{clip_id}-{theme}.mp4"
        vf = f"fps=30,scale={w}:-2:flags=lanczos,format=yuv420p"
        common = ["-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(folder / "list.txt"), "-vf", vf]
        subprocess.run([ffmpeg, *common, "-c:v", "libx264", "-preset", "slow", "-crf", str(CRF),
                        "-tune", "stillimage", "-colorspace", "bt709", "-color_primaries", "bt709",
                        "-color_trc", "bt709", "-color_range", "tv", "-movflags", "+faststart", "-an",
                        str(tmp_mp4)], check=True, cwd=folder)
        mp4 = MEDIA / f"{clip_id}-{theme}-{_hash(tmp_mp4)}.mp4"
        tmp_mp4.rename(mp4)
        entry = {"mp4": mp4.name}
        tmp_webm = MEDIA / f".{clip_id}-{theme}.webm"
        subprocess.run([ffmpeg, *common, "-c:v", "libsvtav1", "-preset", "10", "-crf", "38",
                        "-svtav1-params", "tune=0", "-an", str(tmp_webm)], check=True, cwd=folder)
        if tmp_webm.stat().st_size < mp4.stat().st_size * 0.92:
            webm = MEDIA / f"{clip_id}-{theme}-{_hash(tmp_webm)}.webm"
            tmp_webm.rename(webm)
            entry["webm"] = webm.name
        else:
            tmp_webm.unlink()
        poster_src = _poster_frame(folder, meta.get("poster_at", 0))
        im = Image.open(poster_src).convert("RGB")
        pw = meta["width"]
        im1 = im.resize((pw, round(im.height * pw / im.width)), Image.LANCZOS)
        tmp = MEDIA / f".{clip_id}-{theme}-poster.webp"
        im1.save(tmp, "WEBP", quality=82, method=6)
        poster = MEDIA / f"{clip_id}-{theme}-poster-{_hash(tmp)}.webp"
        tmp.rename(poster)
        entry["poster"] = poster.name
        files[theme] = entry
    rec = {"id": clip_id, "kind": "clip", "width": meta["width"], "height": meta["height"],
           "duration": meta["duration"], "chapters": meta.get("chapters", []), "themes": ["dark", "light"],
           "files": files, "alt": meta["alt"], "source": meta.get("source", {})}
    (MEDIA / f"{clip_id}.json").write_text(json.dumps(rec, indent=1))
    size = sum((MEDIA / n).stat().st_size for t in files.values() for n in t.values())
    print(f"  encoded {clip_id}: {meta['duration']:.1f} s, {size / 1e6:.2f} MB (both themes)")
    manifest_path = MEDIA / "manifest.json"
    manifest = json.loads(manifest_path.read_text()) if manifest_path.exists() else {"assets": {}}
    manifest["assets"][clip_id] = {"kind": "clip", "files": files, "bytes": size, "source": rec["source"],
                                   "published": time.strftime("%Y-%m-%d")}
    manifest_path.write_text(json.dumps(manifest, indent=1) + "\n")
    return rec


def main(argv=None) -> int:
    ids = sys.argv[1:] if argv is None else argv
    found = sorted({p.name.rsplit("-", 1)[0] for p in FRAMES.glob("*-dark") if (p / "clip.json").exists()})
    for cid in found:
        if ids and cid not in ids:
            continue
        if not (FRAMES / f"{cid}-light" / "clip.json").exists():
            print(f"  skipped {cid}: the light theme is missing")
            continue
        encode_one(cid)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
