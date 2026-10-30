---
name: Finn Rutis — Blog
description: A writing room lit by one lamp; warm dark paper, a Cooper drop cap and amber ink, with a daylight edition on request.
colors:
  wings-black: "#1c1915"
  wings-shade: "#242019"
  chalk-ink: "#e8e2d8"
  dust-ink: "#9e9486"
  footlight-amber: "#ff9e42"
  bright-footlight: "#ffb366"
  ember-blush: "#5a2e0f"
  dark-rule-line: "#3b342c"
  dark-code-border: "#332d26"
  gruvbox-dark: "#282828"
  playbill-paper: "#f7f4ed"
  callboard-card: "#efeadd"
  program-ink: "#2b2520"
  faded-ink: "#6f6456"
  marquee-rust: "#b54a00"
  deep-marquee-rust: "#8c3800"
  stub-blush: "#f5d9c4"
  rule-line: "#ddd6c6"
  light-code-bg: "#f3efe6"
  light-code-border: "#e7e0d1"
  alert-note: "#6a8fc5"
  alert-tip: "#6a9a6a"
  alert-important: "#9a6aba"
  alert-warning: "#c09a4a"
  alert-caution: "#c06a6a"
typography:
  display:
    fontFamily: '"Cooper*", Georgia, serif'
    fontSize: "2.3rem"
    fontWeight: 700
    lineHeight: 1.05
    letterSpacing: "0"
    fontFeature: '"dlig" 1'
  headline:
    fontFamily: '"Sabon Next", Georgia, "Times New Roman", serif'
    fontSize: "1.75rem"
    fontWeight: 700
    lineHeight: 1.25
  title:
    fontFamily: '"Sabon Next", Georgia, "Times New Roman", serif'
    fontSize: "1.35rem"
    fontWeight: 500
    lineHeight: 1.3
  body:
    fontFamily: '"Sabon Next", Georgia, "Times New Roman", serif'
    fontSize: "18px"
    fontWeight: 400
    lineHeight: 1.75
  meta:
    fontFamily: '"Sabon Next", Georgia, "Times New Roman", serif'
    fontSize: "0.9rem"
    fontWeight: 400
    lineHeight: 1.6
  label:
    fontFamily: '"Sabon Next", Georgia, "Times New Roman", serif'
    fontSize: "0.95rem"
    fontWeight: 600
    letterSpacing: "0.06em"
    fontFeature: '"smcp" 1'
  code:
    fontFamily: '"PragmataPro Mono Liga", ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace'
    fontSize: "0.85em"
    fontWeight: 400
  mono-label:
    fontFamily: '"PragmataPro Mono Liga", ui-monospace, SFMono-Regular, "SF Mono", Menlo, Consolas, monospace'
    fontSize: "0.72rem"
    fontWeight: 400
    letterSpacing: "0.03em"
rounded:
  hairline: "2px"
  sm: "3px"
  md: "4px"
  card: "6px"
  pill: "999px"
spacing:
  xs: "0.25rem"
  sm: "0.5rem"
  md: "0.75rem"
  lg: "1.25rem"
  xl: "2.5rem"
  xxl: "3rem"
  measure: "700px"
components:
  inline-code:
    backgroundColor: "{colors.wings-shade}"
    textColor: "{colors.chalk-ink}"
    typography: "{typography.code}"
    rounded: "{rounded.sm}"
    padding: "0.1em 0.3em"
  code-block:
    backgroundColor: "{colors.gruvbox-dark}"
    textColor: "{colors.chalk-ink}"
    typography: "{typography.code}"
    rounded: "{rounded.md}"
    padding: "1rem"
  copy-button:
    backgroundColor: "transparent"
    textColor: "{colors.dust-ink}"
    rounded: "{rounded.sm}"
    padding: "0.15rem 0.5rem"
  copy-button-hover:
    backgroundColor: "{colors.wings-shade}"
    textColor: "{colors.footlight-amber}"
  tag-chip:
    backgroundColor: "{colors.wings-shade}"
    textColor: "{colors.chalk-ink}"
    typography: "{typography.label}"
    rounded: "{rounded.pill}"
    padding: "0.3rem 0.7rem 0.4rem"
  tag-chip-hover:
    backgroundColor: "{colors.wings-black}"
    textColor: "{colors.footlight-amber}"
  toc:
    backgroundColor: "{colors.wings-shade}"
    textColor: "{colors.chalk-ink}"
    typography: "{typography.meta}"
    rounded: "{rounded.md}"
    padding: "0.75rem 1rem"
  elsewhere-card:
    backgroundColor: "{colors.wings-shade}"
    textColor: "{colors.chalk-ink}"
    rounded: "{rounded.card}"
    padding: "0.55rem 0.8rem"
  comment:
    backgroundColor: "{colors.wings-shade}"
    textColor: "{colors.chalk-ink}"
    rounded: "{rounded.card}"
    padding: "1rem 1.1rem"
  markdown-alert:
    rounded: "{rounded.hairline}"
    padding: "0.5em 1em"
  footer-slip:
    backgroundColor: "{colors.wings-shade}"
    textColor: "{colors.dust-ink}"
    padding: "0.6rem 0.9rem 0.6rem 0.65rem"
    height: "44px"
