#!/usr/bin/env python3
"""Catch front-matter drift in content/.

Written after two posts shipped with another post's metadata: fractured-mind.md
carried resume-gen.md's `description` and `cover_alt` verbatim, and
nixos-for-who.md's `cover_alt` still named a title from three revisions earlier.
`description` feeds the meta description, og:description, the BlogPosting
JSON-LD, the social card and the feed summary fallback, so one copy-paste was
wrong in five places at once and nothing complained.

Checks, all fatal:

  1. Every post has a non-empty `description`.
  2. No two posts share a `description` — copy-paste drift is what this is for,
     and identical descriptions are also worth avoiding on their own.
  3. `extra.cover_alt`, where set, mentions the post's own title.

Usage:  python3 scripts/check_frontmatter.py [content-dir]
"""

import sys
import tomllib
from pathlib import Path

import yaml


def split_front_matter(text: str):
    """Return the parsed front matter of a Zola content file, or None.

    Zola accepts TOML between +++ fences and YAML between --- fences.
    """
    for fence, parse in (("+++", tomllib.loads), ("---", yaml.safe_load)):
        if not text.startswith(fence + "\n"):
            continue
        end = text.find("\n" + fence, len(fence))
        if end == -1:
            return None
        return parse(text[len(fence) + 1:end + 1])
    return None


def posts(content: Path):
    """Every page in content/ that is a post rather than a section index."""
    for path in sorted(content.rglob("*.md")):
        if path.name == "_index.md":
            continue
        data = split_front_matter(path.read_text(encoding="utf-8"))
        if data:
            yield path, data


def main() -> int:
    content = Path(sys.argv[1] if len(sys.argv) > 1 else "content")
    if not content.is_dir():
        print(f"error: {content} is not a directory", file=sys.stderr)
        return 2

    problems: list[str] = []
    seen_descriptions: dict[str, Path] = {}
    count = 0

    for path, data in posts(content):
        count += 1
        title = (data.get("title") or "").strip()
        description = (data.get("description") or "").strip()

        if not description:
            problems.append(f"{path}: no description")
        else:
            earlier = seen_descriptions.get(description)
            if earlier is not None:
                problems.append(
                    f"{path}: description is identical to {earlier}'s — "
                    f"almost certainly copy-pasted"
                )
            else:
                seen_descriptions[description] = path

        cover_alt = (data.get("extra") or {}).get("cover_alt")
        if cover_alt and title and title not in cover_alt:
            problems.append(
                f"{path}: cover_alt does not mention this post's title\n"
                f"      title:     {title}\n"
                f"      cover_alt: {cover_alt}"
            )

    if problems:
        print(f"{len(problems)} problem(s) in {count} post(s):", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1

    print(f"ok: front matter consistent across {count} posts")
    return 0


if __name__ == "__main__":
    sys.exit(main())
