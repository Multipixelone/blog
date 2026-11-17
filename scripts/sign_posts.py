#!/usr/bin/env python3
"""Sign published source files with the author's key (never run by CI/builds)."""

import argparse
import subprocess
import sys
from pathlib import Path

from post_signatures import (
    SIGNING_KEY, PublicKeyVerifier, orphaned_signatures, published_posts,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="re-sign even valid signatures")
    args = parser.parse_args()
    signatures = Path("static/sig")
    try:
        posts = published_posts(Path("content"))
        with PublicKeyVerifier(Path("static/pgp.asc")) as verifier:
            signatures.mkdir(parents=True, exist_ok=True)
            for orphan in orphaned_signatures(signatures, posts):
                print(f"removing orphaned signature: {orphan}", flush=True)
                orphan.unlink()
            for slug, source in posts.items():
                signature = signatures / f"{slug}.md.asc"
                if not args.all and signature.is_file() and verifier.verify(signature, source)[0]:
                    print(f"unchanged: {source}", flush=True)
                    continue
                print(f"signing: {source} -> {signature}", flush=True)
                subprocess.run(
                    ["gpg", "--armor", "--detach-sign", "--local-user", SIGNING_KEY,
                     "--yes", "--output", str(signature), str(source)],
                    check=True,
                )
                valid, detail = verifier.verify(signature, source)
                if not valid:
                    raise ValueError(f"{source}: new signature does not verify with static/pgp.asc: {detail}")
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
