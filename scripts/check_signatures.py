#!/usr/bin/env python3
"""Verify published post signatures using only static/pgp.asc, without secrets."""

import argparse
import sys
from pathlib import Path

from post_signatures import PublicKeyVerifier, orphaned_signatures, published_posts


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content", type=Path, default=Path("content"))
    parser.add_argument("--signatures", type=Path, default=Path("static/sig"))
    parser.add_argument("--public-key", type=Path, default=Path("static/pgp.asc"))
    args = parser.parse_args()
    problems = []
    try:
        posts = published_posts(args.content)
        with PublicKeyVerifier(args.public_key) as verifier:
            for slug, source in posts.items():
                signature = args.signatures / f"{slug}.md.asc"
                if not signature.is_file():
                    problems.append(f"{source}: missing signature: {signature}")
                    continue
                valid, detail = verifier.verify(signature, source)
                if not valid:
                    problems.append(f"{source}: invalid/stale signature: {signature}\n    {detail}")
            for orphan in orphaned_signatures(args.signatures, posts):
                problems.append(f"{orphan}: orphaned signature (no published post)")
    except (OSError, ValueError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    if problems:
        for problem in problems:
            print(f"error: {problem}", file=sys.stderr)
        print(f"{len(problems)} signature problem(s) in {len(posts)} published post(s)", file=sys.stderr)
        return 1
    print(f"ok: valid signatures for all {len(posts)} published post(s)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
