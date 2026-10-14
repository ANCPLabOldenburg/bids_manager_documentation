# BIDS Manager documentation

The documentation site of [BIDS Manager](https://github.com/ANCPLabOldenburg/BIDS-Manager),
published at <https://ancplaboldenburg.github.io/bids_manager_documentation/>.

The pages are Markdown, built into a static site by a small Python program.
GitHub Actions builds and deploys it on every push to `main`
(`.github/workflows/pages.yml`); the built site, `_site/`, is not committed.

## Build and preview

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt
.venv/bin/python tools/build.py --serve      # build, serve on http://localhost:8765/, rebuild on change
.venv/bin/python tools/build.py              # build into _site/ and check
.venv/bin/python tools/build.py --release    # also fail on anything unfinished (CI uses this)
```

Every build checks the site: links and anchors, figures and their files, the
order of headings, words the style guide does not use, dashes, local paths,
and every command and option a page names against the application's own
argument parsers. Problems stop the build; warnings are printed.

## Layout

```
content/            the pages: Markdown with front matter, Jinja first, then Markdown
  _measured/        numbers measured on the sample data, quoted by m("...") in a page
  _styleguide/      the style guide (built, not linked from the navigation)
templates/          the page layouts (base, home, doc, redirect, 404)
static/             CSS, JavaScript, fonts, the home page hero, brand files
media/              figures and clips, one record per id (media/<id>.json) and its files
data/               reference tables read from the application (CLI, settings, columns, ...)
site.yml            navigation, download links, redirects from the old site's addresses
tools/build.py      the site builder; tools/sitekit holds its parts
tools/reference/    reads the installed BIDS Manager and writes data/
tools/capture/      renders figures and clips from the real application
tools/hero/         precomputes the home page hero from sample data
tools/review/       photographs built pages in headless Chrome, for review
tools/brand/        the social card's source (render it with headless Chrome)
```

## Regenerating what comes from the application

These need the BIDS Manager environment (`pip install bids-manager` plus
Pillow with AVIF support and ffmpeg) and the sample datasets. They isolate
their Qt settings in a temporary folder and never touch your own.

```bash
PY=path/to/bids-manager-env/bin/python
$PY tools/reference/extract.py                 # data/*.json from the installed version
$PY tools/capture/run.py --states              # the course's sample states
$PY tools/capture/run.py --all                 # every figure and clip, light and dark
$PY tools/capture/publish_all.py               # masters -> media/ (AVIF, WebP, records)
$PY tools/capture/encode.py                    # clips -> media/ (MP4, WebM, posters)
$PY tools/hero/make_hero.py                    # static/hero/
```

Every picture exists in a light and a dark version; the page shows the one
that matches its theme.

## Review

```bash
.venv/bin/python tools/review/shoot.py --all --widths 375 768 1280 1920 \
    --themes light dark --motion both --out /tmp/bm_docs_review
.venv/bin/python tools/review/shoot.py --sheet /tmp/bm_docs_review
```

## Writing

Plain, teaching English. No dashes as punctuation, no emojis, no selling words
(the build lists them). Name what a reader sees in the application exactly as
the application writes it, in bold. Numbers come from a measured run, never
from memory. Pictures show sample data whose licence allows it, and no faces
other than of participants who consented.
