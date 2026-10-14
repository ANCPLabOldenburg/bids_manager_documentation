"""Figures and clips, written from what the capture tool measured.

Every shot has a record ``media/<id>.json`` written by ``tools/capture``: its
size, the files per theme, and the regions measured on the real widgets. The
page names the shot; the record decides the markup. A re-shot moves the
hotspot markers with the interface, because they come from the record.
"""

from __future__ import annotations

import html
import json
from pathlib import Path
from typing import Callable, Optional

from .markdown import inline

#: Displayed widths (CSS px) of the column a figure can occupy.
COLUMN = 760
WIDE = 1100


class MediaLibrary:
    def __init__(self, root: Path, link: Callable[[str], str]) -> None:
        self.root = root
        self.link = link
        self.used: set[str] = set()
        self.missing: list[tuple[str, str]] = []

    def record(self, shot_id: str) -> Optional[dict]:
        path = self.root / "media" / f"{shot_id}.json"
        if not path.is_file():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    # -- stills ------------------------------------------------------------
    def figure(self, page: str, shot_id: str, caption: str = "", *, alt: str = "",
               size: str = "", legend=None, hotspots: bool = True, bar: Optional[bool] = None,
               only=None, number: bool = True, focus=None) -> str:
        rec = self.record(shot_id)
        self.used.add(shot_id)
        if rec is None:
            self.missing.append((page, shot_id))
            return (f'<figure class="fig fig--missing" data-shot="{shot_id}"><div class="fig-frame">'
                    f'<p>Missing figure <code>{shot_id}</code></p></div></figure>')
        w, h = rec["width"], rec["height"]
        kind = rec.get("kind", "figure")
        size = size or ("wide" if w > COLUMN + 120 else "")
        display = min(w, WIDE if size == "wide" else COLUMN)
        alt = alt or rec.get("alt", "")
        if bar is None:
            bar = rec.get("window", False)
        regions = [r for r in rec.get("regions", []) if hotspots]
        if only is not None:
            regions = [r for r in regions if r["key"] in only]
        legend = legend or {}
        sizes = (f"(min-width: 1200px) {display}px, min({w}px, 100vw)")
        pictures = []
        for theme in rec["themes"]:
            files = rec["files"][theme]
            sources = []
            for fmt, mime in (("avif", "image/avif"), ("webp", "image/webp")):
                if fmt not in files:
                    continue
                srcset = ", ".join(f'{self.link("/media/" + name)} {px}w'
                                   for px, name in sorted(files[fmt].items(), key=lambda kv: int(kv[0])))
                sources.append(f'<source type="{mime}" srcset="{srcset}" sizes="{sizes}">')
            fallback = files.get("webp") or files.get("avif")
            biggest = max(fallback, key=int)
            pictures.append(
                f'<picture class="theme-{theme}">{"".join(sources)}'
                f'<img src="{self.link("/media/" + fallback[biggest])}" width="{w}" height="{h}" '
                f'alt="{html.escape(alt, quote=True)}" loading="lazy" decoding="async"></picture>')
        markers, items = [], []
        focus = set(focus or [])
        for i, r in enumerate(regions, start=1):
            n = i if number else r.get("n", i)
            label = legend.get(r["key"], r["label"])
            label_html = inline(label)
            short = html.escape(r["label"], quote=True)
            ax, ay = r.get("mx", r["x"]), r.get("my", r["y"])
            markers.append(
                f'<button type="button" class="hs" data-n="{n}" data-key="{r["key"]}" '
                f'data-mx="{ax * 100:.2f}" data-my="{ay * 100:.2f}" '
                f'style="left:clamp(14px,{ax * 100:.3f}%,calc(100% - 14px));top:clamp(14px,{ay * 100:.3f}%,calc(100% - 14px))" '
                f'data-rect="{r["x"]:.5f},{r["y"]:.5f},{r["w"]:.5f},{r["h"]:.5f}" '
                f'aria-label="{n}: {short}"><span>{n}</span></button>')
            items.append(f'<li data-n="{n}" data-key="{r["key"]}"'
                         f'{" class=is-focus" if r["key"] in focus else ""}>'
                         f'<span class="hs-n" aria-hidden="true">{n}</span>'
                         f'<span class="hs-text">{label_html}</span></li>')
        bar_html = ""
        if bar:
            title = html.escape(rec.get("title", "BIDS-Manager"))
            bar_html = (f'<div class="fig-bar" aria-hidden="true"><span class="fig-dots">'
                        f'<i></i><i></i><i></i></span><span class="fig-title">{title}</span></div>')
        cap = ""
        if caption or items:
            legend_html = (f'<ol class="fig-legend">{"".join(items)}</ol>' if items else "")
            cap = (f'<figcaption>{f"<p>{inline(caption)}</p>" if caption else ""}'
                   f'{legend_html}</figcaption>')
        classes = ["fig", f"fig--{kind}"]
        if size:
            classes.append(f"fig--{size}")
        if regions:
            classes.append("has-hotspots")
        return (f'<figure class="{" ".join(classes)}" data-shot="{shot_id}" style="--fig-w:{display}px">'
                f'<div class="fig-frame">{bar_html}<div class="fig-media" style="aspect-ratio:{w}/{h}">'
                f'{"".join(pictures)}'
                f'{"<div class=hs-layer>" + "".join(markers) + "</div>" if markers else ""}'
                f'<button type="button" class="fig-zoom" aria-label="Show at full size">'
                f'<svg viewBox="0 0 16 16" aria-hidden="true"><path d="M9.5 2.5h4v4M6.5 13.5h-4v-4M13.5 2.5'
                f'L9 7M2.5 13.5L7 9"/></svg></button></div></div>{cap}</figure>')

    # -- clips -------------------------------------------------------------
    def clip(self, page: str, clip_id: str, caption: str = "", *, alt: str = "",
             size: str = "", loop: Optional[bool] = None) -> str:
        rec = self.record(clip_id)
        self.used.add(clip_id)
        if rec is None:
            self.missing.append((page, clip_id))
            return (f'<figure class="fig fig--missing" data-shot="{clip_id}"><div class="fig-frame">'
                    f'<p>Missing clip <code>{clip_id}</code></p></div></figure>')
        w, h = rec["width"], rec["height"]
        size = size or ("wide" if w > COLUMN + 120 else "")
        display = min(w, WIDE if size == "wide" else COLUMN)
        duration = float(rec.get("duration", 0))
        if loop is None:
            loop = duration <= 20 and not rec.get("chapters")
        alt = alt or rec.get("alt", "")
        videos = []
        for theme in rec["themes"]:
            files = rec["files"][theme]
            sources = []
            if "webm" in files:
                sources.append(f'<source src="{self.link("/media/" + files["webm"])}" '
                               f'type="video/webm">')
            sources.append(f'<source src="{self.link("/media/" + files["mp4"])}" type="video/mp4">')
            videos.append(
                f'<video class="theme-{theme}" width="{w}" height="{h}" muted playsinline '
                f'preload="none" poster="{self.link("/media/" + files["poster"])}"'
                f'{" data-loop" if loop else ""} aria-label="{html.escape(alt, quote=True)}">'
                f'{"".join(sources)}</video>')
        chapters = rec.get("chapters") or []
        chap_json = html.escape(json.dumps(chapters), quote=True)
        cap = f'<figcaption><p>{inline(caption)}</p></figcaption>' if caption else ""
        classes = ["fig", "fig--clip"]
        if size:
            classes.append(f"fig--{size}")
        return (f'<figure class="{" ".join(classes)}" data-clip="{clip_id}" '
                f'data-duration="{duration:.2f}" data-chapters="{chap_json}" style="--fig-w:{display}px">'
                f'<div class="fig-frame"><div class="fig-media" style="aspect-ratio:{w}/{h}">'
                f'{"".join(videos)}'
                f'<div class="player" hidden><button type="button" class="pl-play" aria-label="Play">'
                f'<svg viewBox="0 0 16 16" aria-hidden="true"><path class="i-play" d="M5 3.5v9l7.5-4.5z"/>'
                f'<path class="i-pause" d="M5 3.5h2v9H5zM9 3.5h2v9H9z"/></svg></button>'
                f'<div class="pl-track" role="slider" tabindex="0" aria-label="Position" '
                f'aria-valuemin="0" aria-valuemax="{duration:.1f}" aria-valuenow="0">'
                f'<div class="pl-fill"></div><div class="pl-marks"></div></div>'
                f'<span class="pl-time">0:00</span>'
                f'<button type="button" class="pl-speed" aria-label="Playback speed">1×</button>'
                f'</div><button type="button" class="pl-big" aria-label="Play the clip">'
                f'<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M8 5.5v13l11-6.5z"/></svg>'
                f'</button></div></div>{cap}</figure>')
