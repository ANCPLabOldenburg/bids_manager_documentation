#!/usr/bin/env bash
# Screenshot a page of the local docs site so it can actually be looked at.
#
# Layout problems are invisible to an HTML validator. A label can sit on top of
# a circle, a card can overflow its column, a figure can render at the wrong
# size, and every automated check still passes. This renders the real page in
# the real browser and writes a PNG.
#
#   tools/shoot_page.sh about.html                 # whole page, dark
#   tools/shoot_page.sh about.html '#how-it-works' # jumped to an anchor
#   tools/shoot_page.sh tutorial.html '' 1400 4000 # taller viewport
#
# The server has to be running:
#   python3 -m http.server 8000 --bind 127.0.0.1
#
# Reduced motion is forced on, which is how a meaningful share of readers see
# the site anyway, and it stops the scroll-reveal from hiding content that has
# not been scrolled past.

set -euo pipefail

PAGE="${1:?usage: shoot_page.sh <page.html> [#anchor] [width] [height]}"
ANCHOR="${2:-}"
WIDTH="${3:-1400}"
HEIGHT="${4:-2600}"
OUT="${OUT:-/tmp/docshot_$(basename "$PAGE" .html)${ANCHOR//#/_}.png}"

CHROME="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome"

"$CHROME" --headless=new --disable-gpu --hide-scrollbars \
  --force-prefers-reduced-motion \
  --virtual-time-budget=6000 \
  --window-size="${WIDTH},${HEIGHT}" \
  --screenshot="$OUT" \
  "http://127.0.0.1:8000/${PAGE}${ANCHOR}" 2>/dev/null

echo "$OUT"
