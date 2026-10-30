#!/bin/sh
# Pulls the 2D game's data and its generated world out of the HTML file into data2d.json, by running
# the game's own DATA and ENGINE sections in macOS's JavaScriptCore (no browser needed).
#   sh extract.sh
HERE=$(cd "$(dirname "$0")" && pwd)
SRC="$HERE/../../../../2D version/erasmus-in-barcelona Opus 5-5.html"
JSC=/System/Library/Frameworks/JavaScriptCore.framework/Versions/Current/Helpers/jsc
OUT="$HERE/data2d.json"
TMP="$HERE/_run.js"
# the script's DATA + ENGINE (up to the rendering helpers), then the dump
awk 'NR>=59 && NR<=1818' "$SRC" > "$TMP"
cat "$HERE/dump.js" >> "$TMP"
"$JSC" "$TMP" > "$OUT" && rm "$TMP" && echo "wrote $OUT"
