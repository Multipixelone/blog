#!/usr/bin/env python3
"""Generate Open Graph social cards (2400x1260) for the blog at build time.

Reads the JSON-LD already embedded in each built post (templates/page.html emits
a BlogPosting block), so no fragile front-matter parsing — the structured data is
purpose-built and stable. Renders an "accent band" card with Pillow:

  - dark paper background, a solid accent band across the top
  - post title in Cooper Black (accent), auto-fit + greedy word wrap
  - a muted two-line description under the title, when the title leaves room
  - tag chips drawn from the JSON-LD `keywords`
  - a muted meta line: "FINN RUTIS · YYYY-MM-DD · N min read"
  - the site's hostname bottom-right, so a screenshotted card still says where
    it came from

Cards are also rendered for each taxonomy term, the tag index and the standalone
sections, all of which otherwise fall back to the generic og.png.

All-Cooper by necessity: Sabon Next / PragmataPro are proprietary and absent from
the sandboxed build, so only the committed Cooper family is available. Pillow needs
TTF/OTF, so the woff2 faces are decompressed (woff2_decompress) into a temp
directory first; pass --font-dir to reuse one that already exists.

Output: <out>/og/<slug>.png per post, <out>/og/tags/<term>.png per tag,
<out>/og/tags.png, one per entry in SECTION_CARDS, plus a site-wide
<out>/og.png default.

Before exiting the script re-reads every built page's og:image and asserts the
file it points at exists, so a regex or template drift that silently stops
producing cards fails the build instead of shipping 404 card URLs.
"""

import argparse
import html
import json
import re
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path
from urllib.parse import urlsplit

from PIL import Image, ImageDraw, ImageFont

# Palette — mirrors the dark theme in static/style.css. Keep in sync.
# Dark rather than light because a card is viewed inside someone else's timeline,
# where a near-white 1200px rectangle is the brightest thing on the screen; the
# dark card sits in the feed instead of shouting over it, and the accent on near
# black clears WCAG AA for large text with room to spare.
PAPER = (28, 25, 21)      # --paper   #1c1915
ACCENT = (255, 158, 66)   # --accent  #ff9e42
INK = (232, 226, 216)     # --ink     #e8e2d8
MUTED = (158, 148, 134)   # --muted   #9e9486

# Canvas. 1200x630 is the Open Graph convention, but it is a *minimum*, and it is
# the size the card gets composited at — on a 2x display that means every card
# was being upscaled from its own native resolution and softening the type.
# Render at SCALE times the convention and declare the true pixel size in the
# templates; every measurement below is in base units and scaled at definition,
# so the layout is unchanged and only the pixel density moves.
SCALE = 2
BASE_W, BASE_H = 1200, 630
W, H = BASE_W * SCALE, BASE_H * SCALE
MARGIN = 80 * SCALE
BAND_H = 18 * SCALE      # accent band thickness across the top
CONTENT_W = W - 2 * MARGIN

# Title auto-fit bounds. Post titles are sentences and start at TITLE_MAX; the
# term/section cards are one short word ("#nix", "About") and would swim in the
# empty card at that size, so they start much larger and shrink from there.
TITLE_MAX = 78 * SCALE
TITLE_DISPLAY_MAX = 148 * SCALE
TITLE_MIN = 50 * SCALE
TITLE_STEP = 2 * SCALE   # auto-fit granularity, in real pixels
TITLE_MAX_LINES = 4
TITLE_LINE_RATIO = 1.12  # line height as a multiple of font size

# Description — only drawn when the title is short enough to leave room.
# Light-on-dark type reads thinner than the same face dark-on-light, so the
# secondary text sits a couple of points above where the light card had it.
DESC_SIZE = 34 * SCALE
DESC_MAX_LINES = 2
DESC_LINE_RATIO = 1.30
DESC_GAP = 30 * SCALE    # space between the title block and the description
TITLE_LINES_FOR_DESC = 3  # a 4-line title fills the card on its own

