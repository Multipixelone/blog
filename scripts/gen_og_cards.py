#!/usr/bin/env python3
"""Generate Open Graph social cards (1200x630) for the blog at build time.

Reads the JSON-LD already embedded in each built post (templates/page.html emits
a BlogPosting block), so no fragile front-matter parsing — the structured data is
purpose-built and stable. Renders an "accent band" card with Pillow:

  - paper background, a solid accent band across the top
  - post title in Cooper Black (accent), auto-fit + greedy word wrap
  - a muted meta line: "FINN RUTIS · YYYY-MM-DD · N min read"

All-Cooper by necessity: Sabon Next / PragmataPro are proprietary and absent from
the sandboxed build, so only the committed Cooper family is available. Pillow needs
TTF/OTF, so the caller decompresses Cooper woff2 -> ttf (woff2_decompress) first and
passes the directory via --font-dir.

Output: <out>/og/<slug>.png per post, plus a site-wide <out>/og.png default.
"""

import argparse
import json
import re
import sys
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

# Palette — mirrors static/style.css :root (light theme). Keep in sync.
PAPER = (247, 244, 237)   # --paper   #f7f4ed
ACCENT = (181, 74, 0)     # --accent  #b54a00
INK = (43, 37, 32)        # --ink     #2b2520
MUTED = (118, 107, 94)    # --muted   #766b5e
BAND_TEXT = (247, 244, 237)  # paper, for text sitting on the accent band

# Canvas — the Open Graph standard card size declared in the templates.
W, H = 1200, 630
MARGIN = 80
BAND_H = 18              # accent band thickness across the top
CONTENT_W = W - 2 * MARGIN

# Title auto-fit bounds.
TITLE_MAX = 78
TITLE_MIN = 50
TITLE_MAX_LINES = 4
TITLE_LINE_RATIO = 1.12  # line height as a multiple of font size

# Tolerate minified HTML: `minify_html` drops the quotes around the type value
# (`<script type=application/ld+json>`), and attribute order isn't guaranteed.
JSONLD_RE = re.compile(
    r'<script\b[^>]*\btype=(?:"application/ld\+json"|\'application/ld\+json\'|application/ld\+json)[^>]*>'
    r'\s*(\{.*?\})\s*</script>',
    re.DOTALL,
)


def load_font(font_dir: Path, name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(font_dir / name), size)


def text_w(draw: ImageDraw.ImageDraw, text: str, font: ImageFont.FreeTypeFont) -> float:
    return draw.textlength(text, font=font)


def wrap(draw, text, font, max_w):
    """Greedy word wrap to max_w pixels. Returns list of lines."""
    words = text.split()
    lines, cur = [], ""
    for word in words:
        trial = f"{cur} {word}".strip()
        if text_w(draw, trial, font) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def fit_title(draw, text, font_dir, name):
    """Shrink the title until it wraps within TITLE_MAX_LINES; return (font, lines)."""
    for size in range(TITLE_MAX, TITLE_MIN - 1, -2):
        font = load_font(font_dir, name, size)
        lines = wrap(draw, text, font, CONTENT_W)
        if len(lines) <= TITLE_MAX_LINES:
            return font, lines
    # Floor: accept overflow at the minimum size rather than fail.
    font = load_font(font_dir, name, TITLE_MIN)
    return font, wrap(draw, text, font, CONTENT_W)


def render_card(out_path, title, meta, font_dir):
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # Accent band across the top.
    draw.rectangle([0, 0, W, BAND_H], fill=ACCENT)

    # Title — Cooper Black, accent, vertically centred in the body region.
    title_font, lines = fit_title(draw, title, font_dir, "Cooper-Black.ttf")
    line_h = int(title_font.size * TITLE_LINE_RATIO)
    block_h = line_h * len(lines)
    meta_font = load_font(font_dir, "Cooper-Regular.ttf", 30)
    meta_h = meta_font.size + 24

    # Place the title block in the space between band and meta line.
    body_top = BAND_H + MARGIN
    body_bottom = H - MARGIN - meta_h
    y = body_top + max(0, (body_bottom - body_top - block_h) // 2)
    for line in lines:
        draw.text((MARGIN, y), line, font=title_font, fill=ACCENT)
        y += line_h

    # Meta line — muted, near the bottom.
    draw.text((MARGIN, H - MARGIN - meta_font.size), meta, font=meta_font, fill=MUTED)

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)


def reading_minutes(word_count: int) -> int:
    return max(1, round(word_count / 200))


def parse_post(html_path: Path):
    """Extract (slug, title, meta-string) from a built post's JSON-LD, or None."""
    html = html_path.read_text(encoding="utf-8")
    for match in JSONLD_RE.finditer(html):
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if data.get("@type") != "BlogPosting":
            continue
        slug = html_path.parent.name
        title = data.get("headline", slug)
        date = (data.get("datePublished") or "")[:10]
        minutes = reading_minutes(int(data.get("wordCount", 0)))
        meta = f"FINN RUTIS  ·  {date}  ·  {minutes} min read"
        return slug, title, meta
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path, help="built site directory")
    ap.add_argument("--font-dir", required=True, type=Path, help="dir with Cooper-*.ttf")
    ap.add_argument("--title", required=True, help="site title for the default card")
    ap.add_argument("--base-url", required=True, help="(unused; kept for clarity)")
    args = ap.parse_args()

    count = 0
    for html_path in sorted(args.out.rglob("index.html")):
        post = parse_post(html_path)
        if post is None:
            continue
        slug, title, meta = post
        render_card(args.out / "og" / f"{slug}.png", title, meta, args.font_dir)
        count += 1
        print(f"  og/{slug}.png  ←  {title}")

    # Site-wide default card (homepage, tags, about).
    render_card(args.out / "og.png", args.title, "FINN RUTIS  ·  Technical writings",
                args.font_dir)
    print(f"  og.png        ←  {args.title} (default)")
    print(f"generated {count} post cards + 1 default")

    if count == 0:
        print("warning: no BlogPosting cards generated", file=sys.stderr)


if __name__ == "__main__":
    main()
