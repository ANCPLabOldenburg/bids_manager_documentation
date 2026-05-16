# BIDS Manager documentation

Static documentation site for
[BIDS Manager](https://github.com/ANCPLabOldenburg/BIDS-Manager).

Hand-written HTML / CSS / JS. No build step. Mirrors the design
pattern of the [INDoS_BrainHack](../INDoS_BrainHack/) site, retinted
for the BIDS Manager brand. The full rebuild plan and the list of
remaining work lives at
`../DOCUMENTATION_PLAN.md`.

## Local preview

The pages load `partials/header.html` and `partials/footer.html`
via `fetch`, so a local HTTP server is required. Opening any
`.html` directly with `file://` triggers a CORS error.

```bash
python3 -m http.server 8000
# open http://localhost:8000/
```

## Structure

```
.
├── .nojekyll                       GitHub Pages serves _underscored paths
├── .gitignore                      .DS_Store, ._*, editor folders, *.heic
├── .github/workflows/pages.yml     Deploys on every push to main
├── README.md                       (this file)
├── index.html                      Landing: six-shot hero collage + features
├── intro.html                      What / why / how, interactive flowchart
├── installation.html               Stub, content TBD
├── tutorial.html                   Stub, Technique-B scenes TBD
├── partials/
│   ├── header.html                 Brand + nav + theme toggle
│   └── footer.html                 ANCP Lab + repo / PyPI / Issues links
├── styles.css                      Design system + collage keyframes
├── script.js                       Partial includes, theme toggle, image swap,
│                                   workflow flowchart, scroll-reveal
└── assets/
    ├── brand/                      logo.png, wordmark.png, app-icon-128 / 256
    ├── screenshots/                16 PNGs: 8 scenes x dark / light variants
    └── workflow/                   workflow.svg
```

## Design system

CSS tokens at the top of `styles.css` mirror the BIDS Manager GUI
palette in `bidsmgr.gui.theme_manager`, so the docs and the app feel
like one product:

| Token       | Dark      | Light     |
|-------------|-----------|-----------|
| `--accent`  | `#58a6ff` | `#0969da` |
| `--purple`  | `#d2a8ff` | `#8250df` |
| `--success` | `#3fb950` | `#1a7f37` |
| `--warning` | `#d29922` | `#9a6700` |
| `--error`   | `#f85149` | `#cf222e` |
| `--teal`    | `#39c5cf` | `#1d7a8c` |

Toggle dark / light via the button in the top right of every page.
The choice persists in `localStorage` under `bidsmgr-docs-theme`.

## Hero animation

`index.html`'s hero is a collage of six screenshots. Each shot runs
its own 18-second opacity cycle, staggered by 3 seconds, so 2-3 shots
are visible at any moment and the set rotates continuously. Pure CSS
keyframes (`@keyframes hero-pulse`); no JS interval.

Each shot also carries a `data-light="..."` attribute. The theme
toggle calls `swapThemedImages()` to flip every such image to its
light variant. The mapping is captured on first call (`img.dataset.dark`)
so the swap is reversible.

Honors `prefers-reduced-motion`: animations stop and shots show at a
flat 0.5 opacity collage.

## Adding a page

1. Copy any existing page as `<your-page>.html`.
2. Body starts with `<div data-include="header"></div>` and ends
   with `<div data-include="footer"></div>`. The chrome is then
   inherited from `partials/`.
3. Add a link in `partials/header.html` so the nav picks it up.

No frameworks. No registry. The `bootDocs()` function in `script.js`
discovers partials, theme toggle, scroll reveal, and the flowchart
on every page automatically.

## Adding a themed screenshot

1. Capture dark + light versions of the GUI scene.
2. Drop into `assets/screenshots/<scene>_dark.png` and
   `assets/screenshots/<scene>_light.png`.
3. Reference with:

   ```html
   <img src="assets/screenshots/<scene>_dark.png"
        data-light="assets/screenshots/<scene>_light.png"
        alt="...">
   ```

   `swapThemedImages()` will swap variants on theme toggle.

PNG (not JPG) is the right format: JPG flattens HEIC's transparent
window-shadow border to white, leaving a visible white margin on
the hero. PNG preserves the alpha so the rounded macOS window
corners blend with whatever sits behind them.

If the source HEICs in `../Assets_temp/` get refreshed, re-run:

```bash
rm -f assets/screenshots/*.png
for src in ../Assets_temp/*.heic; do
  base=$(basename "$src" .heic | tr '[:upper:] ' '[:lower:]-')
  sips -s format png -Z 1600 "$src" --out "assets/screenshots/${base}.png" >/dev/null
done
```

## Deploy (GitHub Pages)

The repo ships `.github/workflows/pages.yml`, which publishes the
static site on every push to `main`. One-time setup in the GitHub
repo settings:

1. Push the repo to GitHub (`git push origin main`).
2. **Settings &rarr; Pages &rarr; Build and deployment &rarr;
   Source = GitHub Actions**.

After that, every push to `main` triggers the workflow; the site
goes live at `https://<owner>.github.io/<repo>/` within ~60 seconds.

`.nojekyll` is included so GitHub Pages serves files / folders whose
names start with `_` correctly (Jekyll would skip them otherwise).

## What is next

See `../DOCUMENTATION_PLAN.md` Section 3 for the full punch list. In
short:

- **`installation.html`** — port the per-OS bootstrap walkthrough
  from `../bids_manager_documentation_v0_backup/book/installation.md`,
  refresh for v1.1.
- **`tutorial.html`** — author the nine Technique-B scenes (scan,
  inspect, override, bulk-edit, convert, open in editor, NIfTI
  inspect, validate). Each scene is a self-contained HTML / CSS / JS
  re-implementation of the active GUI widget.
- Optional follow-ups: per-page right-rail TOC, FAQ, changelog,
  search.

## Legacy

The pre-v1.1 Jupyter Book version of this site lives at
`../bids_manager_documentation_v0_backup/` (sibling folder, full
`.git/` preserved). Read-only reference; do not edit. Its `book/`
content still has useful prose for the installation walkthrough.