# Bottom row: tag chips above a meta line, hostname opposite the meta line.
# 34 base units rather than the eyeballed-at-full-size 30: cards render ~500px
# wide in most timelines, and 30 did not survive the downscale.
META_SIZE = 34 * SCALE
SITE_SIZE = 32 * SCALE
CHIP_SIZE = 26 * SCALE
CHIP_H = 44 * SCALE
CHIP_PAD_X = 18 * SCALE
CHIP_GAP = 12 * SCALE
CHIP_MAX = 3
CHIP_META_GAP = 22 * SCALE
BODY_BOTTOM_GAP = 32 * SCALE

# Standalone sections that get their own card: <slug>/index.html in the built
# output becomes og/<slug>.png, titled with the label and described from the
# page's own og:description. Anything not listed falls back to og.png.
SECTION_CARDS = (("about", "About"), ("archive", "Archive"))

# Cards are flat color with antialiased text, so they palette-quantize losslessly
# to the eye. Only bother when one crosses the threshold — most land far under.
# Scaled with the canvas: four times the pixels is roughly four times the file.
MAX_BYTES = 150 * 1024 * SCALE * SCALE
QUANTIZE_COLORS = 64

# Tolerate minified HTML: `minify_html` drops the quotes around the type value
# (`<script type=application/ld+json>`), and attribute order isn't guaranteed.
JSONLD_RE = re.compile(
    r'<script\b[^>]*\btype=(?:"application/ld\+json"|\'application/ld\+json\'|application/ld\+json)[^>]*>'
    r'\s*(\{.*?\})\s*</script>',
    re.DOTALL,
)

# Meta tags are read attribute-wise rather than with one big pattern: minify_html
# both strips quotes from values without spaces *and* reorders attributes, so it
# emits `<meta content=… property=og:image>` — the opposite order to the source.
# A pattern that assumed `property` came first matched nothing and made the
# verification pass below a no-op.
META_TAG_RE = re.compile(r"<meta\b([^>]*)>", re.IGNORECASE)
ATTR_RE = re.compile(r"""([\w:.-]+)\s*=\s*(?:"([^"]*)"|'([^']*)'|([^\s"'>=`]+))""")


# Cooper is the only build-available family: Sabon Next and PragmataPro are
# proprietary and absent from the sandboxed build. It ships as woff2 and Pillow
# needs TTF/OTF, hence the decompress step.
COOPER_FACES = ("Cooper-Black", "Cooper-Bold", "Cooper-Regular")
COOPER_SOURCE = Path("static/fonts/cooper")


def prepare_fonts(dest: Path, source: Path = COOPER_SOURCE) -> Path:
    """Decompress the committed Cooper woff2 faces into `dest` as TTF."""
    dest.mkdir(parents=True, exist_ok=True)
    for face in COOPER_FACES:
        copy = dest / f"{face}.woff2"
        shutil.copy(source / f"{face}.woff2", copy)
        subprocess.run(["woff2_decompress", str(copy)], check=True)
    return dest


def load_font(font_dir: Path, name: str, size: int) -> ImageFont.FreeTypeFont:
    return ImageFont.truetype(str(font_dir / name), size)


def lerp(a, b, t):
    """Blend two RGB tuples; used to derive chip colors from the palette."""
    return tuple(round(x + (y - x) * t) for x, y in zip(a, b))


# A 10% accent tint reads as a chip on paper but disappears into a dark card, so
# the fill is lifted until the pill has an edge without competing with the title.
CHIP_BG = lerp(PAPER, ACCENT, 0.18)
CHIP_FG = lerp(ACCENT, INK, 0.15)

# --muted is tuned for body-adjacent text at reading size on a lit page. The
# description and meta line are neither: they are small, they are the first
# things a timeline downscale eats, and light-on-dark makes them look thinner
# still. Lift them partway to --ink — dimmer than the title, but not dim.
SECONDARY = lerp(MUTED, INK, 0.4)


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


