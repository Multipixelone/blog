#!/usr/bin/env python3
"""Publish the exact signed Markdown bytes alongside Zola's static signatures."""

import argparse
import shutil
import sys
from pathlib import Path

from post_signatures import published_posts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", type=Path, help="built site's output directory")
    args = parser.parse_args()
    try:
        posts = published_posts(Path("content"))
        target = args.output / "sig"
        target.mkdir(parents=True, exist_ok=True)
        for slug, source in posts.items():
            shutil.copyfile(source, target / f"{slug}.md")
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"published exact source bytes for {len(posts)} post(s) in {target}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
