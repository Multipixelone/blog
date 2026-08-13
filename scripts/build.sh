#!/usr/bin/env bash
# Build the complete site: pages, social cards, search index.
#
# The flake's buildPhase and CI's audit job both need the whole thing, and they
# had already drifted — CI was auditing a site with no /og/ cards and no
# /pagefind/ index, which is not the site that ships. One script, two callers.
#
#   scripts/build.sh <output-dir> [base-url]
#
# base-url defaults to whatever zola.toml says, so the two never disagree; CI
# overrides it to point the absolute URLs at its local audit server.
set -euo pipefail

out=${1:?usage: build.sh <output-dir> [base-url]}
base_url=${2:-}

if [ -z "$base_url" ]; then
  base_url=$(sed -n 's/^base_url *= *"\(.*\)"/\1/p' zola.toml | head -1)
fi
if [ -z "$base_url" ]; then
  echo "build.sh: no base_url given and none found in zola.toml" >&2
  exit 1
fi

zola build --base-url "$base_url" --output-dir "$out"

# Social cards. The generator handles the woff2 -> ttf step Pillow needs.
python3 scripts/gen_og_cards.py \
  --out "$out" --title "Finn Rutis" --base-url "$base_url"

# Search index, built from the finished HTML so it can't disagree with it.
pagefind --site "$out"