def fit_title(draw, text, font_dir, name, avail_h, start=TITLE_MAX):
    """Shrink the title until it wraps within TITLE_MAX_LINES *and* avail_h.

    Height matters as much as line count now that the bottom row (chips + meta)
    eats into the body region: four 78px lines are taller than what a card with
    chips has left over. Returns (font, lines).
    """
    for size in range(start, TITLE_MIN - 1, -TITLE_STEP):
        font = load_font(font_dir, name, size)
        lines = wrap(draw, text, font, CONTENT_W)
        block_h = int(size * TITLE_LINE_RATIO) * len(lines)
        if len(lines) <= TITLE_MAX_LINES and block_h <= avail_h:
            return font, lines
    # Floor: accept overflow at the minimum size rather than fail.
    font = load_font(font_dir, name, TITLE_MIN)
    return font, wrap(draw, text, font, CONTENT_W)[:TITLE_MAX_LINES]


def fit_description(draw, text, font, max_lines):
    """Wrap to at most max_lines, ellipsising the last line if it overflows."""
    lines = wrap(draw, text, font, CONTENT_W)
    if len(lines) <= max_lines:
        return lines
    lines = lines[:max_lines]
    last = lines[-1]
    while last and text_w(draw, last + "…", font) > CONTENT_W:
        last = last.rsplit(" ", 1)[0] if " " in last else last[:-1]
    lines[-1] = last.rstrip(" ,;:.") + "…"
    return lines


def draw_chips(draw, tags, font, top):
    """Draw up to CHIP_MAX rounded tag chips left-aligned at `top`."""
    x = MARGIN
    for tag in tags[:CHIP_MAX]:
        label = f"#{tag}"
        w = text_w(draw, label, font) + 2 * CHIP_PAD_X
        if x + w > W - MARGIN:
            break
        draw.rounded_rectangle(
            [x, top, x + w, top + CHIP_H], radius=CHIP_H // 2, fill=CHIP_BG
        )
        draw.text(
            (x + w / 2, top + CHIP_H / 2), label, font=font, fill=CHIP_FG, anchor="mm"
        )
        x += w + CHIP_GAP


