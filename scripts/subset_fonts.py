#!/usr/bin/env python3
"""Subset webfonts to what this site actually renders, and prove nothing broke.

Fonts are the only meaningful weight on these pages; everything else is text.
Full-coverage faces carry Cyrillic, Greek, currency and typographic furniture
that never appears here — Cooper ships 491 glyphs and the site reaches about
240 of them.

The interesting part is the verification, not the subsetting. Subsetting is one
pyftsubset call; the way it goes wrong is silently, by dropping something the
design depends on and only showing up as a wrong-looking glyph months later.
Two things here are exactly that kind of trap:

  - U+2766 (❦), the fleuron under the site header. It lives in a CSS `content:`
    property, so no text-scanning heuristic would ever find it.
  - the `swsh` feature, which draws the swash drop cap on the first paragraph
    of every post. Layout-feature pruning removes it by default.

So the script asserts, on the output: every required codepoint is still mapped,
every required feature is still present, and swsh still substitutes for the
letters a post might open on.

  python3 scripts/subset_fonts.py static/fonts/cooper --in-place
  python3 scripts/subset_fonts.py ~/fonts/sabon --out ~/fonts/sabon-subset

The second form is how the R2-hosted families (Sabon Next, PragmataPro) get
done: they are proprietary and can't live in this repo, so subset them locally
and upload the result to fonts.finnrut.is.
"""

import argparse
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from fontTools.ttLib import TTFont

# Latin-1 and Latin Extended-A (European names in titles and comments), the
# whole of General Punctuation (dashes, curly quotes, ellipsis, dagger, bullet),
# a handful of symbols and maths marks that turn up in prose, the fleurons, and
# the fi/fl ligature block — this is a serif; losing those is visible.
UNICODES = ",".join((
    "U+0000-00FF",   # Basic Latin + Latin-1 Supplement
    "U+0100-017F",   # Latin Extended-A
    "U+0192",        # florin
    "U+02BC",        # modifier apostrophe
    "U+02C6-02DD",   # modifier letters and accents
    "U+2000-206F",   # General Punctuation
    "U+20AC",        # euro
    "U+2116",        # numero
    "U+2122",        # trade mark
    "U+2212",        # minus
    "U+2215",        # division slash
    "U+2219",        # bullet operator
    "U+25CA",        # lozenge
    "U+2766-2769",   # fleurons, incl. the ❦ under the header
    "U+FB00-FB04",   # fi fl ffi ffl ligatures
))

# swsh is the drop cap. The rest are ordinary typographic hygiene.
FEATURES = "kern,liga,clig,calt,swsh,dlig,frac,ordn,sups,onum,lnum"

# Checked on the output. Anything here is load-bearing somewhere in the design.
REQUIRED_CODEPOINTS = {
    0x0041: "A (drop cap)",
    0x00B7: "· (meta separators)",
    0x2013: "– en dash",
    0x2014: "— em dash",
    0x2018: "' left single quote",
    0x2019: "' right single quote",
    0x201C: '" left double quote',
    0x201D: '" right double quote',
    0x2026: "… ellipsis",
    0x2766: "❦ header fleuron",
    0xFB01: "fi ligature",
    0xFB02: "fl ligature",
}
REQUIRED_FEATURES = {"swsh", "liga"}

# Hinting is dropped by default: across the Cooper family it is the difference
# between a 17% and a 45% saving. These same files feed the Open Graph card
# renderer through FreeType at 24–148px, which is where dropping hints could
# have shown up — measured at 5 of 256 bits on the reference card, well inside
# the tolerance in check_og_render.py and indistinguishable by eye. Pass
# --keep-hinting for a family where that turns out not to hold.
KEEP_HINTING = False


def subset(source: Path, destination: Path, keep_hinting: bool) -> None:
    command = [
        "pyftsubset",
        str(source),
        f"--output-file={destination}",
        "--flavor=woff2",
        f"--unicodes={UNICODES}",
        f"--layout-features={FEATURES}",
    ]
    if not keep_hinting:
        command += ["--no-hinting", "--desubroutinize"]
    subprocess.run(command, check=True)


def features(font: TTFont) -> set[str]:
    tags = set()
    for table in ("GSUB", "GPOS"):
        if table in font:
            records = font[table].table.FeatureList.FeatureRecord
            tags.update(record.FeatureTag for record in records)
    return tags


def swash_targets(font: TTFont) -> set[str]:
    """Glyphs that swsh can substitute — empty means the drop cap is gone."""
    if "GSUB" not in font:
        return set()
    gsub = font["GSUB"].table
    indices = {
        index
        for record in gsub.FeatureList.FeatureRecord
        if record.FeatureTag == "swsh"
        for index in record.Feature.LookupListIndex
    }
    covered = set()
    for index in indices:
        for sub in gsub.LookupList.Lookup[index].SubTable:
            mapping = getattr(sub, "mapping", None)
            if mapping:
                covered.update(mapping)
            alternates = getattr(sub, "alternates", None)
            if alternates:
                covered.update(alternates)
    return covered


def verify(path: Path) -> list[str]:
    font = TTFont(path)
    cmap = font.getBestCmap()
    problems = []
    for codepoint, what in REQUIRED_CODEPOINTS.items():
        if codepoint not in cmap:
            problems.append(f"{path.name}: dropped U+{codepoint:04X} — {what}")
    missing_features = REQUIRED_FEATURES - features(font)
    if missing_features:
        problems.append(
            f"{path.name}: dropped layout feature(s) {sorted(missing_features)}"
        )
    elif not swash_targets(font):
        problems.append(f"{path.name}: swsh survived but substitutes nothing")
    return problems


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", type=Path, help="directory of fonts to subset")
    parser.add_argument("--out", type=Path, help="write subset fonts here")
    parser.add_argument(
        "--in-place",
        action="store_true",
        help="replace the source fonts (only after the verification passes)",
    )
    parser.add_argument(
        "--keep-hinting",
        action="store_true",
        default=KEEP_HINTING,
        help="retain hinting; larger, but identical server-side rasterisation",
    )
    args = parser.parse_args()

    if not args.in_place and not args.out:
        parser.error("give --out or --in-place")

    fonts = sorted(
        p for p in args.source.iterdir()
        if p.suffix.lower() in (".woff2", ".ttf", ".otf")
    )
    if not fonts:
        print(f"error: no fonts in {args.source}", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as scratch:
        staged, problems, before, after = [], [], 0, 0
        for font in fonts:
            output = Path(scratch) / f"{font.stem}.woff2"
            subset(font, output, args.keep_hinting)
            problems += verify(output)
            before += font.stat().st_size
            after += output.stat().st_size
            staged.append((font, output))
            print(
                f"  {font.name}: {font.stat().st_size:,} -> "
                f"{output.stat().st_size:,} bytes"
            )

        if problems:
            print("\nrefusing to write; the subset lost something:", file=sys.stderr)
            for problem in problems:
                print(f"  {problem}", file=sys.stderr)
            return 1

        destination = args.source if args.in_place else args.out
        destination.mkdir(parents=True, exist_ok=True)
        for original, output in staged:
            shutil.copy(output, destination / f"{original.stem}.woff2")

    saved = before - after
    print(
        f"\nwrote {len(fonts)} fonts to {destination}: "
        f"{before:,} -> {after:,} bytes ({saved:,} saved, "
        f"{saved * 100 // before}%)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
