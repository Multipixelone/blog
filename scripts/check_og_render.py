#!/usr/bin/env python3
"""Detect unintended changes to how social cards render.

Nothing in CI looks at the cards. A nixpkgs bump that moves Pillow, FreeType or
the font stack could shift metrics, drop a feature, or substitute a face, and
every check would still pass while the cards quietly turned into something else.

This renders one card from *fixed* inputs — so the only thing that can move it
is the renderer — and compares it to a committed reference with a difference
hash. A perceptual hash rather than a byte comparison because PNG encoders and
antialiasing wobble at the last bit without anything visible changing; a
threshold catches "the layout moved" without crying about "one pixel is one
shade different".

  python3 scripts/check_og_render.py            # compare against the reference
  python3 scripts/check_og_render.py --update   # adopt the current render

Run --update deliberately, after looking at the new card, when a design change
is the point. The diff will show the reference image changing, which is the
review you want.
"""

import argparse
import sys
import tempfile
from pathlib import Path

from PIL import Image

# The renderer itself, so this check exercises the real drawing code rather than
# a copy of it. Imported by path because scripts/ isn't a package.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import gen_og_cards as og  # noqa: E402

REFERENCE = Path("tests/og-reference.png")

# Fixed inputs. Do not derive these from real content: a card that changes when
# a post is edited is a card nobody can hold still long enough to compare.
CARD = {
    "title": "A reference card, held still on purpose",
    "meta": "FINN RUTIS  ·  2026-01-01  ·  7 min read",
    "site": "blog.finnrut.is",
    "description": (
        "Fixed text, fixed layout, fixed fonts — so anything that moves this "
        "image came from the renderer rather than the content."
    ),
    "tags": ["nix", "flakes", "meta"],
}

# Bits of a 256-bit difference hash. Antialiasing noise lands in low single
# digits; a shifted baseline or a substituted face lands far above this.
THRESHOLD = 10
HASH_SIZE = 16


def dhash(image: Image.Image, size: int = HASH_SIZE) -> list[bool]:
    """Difference hash: each bit is "this pixel is darker than the next one".

    Scale-invariant and tolerant of small tonal shifts, which is exactly the
    noise we want to ignore, while staying sensitive to where things sit.
    """
    small = image.convert("L").resize((size + 1, size), Image.LANCZOS)
    # tobytes() on an "L" image is row-major one byte per pixel — same values
    # getdata() would give, without the deprecation.
    pixels = small.tobytes()
    return [
        pixels[row * (size + 1) + col] < pixels[row * (size + 1) + col + 1]
        for row in range(size)
        for col in range(size)
    ]


def distance(a: list[bool], b: list[bool]) -> int:
    return sum(1 for x, y in zip(a, b) if x != y)


def render_reference(destination: Path) -> None:
    with tempfile.TemporaryDirectory() as scratch:
        fonts = og.prepare_fonts(Path(scratch))
        og.render_card(
            destination,
            CARD["title"],
            CARD["meta"],
            fonts,
            site=CARD["site"],
            description=CARD["description"],
            tags=CARD["tags"],
        )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--update",
        action="store_true",
        help="overwrite the reference with the current render",
    )
    parser.add_argument("--reference", type=Path, default=REFERENCE)
    args = parser.parse_args()

    if args.update:
        args.reference.parent.mkdir(parents=True, exist_ok=True)
        render_reference(args.reference)
        print(f"wrote {args.reference}")
        return 0

    if not args.reference.is_file():
        print(
            f"error: no reference at {args.reference}. "
            f"Create one with --update once the card looks right.",
            file=sys.stderr,
        )
        return 1

    with tempfile.TemporaryDirectory() as scratch:
        current = Path(scratch) / "current.png"
        render_reference(current)
        if current.read_bytes() == args.reference.read_bytes():
            print("ok: card renders byte-for-byte identically")
            return 0
        moved = distance(
            dhash(Image.open(current)), dhash(Image.open(args.reference))
        )

    if moved > THRESHOLD:
        print(
            f"error: the reference card renders differently "
            f"({moved}/{HASH_SIZE ** 2} bits changed, threshold {THRESHOLD}).\n"
            f"  Something in the render path moved — Pillow, FreeType, the "
            f"fonts, or scripts/gen_og_cards.py.\n"
            f"  If the change was intended, look at the new card and run:\n"
            f"    python3 scripts/check_og_render.py --update",
            file=sys.stderr,
        )
        return 1

    print(f"ok: card within tolerance ({moved}/{HASH_SIZE ** 2} bits changed)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
