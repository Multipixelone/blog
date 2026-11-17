#!/usr/bin/env bash
# Run from any directory; Python shares post selection with verification/builds.
set -euo pipefail
cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.."
exec python3 scripts/sign_posts.py "$@"
