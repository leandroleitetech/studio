#!/bin/bash
# Render every HTML draft to a 1920x1080 PNG next to it.
#
#   render.sh draft-a.html draft-b.html ...
#
# Sequential on purpose: about 3 seconds per draft. Running several Chromes at
# once with --user-data-dir writes the PNGs but Chrome then never exits
# (observed 2026-09-14), so the parallel version hung every time.
# Output: <name>.png beside each <name>.html. One line per render.
# Browser: $CHROME if set, else Google Chrome / Chromium, else the playwright Chromium
# installed by `npm run instalar`. Exits 1 if any draft failed.
set -uo pipefail

[ $# -gt 0 ] || { echo "usage: render.sh <draft.html>..." >&2; exit 1; }

here="$(cd "$(dirname "$0")" && pwd)"
pw_prefix="$here/../../overlay-graphics/scripts"
find_chrome() {
  [ -n "${CHROME:-}" ] && { echo "$CHROME"; return; }
  for c in "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" \
           "/Applications/Chromium.app/Contents/MacOS/Chromium" \
           "$(command -v google-chrome || true)" "$(command -v chromium || true)"; do
    [ -n "$c" ] && [ -x "$c" ] && { echo "$c"; return; }
  done
  [ -d "$pw_prefix/node_modules/playwright" ] &&
    (cd "$pw_prefix" && node -e 'console.log(require("playwright").chromium.executablePath())' 2>/dev/null)
}
CHROME="$(find_chrome)"
[ -n "$CHROME" ] && [ -x "$CHROME" ] || { echo "no Chrome/Chromium found: run npm run instalar or set CHROME=/path" >&2; exit 1; }

failed=0
for html in "$@"; do
  if [ ! -f "$html" ]; then echo "FAILED $html (not found)"; failed=1; continue; fi
  abs=$(cd "$(dirname "$html")" && pwd)/$(basename "$html")
  out="${abs%.html}.png"
  rm -f "$out"
  "$CHROME" --headless=new --disable-gpu --hide-scrollbars \
      --force-device-scale-factor=1 --window-size=1920,1080 \
      --screenshot="$out" "file://$abs" >/dev/null 2>&1
  # Chrome exits 0 even when it writes nothing: trust the file, not the exit code.
  if [ -s "$out" ]; then
    echo "rendered $out"
  else
    echo "FAILED $html"; failed=1
  fi
done
exit $failed
