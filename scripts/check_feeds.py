#!/usr/bin/env python3
"""Validate the built Atom and RSS feeds.

The feed templates are hand-maintained overrides of Zola's built-ins, and their
comments record that byte-level XML problems have bitten before (a stray newline
above the XML declaration is enough to make every reader reject the file). This
is the check that would have caught that, plus the ones that catch the more
ordinary ways a feed goes wrong.

Three layers, cheapest first:

  1. Well-formedness, and the declaration really starting at byte 0.
  2. Structure: the elements the specs require, on the feed and on every entry.
  3. feedparser's own verdict — it is the parser a large share of real readers
     are built on, so its `bozo` flag is a fair proxy for "a reader will choke".

Usage:  python3 scripts/check_feeds.py <built-site-dir>
Exits non-zero, listing every problem, if anything fails.
"""

import sys
import xml.etree.ElementTree as ET
from pathlib import Path

import feedparser

ATOM = "http://www.w3.org/2005/Atom"

# Elements each format must carry, as (path relative to the root, human name).
ATOM_FEED_REQUIRED = ("id", "title", "link")
ATOM_ENTRY_REQUIRED = ("id", "title", "updated")
RSS_CHANNEL_REQUIRED = ("title", "link", "description")
RSS_ITEM_REQUIRED = ("title", "link")


def find_feeds(root: Path) -> list[Path]:
    """Every feed in the built output: site-wide and per tag."""
    return sorted(
        p
        for p in root.rglob("*.xml")
        if p.name in ("atom.xml", "rss.xml")
    )


def check_declaration(path: Path, problems: list[str]) -> bytes:
    """The XML declaration has to be the first bytes of the file, no BOM."""
    raw = path.read_bytes()
    if not raw.startswith(b"<?xml "):
        problems.append(
            f"{path}: does not start with an XML declaration "
            f"(first bytes: {raw[:20]!r})"
        )
    return raw


def check_atom(path: Path, root: ET.Element, problems: list[str]) -> None:
    for name in ATOM_FEED_REQUIRED:
        if root.find(f"{{{ATOM}}}{name}") is None:
            problems.append(f"{path}: feed is missing <{name}>")
    entries = root.findall(f"{{{ATOM}}}entry")
    if not entries:
        problems.append(f"{path}: feed has no entries")
    for index, entry in enumerate(entries, start=1):
        for name in ATOM_ENTRY_REQUIRED:
            if entry.find(f"{{{ATOM}}}{name}") is None:
                problems.append(f"{path}: entry {index} is missing <{name}>")
        if entry.find(f"{{{ATOM}}}link") is None:
            problems.append(f"{path}: entry {index} is missing <link>")


def check_rss(path: Path, root: ET.Element, problems: list[str]) -> None:
    channel = root.find("channel")
    if channel is None:
        problems.append(f"{path}: no <channel>")
        return
    for name in RSS_CHANNEL_REQUIRED:
        if channel.find(name) is None:
            problems.append(f"{path}: channel is missing <{name}>")
    items = channel.findall("item")
    if not items:
        problems.append(f"{path}: channel has no items")
    for index, item in enumerate(items, start=1):
        for name in RSS_ITEM_REQUIRED:
            if item.find(name) is None:
                problems.append(f"{path}: item {index} is missing <{name}>")


def check_with_feedparser(path: Path, problems: list[str]) -> None:
    parsed = feedparser.parse(str(path))
    # bozo is set for anything from a syntax error to an undeclared namespace.
    # CharacterEncodingOverride is the one benign case: feedparser reports it
    # when it trusts the declaration over its own sniffing, which is fine.
    if parsed.bozo and not isinstance(
        parsed.bozo_exception, feedparser.CharacterEncodingOverride
    ):
        problems.append(f"{path}: feedparser rejected it: {parsed.bozo_exception}")
    if not parsed.entries:
        problems.append(f"{path}: feedparser found no entries")


def main() -> int:
    if len(sys.argv) != 2:
        print(__doc__, file=sys.stderr)
        return 2
    root = Path(sys.argv[1])
    feeds = find_feeds(root)
    if not feeds:
        print(f"error: no feeds found under {root}", file=sys.stderr)
        return 1

    problems: list[str] = []
    for path in feeds:
        check_declaration(path, problems)
        try:
            tree = ET.parse(path)
        except ET.ParseError as exc:
            problems.append(f"{path}: not well-formed XML: {exc}")
            continue
        element = tree.getroot()
        if element.tag == f"{{{ATOM}}}feed":
            check_atom(path, element, problems)
        elif element.tag == "rss":
            check_rss(path, element, problems)
        else:
            problems.append(f"{path}: unrecognised root element <{element.tag}>")
        check_with_feedparser(path, problems)

    if problems:
        print(f"{len(problems)} problem(s) in {len(feeds)} feed(s):", file=sys.stderr)
        for problem in problems:
            print(f"  {problem}", file=sys.stderr)
        return 1

    print(f"ok: {len(feeds)} feeds valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
