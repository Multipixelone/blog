#!/usr/bin/env python3
"""Shared post selection and public-key-only detached-signature verification."""

import re
import subprocess
import tempfile
from pathlib import Path

from check_frontmatter import split_front_matter

SIGNING_KEY = "0x59BF38D05371C5E9"


def published_posts(content: Path) -> dict[str, Path]:
    """Map URL-safe slugs to flat, non-draft posts, never rewriting source bytes."""
    if not content.is_dir():
        raise ValueError(f"{content}: not a content directory")
    result = {}
    for path in sorted(content.glob("*.md")):
        if path.name == "_index.md":
            continue
        data = split_front_matter(path.read_text(encoding="utf-8"))
        if not isinstance(data, dict):
            raise ValueError(f"{path}: missing or invalid front matter")
        if data.get("draft") is True:
            continue
        slug = data.get("slug", path.stem)
        if not isinstance(slug, str) or not re.fullmatch(r"[\w-]+", slug):
            raise ValueError(f"{path}: unsafe or empty signature slug {slug!r}")
        if slug in result:
            raise ValueError(f"{path}: duplicate signature slug {slug!r} ({result[slug]})")
        result[slug] = path
    return result


def orphaned_signatures(directory: Path, posts: dict[str, Path]) -> list[Path]:
    expected = {directory / f"{slug}.md.asc" for slug in posts}
    return sorted(path for path in directory.rglob("*.asc") if path not in expected)


class PublicKeyVerifier:
    """Use only the supplied public key, never the user's keyring or trust DB."""

    def __init__(self, public_key: Path):
        self.public_key = public_key
        self.temp = tempfile.TemporaryDirectory(prefix="post-signatures-")

    def __enter__(self):
        self.home = Path(self.temp.name)
        self.keyring = self.home / "public-key.gpg"
        try:
            result = subprocess.run(
                ["gpg", "--no-options", "--homedir", str(self.home), "--batch",
                 "--dearmor", "--output", str(self.keyring), str(self.public_key.resolve())],
                capture_output=True, text=True, check=False,
            )
            if result.returncode:
                raise ValueError(f"{self.public_key}: cannot load public key: {result.stderr.strip()}")
        except Exception:
            self.temp.cleanup()
            raise
        return self

    def verify(self, signature: Path, source: Path) -> tuple[bool, str]:
        result = subprocess.run(
            ["gpgv", "--homedir", str(self.home), "--keyring", str(self.keyring),
             str(signature.resolve()), str(source.resolve())],
            capture_output=True, text=True, check=False,
        )
        return result.returncode == 0, result.stderr.strip()

    def __exit__(self, *_):
        self.temp.cleanup()
