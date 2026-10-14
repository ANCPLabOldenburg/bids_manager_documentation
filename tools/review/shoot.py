"""Capture pages of the built site in headless Chrome, to look at them.

    environments/docs/bin/python tools/review/shoot.py --out /private/tmp/bm_docs/review/round1 \
        --pages "" learn/03-scanning/ --widths 375 768 1280 1920 --themes light dark --motion both
    environments/docs/bin/python tools/review/shoot.py --all ...       # every page of the site
    environments/docs/bin/python tools/review/shoot.py --sheet DIR     # contact sheet of a folder

Drives Chrome through its DevTools protocol, so any width works (the window
size flag clamps narrow windows) and long pages are captured in slices
(Chrome stops drawing beyond about 16,384 px) and stitched. Lazy images are
made eager first, and every image is waited for. The site is served from
``_site`` on a local port for the duration; nothing leaves the machine.
"""

from __future__ import annotations

import argparse
import base64
import http.server
import io
import json
import subprocess
import tempfile
import threading
import time
import urllib.request
from pathlib import Path

import websocket
from PIL import Image

SITE = Path(__file__).resolve().parent.parent.parent
OUT_SITE = SITE / "_site"
CHROME = "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"
SLICE = 6000


class CDP:
    def __init__(self, ws_url: str) -> None:
        self.ws = websocket.create_connection(ws_url, timeout=120, suppress_origin=True)
        self.n = 0

    def call(self, method: str, **params):
        self.n += 1
        mid = self.n
        self.ws.send(json.dumps({"id": mid, "method": method, "params": params}))
        while True:
            msg = json.loads(self.ws.recv())
            if msg.get("id") == mid:
                if "error" in msg:
                    raise RuntimeError(f"{method}: {msg['error']}")
                return msg.get("result", {})

    def eval(self, expr: str, await_promise: bool = False):
        r = self.call("Runtime.evaluate", expression=expr, awaitPromise=await_promise, returnByValue=True)
        return r.get("result", {}).get("value")


def serve(port: int):
    class H(http.server.SimpleHTTPRequestHandler):
        def __init__(self, *a, **kw):
            super().__init__(*a, directory=str(OUT_SITE), **kw)

        def log_message(self, *a):
            pass
    httpd = http.server.ThreadingHTTPServer(("127.0.0.1", port), H)
    threading.Thread(target=httpd.serve_forever, daemon=True).start()
    return httpd