def render_card(out_path, title, meta, font_dir, site="", description="", tags=(),
                title_max=TITLE_MAX):
    img = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(img)

    # Accent band across the top.
    draw.rectangle([0, 0, W, BAND_H], fill=ACCENT)

    meta_font = load_font(font_dir, "Cooper-Regular.ttf", META_SIZE)
    chip_font = load_font(font_dir, "Cooper-Regular.ttf", CHIP_SIZE)
    desc_font = load_font(font_dir, "Cooper-Regular.ttf", DESC_SIZE)

    # Bottom row first — whatever it claims is off-limits to the title block.
    meta_zone_top = H - MARGIN - META_SIZE
    chip_top = meta_zone_top - CHIP_META_GAP - CHIP_H if tags else None
    body_top = BAND_H + MARGIN
    body_bottom = (chip_top if chip_top is not None else meta_zone_top) - BODY_BOTTOM_GAP
    body_h = body_bottom - body_top

    title_font, lines = fit_title(
        draw, title, font_dir, "Cooper-Black.ttf", body_h, start=title_max
    )
    line_h = int(title_font.size * TITLE_LINE_RATIO)
    block_h = line_h * len(lines)

    # Description fills the empty middle that short titles leave behind. A title
    # that already runs to TITLE_MAX_LINES gets the card to itself.
    desc_lines = []
    desc_line_h = int(DESC_SIZE * DESC_LINE_RATIO)
    if description and len(lines) <= TITLE_LINES_FOR_DESC:
        room = body_h - block_h - DESC_GAP
        allowed = min(DESC_MAX_LINES, room // desc_line_h)
        if allowed >= 1:
            desc_lines = fit_description(draw, description, desc_font, int(allowed))
            block_h += DESC_GAP + desc_line_h * len(desc_lines)

    y = body_top + max(0, (body_h - block_h) // 2)
    for line in lines:
        draw.text((MARGIN, y), line, font=title_font, fill=ACCENT, anchor="la")
        y += line_h
    if desc_lines:
        y += DESC_GAP
        for line in desc_lines:
            draw.text((MARGIN, y), line, font=desc_font, fill=SECONDARY, anchor="la")
            y += desc_line_h

    if tags:
        draw_chips(draw, list(tags), chip_font, chip_top)

    # Meta line and site identity share a baseline at the bottom margin, so the
    # attribution travels with a card that gets reshared without its link.
    baseline = H - MARGIN
    draw.text((MARGIN, baseline), meta, font=meta_font, fill=SECONDARY, anchor="ls")
    if site:
        site_font = load_font(font_dir, "Cooper-Bold.ttf", SITE_SIZE)
        draw.text((W - MARGIN, baseline), site, font=site_font, fill=ACCENT, anchor="rs")

    out_path.parent.mkdir(parents=True, exist_ok=True)
    img.save(out_path, "PNG", optimize=True)
    if out_path.stat().st_size > MAX_BYTES:
        img.quantize(colors=QUANTIZE_COLORS).save(out_path, "PNG", optimize=True)


def reading_minutes(word_count: int) -> int:
    return max(1, round(word_count / 200))


def slugify(name: str) -> str:
    """Approximate Zola's taxonomy slugification (ASCII, lowercase, dashes)."""
    ascii_name = (
        unicodedata.normalize("NFKD", name).encode("ascii", "ignore").decode("ascii")
    )
    return re.sub(r"[^a-z0-9]+", "-", ascii_name.lower()).strip("-")


def meta_tags(page_html: str):
    """Yield every <meta> in the page as a lowercased attribute dict."""
    for tag in META_TAG_RE.finditer(page_html):
        attrs = {}
        for attr in ATTR_RE.finditer(tag.group(1)):
            name, dq, sq, bare = attr.groups()
            value = dq if dq is not None else sq if sq is not None else bare or ""
            attrs[name.lower()] = html.unescape(value)
        yield attrs


def meta_content(page_html: str, key: str) -> str:
    """Read the content of the first <meta> with this property= or name=."""
    for attrs in meta_tags(page_html):
        if key in (attrs.get("property"), attrs.get("name")):
            return attrs.get("content", "")
    return ""


def og_images(page_html: str) -> list[str]:
    """Every og:image URL declared by a page."""
    return [
        attrs["content"]
        for attrs in meta_tags(page_html)
        if attrs.get("property") == "og:image" and "content" in attrs
    ]


def parse_post(html_path: Path):
    """Extract a post's card fields from its JSON-LD, or None if not a post."""
    page = html_path.read_text(encoding="utf-8")
    for match in JSONLD_RE.finditer(page):
        try:
            data = json.loads(match.group(1))
        except json.JSONDecodeError:
            continue
        if data.get("@type") != "BlogPosting":
            continue
        slug = html_path.parent.name
        date = (data.get("datePublished") or "")[:10]
        minutes = reading_minutes(int(data.get("wordCount", 0)))
        return {
            "slug": slug,
            "title": data.get("headline", slug),
            "description": data.get("description", ""),
            "tags": data.get("keywords") or [],
            "meta": f"FINN RUTIS  ·  {date}  ·  {minutes} min read",
        }
    return None


def plural(n: int, word: str) -> str:
    return f"{n} {word}{'' if n == 1 else 's'}"


def verify_cards(out: Path, base_url: str) -> list[str]:
    """Every og:image under base_url must exist on disk. Returns the failures.

    The old script only warned when *zero* cards were generated, which meant a
    regex mismatch after a Zola upgrade could ship a handful of posts pointing
    at 404s and still go green.
    """
    prefix = base_url if base_url.endswith("/") else base_url + "/"
    missing, checked = [], 0
    for page in sorted(out.rglob("index.html")):
        for url in og_images(page.read_text(encoding="utf-8")):
            if not url.startswith(prefix):
                continue
            checked += 1
            if not (out / url[len(prefix):]).is_file():
                missing.append(f"{page.relative_to(out)} → {url}")
    # A guard that checks nothing passes for the wrong reason; every page in the
    # build declares an og:image, so finding none means the parser broke.
    if not checked:
        missing.append("no og:image declarations found in the built output")
    return missing


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", required=True, type=Path, help="built site directory")
    ap.add_argument(
        "--font-dir",
        type=Path,
        help="dir with Cooper-*.ttf; decompressed into a temp dir when omitted",
    )
    ap.add_argument("--title", required=True, help="site title for the default card")
    ap.add_argument(
        "--base-url",
        required=True,
        help="site base URL; supplies the card wordmark and resolves og:image checks",
    )
    args = ap.parse_args()

    out = args.out
    site = urlsplit(args.base_url).netloc.removeprefix("www.")

    scratch = None
    if args.font_dir:
        fonts = args.font_dir
    else:
        scratch = tempfile.TemporaryDirectory()
        fonts = prepare_fonts(Path(scratch.name))

    # Posts.
    tag_counts: dict[str, int] = {}
    posts = 0
    for html_path in sorted(out.rglob("index.html")):
        post = parse_post(html_path)
        if post is None:
            continue
        render_card(
            out / "og" / f"{post['slug']}.png",
            post["title"],
            post["meta"],
            fonts,
            site=site,
            description=post["description"],
            tags=post["tags"],
        )
        for tag in post["tags"]:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        posts += 1
        print(f"  og/{post['slug']}.png  ←  {post['title']}")

    # Taxonomy terms. Counts come from the posts we just parsed rather than from
    # re-parsing the tag pages; only emit a card where Zola actually built the
    # term directory, so a slugify disagreement can't leave orphan cards behind.
    terms = 0
    for tag, count in sorted(tag_counts.items()):
        slug = slugify(tag)
        if not (out / "tags" / slug / "index.html").is_file():
            print(f"  skipped #{tag}: no built page at tags/{slug}/", file=sys.stderr)
            continue
        render_card(
            out / "og" / "tags" / f"{slug}.png",
            f"#{tag}",
            f"FINN RUTIS  ·  {plural(count, 'post')}",
            fonts,
            site=site,
            title_max=TITLE_DISPLAY_MAX,
        )
        terms += 1
        print(f"  og/tags/{slug}.png  ←  #{tag}")

    # Tag index and About — custom templates that used to fall back to og.png.
    sections = 0
    if (out / "tags" / "index.html").is_file():
        render_card(
            out / "og" / "tags.png",
            "Tags",
            f"FINN RUTIS  ·  {plural(terms, 'tag')}",
            fonts,
            site=site,
            description="Everything on the blog, grouped by what it is about.",
            title_max=TITLE_DISPLAY_MAX,
        )
        sections += 1
        print("  og/tags.png   ←  Tags")

    for slug, label in SECTION_CARDS:
        page_path = out / slug / "index.html"
        if not page_path.is_file():
            continue
        render_card(
            out / "og" / f"{slug}.png",
            label,
            f"FINN RUTIS  ·  {label}",
            fonts,
            site=site,
            description=meta_content(
                page_path.read_text(encoding="utf-8"), "og:description"
            ),
            title_max=TITLE_DISPLAY_MAX,
        )
        sections += 1
        print(f"  og/{slug}.png  ←  {label}")

    # Site-wide default card (homepage, 404, anything without its own).
    render_card(
        out / "og.png",
        args.title,
        "FINN RUTIS  ·  Technical writings",
        fonts,
        site=site,
        description="Technical notes on Nix, infrastructure, and building software.",
        title_max=TITLE_DISPLAY_MAX,
    )
    print(f"  og.png        ←  {args.title} (default)")
    print(
        f"generated {posts} post cards, {terms} tag cards, "
        f"{sections} section cards + 1 default"
    )

    missing = verify_cards(out, args.base_url)
    if missing:
        print("error: pages reference social cards that were not generated:",
              file=sys.stderr)
        for item in missing:
            print(f"  {item}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