---

# Design System: Finn Rutis — Blog

## Overview

**Creative North Star: "The Ghost Light"**

The ghost light is the single bare lamp left burning on an empty stage after everyone has gone home. This blog is what gets written under it: one person, late, turning a messy day into sentences. The page is warm dark paper, not a black screen; the type is a book serif, read at a comfortable 700px measure; the only colour with any heat is a footlight amber, used for the things you can touch (links, the drop cap, the ❦ under the header, focus rings) and for nothing else.

It is the sibling of finnrut.is ("The Callboard", recorded in `MAIN_WEBSITE.md`). Both rooms share the same stock: Cooper for titles, Sabon Next for reading, PragmataPro for code and identifiers, one warm accent, paper surfaces with hairline rules, and the torn-paper footer slips. The blog is quieter. There are no tilted prints or ticket stubs on the page; posts are long, often technical, and must be comfortable from first line to last footnote. Personality lives in a few small, deliberate places: the Cooper drop cap, the fleuron, small-caps labels, the slips that lift in the footer.

**Dark is the default edition.** Every reader gets the Ghost Light palette on first paint, whatever their OS says. The daylight edition (the Callboard's cream paper and Marquee Rust) is one toggle away and is remembered once chosen. The main site's Daylight Rule does not apply here.

Rejected: the developer-portfolio dark mode (pure black, neon accents, terminal motifs, gradient cards), the tutorial mill (sidebars, ad slots, "Table of Contents" boxes shouting above the fold), and anything that makes a stranger feel more expected than a friend.

**Key Characteristics:**

- Warm dark paper (Wings Black) with chalky warm ink; never `#000` and never pure white text.
- One accent per edition: Footlight Amber in the dark, Marquee Rust in the light.
- Cooper at headline scale for page titles and the drop cap only; Sabon Next for everything read; PragmataPro for code and identifiers.
- Flat, tonal surfaces separated by hairline rules; shadows only on code cards, slips and lifted chips.
- Small, warm motion (150ms colour shifts, a 1px lift, a slip that rotates in) that disappears under reduced motion.

## Colors

Two editions on the same structure. Each has one paper, one heavier backing stock, one ink, one faded ink, one accent and its hover, one selection tint and one rule line. The dark edition is canonical.

### Primary

- **Footlight Amber** (#ff9e42): the accent in the dark edition. Links, the drop cap, the ❦ header ornament, hovered nav and tags, focus outlines, the left stripe on the table of contents. 8.52:1 on Wings Black.
- **Bright Footlight** (#ffb366): hovered links, and the footer slip label when hovered or current. 9.92:1 on Wings Black.
- **Marquee Rust** (#b54a00): the accent in the light edition, shared with finnrut.is. 4.85:1 on Playbill Paper.
- **Deep Marquee Rust** (#8c3800): Marquee Rust's hover in the light edition.

### Neutral (dark edition, default)

- **Wings Black** (#1c1915): page background, and the `theme-color` meta in dark mode.
- **Wings Shade** (#242019): backing stock for inline code, the table of contents, tag chips, "Elsewhere" cards, comments, footer slips.
- **Chalk Ink** (#e8e2d8): body text and headings. 13.59:1 on Wings Black.
- **Dust Ink** (#9e9486): dates, reading time, pronouns, footnotes, tag links, footer text. 5.87:1 on Wings Black, 5.43:1 on Wings Shade.
- **Ember Blush** (#5a2e0f): text selection and the highlight on a targeted footnote.
- **Dark Rule Line** (#3b342c): hairlines under the header, between posts (dashed), above footnotes and the footer; chip and card borders.
- **Gruvbox Dark** (#282828): the surface of highlighted code blocks, supplied by `giallo-dark.css`.

### Neutral (light edition)

- **Playbill Paper** (#f7f4ed), **Callboard Card** (#efeadd), **Program Ink** (#2b2520, 13.77:1), **Faded Ink** (#6f6456, 5.26:1), **Stub Blush** (#f5d9c4) and **Rule Line** (#ddd6c6): the same roles as their dark counterparts, with the same names and values as finnrut.is. Code uses **Light Code Bg** (#f3efe6) and **Light Code Border** (#e7e0d1), plus the Gruvbox light surface from `giallo-light.css`.

### Alerts

Markdown alerts (note, tip, important, warning, caution) carry the only other hues: a muted blue, green, violet, ochre and red, used as a 3px left border on a barely tinted surface of the same hue. The values in the frontmatter are the dark-edition borders; each edition defines its own `--alert-*-bd` / `--alert-*-bg` pair in `static/style.css`.

### Named Rules

**The One Lamp Rule.** Each edition has exactly one accent. Amber (or Rust) marks what can be clicked, focused or followed, plus the drop cap and the fleuron. It is never a background fill, never body text, never a heading colour. Alert hues stay inside alerts.

**The Ghost Light Rule.** Dark is the default edition for every new reader. Light exists, is fully supported and must pass the same contrast checks, but it is opt-in.

**The Warm Dark Rule.** Darks are brown-black, lights are bone. No `#000`, no `#fff`, no cool greys, in either edition (print styles excepted).

## Typography

**Title Font:** Cooper* (local, OFL), weights 400/700/900
**Reading Font:** Sabon Next (licensed, `fonts.finnrut.is`), regular, italic, demi, bold
**Code Font:** PragmataPro Mono Liga (licensed, `fonts.finnrut.is`), regular, bold, italic, bold italic

**Character:** A bookish serif at a generous 1.75 line height does the reading. Cooper's soft, heavy curves give each page title and drop cap a theatrical warmth without shouting. PragmataPro is narrow and dense, so long Nix and shell lines fit inside the measure.

### Hierarchy

- **Display** (Cooper 700, 2.3rem, line-height 1.05, discretionary ligatures, balanced wrapping): the page or post `h1`, once per page. 1.85rem under 600px.
- **Headline** (Sabon Next 700, 1.75rem, 1.25): `h2` section heads and post titles on the index. 1.6rem under 600px.
- **Title** (Sabon Next 500, 1.35rem, 1.3): `h3`. `h4`–`h6` step down to 1.2, 1.05 and 1rem at weight 600.
- **Body** (Sabon Next 400, 18px, 1.75; 17px under 600px): all prose. Common ligatures on.
- **Meta** (Sabon Next, 0.85–0.9rem, often italic, Dust Ink): dates, reading time, archive counts, footnotes, the subscribe line.
- **Label** (Sabon Next 600, small caps, 0.04–0.06em tracking): nav, tags, pagination, post navigation, TOC summary, "Notes", "Related", archive years.
- **Code** (PragmataPro, 0.85em): inline code and blocks. **Mono Label** (0.7–0.75rem): code block headers, the copy button, tag counts, handles, dates in Related.
- **Drop cap**: the first letter of the first paragraph of a post, in Cooper 400 with swashes, Footlight Amber, three lines tall (`initial-letter: 3`, with a float fallback).

### Named Rules

**The Playbill Rule.** Cooper sets page titles, the drop cap, the ❦ ornament and the footer heading. It never sets body text, labels, or `h2` and below.

**The Small Caps Label Rule.** Interface labels are Sabon small caps with light tracking, not uppercase and not mono. Mono is for literals: code, filenames, hashes, handles, counts.

## Layout

A single centred column: `max-width: 700px`, padding 2rem 1.5rem 3rem (1.25rem 1rem 2rem under 600px). No sidebar, no grid at page level. Vertical rhythm comes from spacing, not boxes: headings get 3rem above and 1rem below; paragraphs and lists 1.25rem below; sections such as footnotes, Related, Comments, pagination and the footer each start with 2.5–4rem of space and a 1px rule.

The header is a single row of small-caps nav links with the theme toggle pushed to the right, closed by a hairline that the ❦ ornament sits on. Posts on the index are separated by a dashed rule. Small grids appear only inside components: the "Elsewhere" cards (`minmax(14rem, 1fr)`) and the footer directory (`minmax(8rem, 1fr)`, with a container query).

Code blocks stay inside the measure, cap at 28rem tall, and scroll with fading edge hints; line numbers hide under 600px.

### Named Rules

**The Measure Rule.** Everything, including code, lives inside the 700px column. Nothing bleeds out to full width.

## Elevation & Depth

Mostly flat. Depth comes from tone: Wings Shade sitting on Wings Black, bordered by Dark Rule Line. The page background adds two faint fixed radial gradients (a `--glow` at the top, a `--shadow` at the bottom) so the paper feels lit from above rather than flat.

### Shadow Vocabulary

- **Code card** (`inset 0 0 0 1px var(--paper-shade), 0 2px 6px var(--shadow)`): every `pre`, so a block reads as a card resting on the page.
- **Lift** (`0 2px 6px var(--shadow)` plus `translateY(-1px)`): hover on tag chips, Elsewhere cards and the key download pill.
- **Slip** (`drop-shadow(0 2px 2px var(--shadow))`): the torn paper behind a hovered, focused or current footer link.

`--shadow` is `rgba(0,0,0,0.2)` in the dark edition and `rgba(43,37,32,0.06)` in the light.

### Named Rules

**The Paper Casts, Words Don't Rule.** Shadows belong to paper objects (code cards, chips, slips). Text, rules and icons never get one.

## Shapes

Small, soft corners on interface pieces: 2px on alerts, 3px on inline code, images and the copy button, 4px on code blocks, the TOC, search and focus rings, 6px on cards and comments. Chips and the key download link are full pills (999px). The header ornament is a ❦ fleuron; footer slips have a torn right edge (a `clip-path` polygon) and rest at -2deg or 1.5deg. Rules are 1px; the index separator and the slip's inner line are dashed.

## Components

### Navigation

Small-caps Sabon 600 at 0.95rem, 0.06em tracking, Chalk Ink, 1.75rem apart (1.25rem on mobile). Hover turns Footlight Amber with an underline at 0.15em offset. The theme toggle is a 1.05rem outline icon (1.7 stroke) at the right edge, hidden until JS runs; focus gets a 2px amber outline. A skip link drops in from the top-left on focus.

### Text Links

Footlight Amber, 1px underline at 0.12em offset, shifting to Bright Footlight on hover over 150ms. Quieter links (tags, TOC, Related, post titles on the index) drop the underline and the accent until hovered.

### Code Blocks (signature)

A Gruvbox card in the column: header bar with the filename or language in PragmataPro 0.75rem Dust Ink, sticky while scrolling; CSS-counter line numbers; full-line highlights; a ghost **copy button** (transparent, 1px code border, 3px corners) that turns amber with a Wings Shade fill on hover or focus. Max 28rem tall, keyboard-scrollable, with an amber inset focus ring.

### Drop Cap and Ornament (signature)

Every post's first letter is a three-line Cooper swash in Footlight Amber. The header rule carries a centred ❦ in amber on a Wings Black patch. These two marks are the blog's signature; don't add more ornaments around them.

### Tag Chips

On `/tags/`: Wings Shade pills, 1px rule border, small-caps label with a mono count. Hover: amber text and border, background drops to Wings Black, 1px lift with the Lift shadow. In a post's meta, tags are plain Dust Ink small caps with a decorative `#` prefix.

### Table of Contents

A `<details>` above posts with three or more headings: Wings Shade, 1px rule, a 3px amber left stripe, 4px corners, 0.9rem text, small-caps summary.

### Markdown Alerts

3px left border in the alert's hue on its tinted surface, 2px corners, 0.5em 1em padding; first line is bold.

### Cards (Elsewhere, Comments)

Wings Shade on a 1px rule, 6px corners. Elsewhere cards put the name in small caps and the handle hard right in mono; they lift on hover. Comment cards (Mastodon replies loaded client-side) are static.

### Footer Directory

Ported from finnrut.is: a Cooper 1.25rem heading in Dust Ink, then a grid of 44px-tall links. On hover, focus or current page, a torn Wings Shade slip rotates in behind the link (220ms, `cubic-bezier(0.16, 1, 0.3, 1)`), the label's underline thickens to 2px and the text turns Bright Footlight. A dashed rule separates the colophon row and build badge.

## Do's and Don'ts

### Do:

- **Do** ship the dark edition as the first paint for every new reader; light only after the reader picks it.
- **Do** keep both editions in step: every new colour is a custom property defined for dark and light, and both pass pa11y contrast for text and links.
- **Do** use `var(--accent)` for interactive affordances and focus (`2px solid`, 2–3px offset).
- **Do** keep prose at 18px Sabon Next, 1.75 line height, inside the 700px measure.
- **Do** use small-caps Sabon for labels and PragmataPro for literals.
- **Do** wrap motion in a reduced-motion guard; transitions are 150ms colour/opacity, 1px lifts, 220ms slips.

### Don't:

- **Don't** introduce a second accent hue, gradients on components, or neon/terminal styling.
- **Don't** use `#000`, `#fff` or cool greys outside print styles.
- **Don't** set body text, labels or `h2`+ in Cooper.
- **Don't** put shadows on text, rules or icons.
- **Don't** let content break out of the 700px column.
- **Don't** import the main site's tilted prints, ticket stubs or playbill-scale name into post pages; the footer slips are the one shared paper object.

## Known Drift

As of this document, the code still follows the reader's OS setting instead of defaulting to dark: the dark tokens live inside `@media (prefers-color-scheme: dark)` plus `[data-theme="dark"]`, the Gruvbox stylesheets and `theme-color` metas switch on the media query, and the toggle cycles system → light → dark. To match the Ghost Light Rule, make dark the `:root` default, make light the `[data-theme="light"]` override, and drop the "system" step from the toggle.