def launch(port: int):
    profile = tempfile.mkdtemp(prefix="bm_docs_chrome_")
    proc = subprocess.Popen([CHROME, "--headless=new", f"--remote-debugging-port={port}",
                             "--hide-scrollbars", "--no-first-run", "--no-default-browser-check",
                             "--disable-extensions", "--mute-audio", "--use-angle=metal",
                             f"--user-data-dir={profile}", "--password-store=basic",
                             "--use-mock-keychain", "about:blank"],
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for _ in range(100):
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/json/version", timeout=1):
                break
        except Exception:
            time.sleep(0.1)
    req = urllib.request.Request(f"http://127.0.0.1:{port}/json/new?about:blank", method="PUT")
    with urllib.request.urlopen(req) as r:
        target = json.loads(r.read())
    return proc, CDP(target["webSocketDebuggerUrl"])


def shoot(cdp: CDP, url: str, width: int, theme: str, reduce: bool, dpr: float, out: Path,
          height: int = 900, full: bool = True, wait: float = 0.6) -> Path:
    cdp.call("Emulation.setDeviceMetricsOverride", width=width, height=height, deviceScaleFactor=dpr,
             mobile=width < 700)
    cdp.call("Emulation.setEmulatedMedia", features=[
        {"name": "prefers-color-scheme", "value": theme},
        {"name": "prefers-reduced-motion", "value": "reduce" if reduce else "no-preference"}])
    cdp.call("Page.enable")
    cdp.call("Page.navigate", url=url)
    for _ in range(200):
        if cdp.eval("document.readyState") == "complete":
            break
        time.sleep(0.05)
    cdp.eval("document.querySelectorAll('img[loading=lazy]').forEach(i => i.loading = 'eager');"
             "document.querySelectorAll('video[preload=none]').forEach(v => v.preload = 'metadata');")
    # Walk down the page so every image is asked for, then wait for the ones shown.
    cdp.eval("(async () => { for (let y = 0; y < document.documentElement.scrollHeight; y += innerHeight) "
             "{ scrollTo(0, y); await new Promise(r => setTimeout(r, 60)); } scrollTo(0, 0); return 1; })()",
             await_promise=True)
    cdp.eval("Promise.all([...document.images].filter(i => i.offsetParent !== null).map(i => "
             "(i.complete && i.naturalWidth) ? 1 : new Promise(r => {i.addEventListener('load', r); "
             "i.addEventListener('error', r); setTimeout(r, 8000);}))).then(() => document.fonts.ready)"
             ".then(() => 1)", await_promise=True)
    time.sleep(wait)
    if not full:
        data = cdp.call("Page.captureScreenshot", format="png")["data"]
        out.write_bytes(base64.b64decode(data))
        return out
    total = int(cdp.eval("Math.ceil(document.documentElement.scrollHeight)") or height)
    # Let everything below the fold reveal (as a reader scrolling would see it).
    cdp.eval("window.scrollTo(0, document.body.scrollHeight)")
    time.sleep(0.25)
    cdp.eval("window.scrollTo(0, 0)")
    cdp.eval("document.querySelectorAll('.reveal').forEach(e => e.classList.add('is-in'))")
    time.sleep(0.5)
    parts = []
    y = 0
    while y < total:
        h = min(SLICE, total - y)
        data = cdp.call("Page.captureScreenshot", format="png", captureBeyondViewport=True,
                        clip={"x": 0, "y": y, "width": width, "height": h, "scale": 1})["data"]
        parts.append(Image.open(io.BytesIO(base64.b64decode(data))).convert("RGB"))
        y += h
    img = Image.new("RGB", (parts[0].width, sum(p.height for p in parts)))
    yy = 0
    for p in parts:
        img.paste(p, (0, yy))
        yy += p.height
    img.save(out)
    return out


def all_pages() -> list[str]:
    import yaml
    cfg = yaml.safe_load((SITE / "site.yml").read_text())
    pages = [""]
    for sec in cfg["sections"].values():
        pages += sec["pages"]
    return pages


def contact_sheet(folder: Path, out: Path, thumb_w: int = 360, cols: int = 6, max_h: int = 900) -> Path:
    from PIL import ImageDraw
    files = sorted(p for p in folder.glob("*.png") if not p.name.startswith("sheet"))
    thumbs = []
    for f in files:
        im = Image.open(f).convert("RGB")
        scale = thumb_w / im.width
        im = im.resize((thumb_w, max(1, int(im.height * scale))), Image.LANCZOS)
        im = im.crop((0, 0, thumb_w, min(im.height, max_h)))
        thumbs.append((f.stem, im))
    rows = (len(thumbs) + cols - 1) // cols
    cell_h = max_h + 28
    sheet = Image.new("RGB", (cols * (thumb_w + 16) + 16, rows * cell_h + 16), "#888888")
    d = ImageDraw.Draw(sheet)
    for i, (name, im) in enumerate(thumbs):
        x = 16 + (i % cols) * (thumb_w + 16)
        y = 16 + (i // cols) * cell_h
        sheet.paste(im, (x, y + 20))
        d.text((x, y + 4), name[:58], fill="#000000")
    sheet.save(out)
    return out


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--out", type=Path, default=Path("/private/tmp/bm_docs/review/latest"))
    ap.add_argument("--pages", nargs="*", default=None)
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--widths", nargs="*", type=int, default=[1280])
    ap.add_argument("--themes", nargs="*", default=["light", "dark"])
    ap.add_argument("--motion", choices=("reduce", "full", "both"), default="reduce")
    ap.add_argument("--dpr", type=float, default=1.0)
    ap.add_argument("--viewport", action="store_true", help="only the first screen, not the whole page")
    ap.add_argument("--anchor", default="")
    ap.add_argument("--wait", type=float, default=0.6)
    ap.add_argument("--sheet", type=Path, help="make a contact sheet of this folder and stop")
    ap.add_argument("--port", type=int, default=8791)
    args = ap.parse_args(argv)
    if args.sheet:
        print(contact_sheet(args.sheet, args.sheet / "sheet.png"))
        return 0
    pages = all_pages() if args.all else (args.pages if args.pages is not None else [""])
    args.out.mkdir(parents=True, exist_ok=True)
    httpd = serve(args.port)
    proc, cdp = launch(args.port + 1)
    motions = {"reduce": [True], "full": [False], "both": [True, False]}[args.motion]
    try:
        for page in pages:
            for w in args.widths:
                for theme in args.themes:
                    for reduce in motions:
                        name = (page.strip("/").replace("/", "_") or "home")
                        tag = f"{name}{('_' + args.anchor.strip('#')) if args.anchor else ''}_{w}_{theme}_{'rm' if reduce else 'mo'}.png"
                        url = f"http://127.0.0.1:{args.port}/{page}{args.anchor}"
                        shoot(cdp, url, w, theme, reduce, args.dpr, args.out / tag,
                              full=not args.viewport, wait=args.wait)
                        print(args.out / tag)
    finally:
        proc.terminate()
        httpd.shutdown()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
