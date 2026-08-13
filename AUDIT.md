# Site Audit — blog.finnrut.is

Improvement angles for everything _around_ the content. The baseline here is
already unusually strong (build-time OG cards, JSON-LD, dual feeds with per-tag
variants, pa11y + Lighthouse in CI, WKD-discoverable PGP key), so this is a
"good → great" list, not a fix-it list. Ordered roughly by impact within each
section.

---

## 1. Social cards

The generated cards (accent band, Cooper Black title, meta line) are clean and
on-brand, but they're anonymous — nothing on the card says where it came from.

- [ ] **Put the site identity on the card.** Add `blog.finnrut.is` (or a small
      wordmark) in the bottom-right corner, opposite the meta line. When a card
      gets screenshotted and reshared without the link, the attribution should
      travel with it. One `draw.text` anchored `rb` in `scripts/gen_og_cards.py`.
- [ ] **Use the description.** The JSON-LD the script already parses contains
      `description`; a 1–2 line muted summary under the title would make cards for
      short titles (lots of empty middle space today) feel composed instead of
      sparse. Wrap at ~2 lines, drop it when the title needs 4 lines.
- [ ] **Tag chips.** `keywords` is also already in the JSON-LD. Two or three
      small rounded-rect chips (`#nix #flakes`) near the meta line add texture and
      say what the post is about at a glance.
- [ ] **Per-tag and section cards.** Tag pages, `/tags/`, and `/about/` all
      fall back to the generic `og.png`. The script already loops the built output —
      render a card per taxonomy term (`#nix — 3 posts`) and one for About. Tag
      URLs get shared more than you'd think when someone says "their Nix posts".
- [ ] **A card-regression check in CI.** The script only warns when _zero_
      cards are generated. Assert instead that every `BlogPosting` page produced
      `og/<slug>.png`, and fail the build otherwise — a silent regex mismatch after
      a Zola upgrade would currently ship posts with 404 card URLs.
- [ ] **Larger meta line.** At preview sizes (~500px wide in most timelines)
      the 30px meta line is on the edge of legibility. 34–36px still reads as
      "muted" but survives the downscale.

## 2. Fediverse & IndieWeb integration

You're on Mastodon and already emit `rel="me"` — the remaining pieces are
cheap and visible.

- [ ] **`fediverse:creator` meta tag.** Mastodon (4.3+) shows a "More from
      @tunnelmaker@pony.social" author byline on link previews when the page
      carries `<meta name="fediverse:creator" content="@tunnelmaker@pony.social">`.
      One line in `base.html`; derive it from the Mastodon entry in
      `config.extra.profiles` so it can't drift.
- [ ] **Mastodon-thread comments.** The classic static-site pattern: add an
      optional `extra.mastodon_status` front-matter key holding the toot URL for a
      post's announcement; the template renders "Discuss on Mastodon" (zero JS) or,
      fancier, fetches the thread's replies client-side from the pony.social API
      and renders them as a comment section. Gives the blog a social surface
      without any comment infrastructure.
- [ ] **Microformats2.** Add `h-entry` / `h-card` / `p-author` / `dt-published`
      classes to `page.html` and the homepage list. Invisible to humans, but makes
      posts parseable by webmention receivers, indie readers, and Bridgy.
- [ ] **Webmentions.** Register at webmention.io, add the
      `<link rel="webmention">` endpoint tag, and (optionally, later) pull the
      mention JSON at build time to render "N mentions" under posts. Pairs with
      Bridgy to backfeed Mastodon favs/boosts as mentions.

## 3. SEO & structured data

The head is already better than most commercial sites. What's left:

- [x] **Fix metadata drift in existing posts.** Concrete instances:
  - `content/fractured-mind.md` — the `description` ("Building a Nix-flake
    resume generator…") and `cover_alt` describe the _resume-gen_ post, not
    this one. Since `description` feeds the meta description, OG description,
    JSON-LD, _and_ the feed summary fallback, this is the highest-leverage SEO
    fix in the repo.
  - `content/nixos-for-who.md` — `cover_alt` references an old title
    ("…and I want more!").
    A tiny CI guard could catch this class of bug: warn when `cover_alt` doesn't
    contain the post title.
- [ ] **Derive `sameAs` from profiles.** The `Person` JSON-LD in `page.html`
      hardcodes only the GitHub URL. Loop `config.extra.profiles` (skip mailto /
      no-URL entries) so Google/knowledge-graph consumers see Mastodon, LinkedIn,
      etc. Same for a `Person` block on the About page itself, which currently has
      no JSON-LD despite being the canonical "who is this" URL.
- [ ] **Use `updated` front-matter when you revise posts.** The machinery
      (`article:modified_time`, `dateModified`, feed `<updated>`, sitemap lastmod)
      all keys off `page.updated` and it's never set. Worth adopting as a habit for
      substantive edits — freshness signals are real for evergreen technical posts.
- [ ] **Related-posts block.** Internal linking is currently only prev/next
      (chronological). A "related" section — pick 2–3 posts sharing the most tags —
      is easy in Tera and does more for both readers and crawl depth than
      chronology does.
- [ ] **Decide an AI-crawler policy in `robots.txt`.** Currently allow-all.
      Either stance is fine, but it should be a decision, not a default (GPTBot,
      ClaudeBot, CCBot, Google-Extended each honor their own UA rules).
- [ ] **`og:image:type` (`image/png`)** on the image blocks — trivial, a few
      scrapers use it to skip a HEAD request.

## 4. Feeds

- [ ] **Style the feeds with XSL.** Clicking the footer RSS icon today shows
      raw XML — the single most common "is this broken?" moment for non-feed
      users. An `<?xml-stylesheet?>` pointing at a small XSLT (see the
      "pretty-feed-v3" pattern) renders a human page explaining what a feed is,
      listing recent posts, with the copyable URL. Works for both Atom and RSS
      templates since they're already local overrides.
- [ ] **Consider full-content feeds.** Entries are summary-only by design
      ("mirrors the homepage"). Feed readers are your most loyal audience, and
      making them click through is a tax that mostly sheds readers. If you want a
      middle path: full `<content>` plus the summary — Atom supports both on one
      entry.
- [ ] **Feed icon distinction on About.** Both RSS and Atom rows use the same
      icon; fine, but the _homepage_ has no visible feed affordance at all (footer
      only). A one-liner under the intro ("Subscribe via RSS") is worth testing.

## 5. Performance & delivery

Fonts are the whole story here; the rest of the page is effectively free.

- [ ] **Subset the webfonts.** Sabon Regular alone is ~98KB and you ship 4
      Sabon weights + 4 PragmataPro styles + 3 Coopers. `pyftsubset`
      (fonttools) with `--unicodes=U+0000-00FF,U+2013-2014,U+2018-201D,U+2026` and
      layout-feature pruning typically cuts serif woff2s by 50–70%. This is the
      biggest byte win available on the site.
- [ ] **Load PragmataPro styles on demand, or drop unused faces.** All four
      mono styles are declared site-wide, but pages without code blocks never use
      them (and `font-display: swap` means they still may be fetched depending on
      content). Verify with DevTools coverage which weights actually appear —
      bold-italic mono is almost certainly never rendered.
- [ ] **Preload the mono font on post pages only.** You preload Sabon Regular
      globally (good). Posts that open with a code block get a late mono swap;
      a conditional preload in `page.html` when the post has code would remove it.
      (Zola doesn't expose "has code blocks" directly — a cheap heuristic is a
      front-matter flag or just preloading mono on all `page.html` renders.)
- [x] **Front the site with Cloudflare for headers + cache control.** GitHub
      Pages hard-codes `cache-control: max-age=600` and can't set security
      headers. The DNS zone is already... yours, and fonts are already on R2 —
      proxying through Cloudflare gets you long-lived immutable caching for
      `/fonts/`, `/og/`, and CSS, plus real `Content-Security-Policy`,
      `X-Content-Type-Options`, and `Referrer-Policy` headers (the only Lighthouse
      best-practice items you structurally can't fix on Pages today).
      Alternatively CSP can ship as a `<meta http-equiv>` tag now, losing only
      `frame-ancestors`.
- [ ] **Self-host check for `og.png` weight.** PNG cards with flat color
      compress well, but verify sizes; if any card crosses ~150KB, quantize with
      `optimize=True` + `img.quantize(64)` — flat-color cards survive palette mode
      perfectly and often shrink 3–4×.

## 6. Site features

- [ ] **Search.** Five posts don't need it yet, but the nice-fit option for
      this stack is [Pagefind](https://pagefind.app/) — runs over the built output
      (drop it into the flake's `buildPhase` like the OG script), fully static,
      ~10KB JS lazily loaded only when the search box is used. Alternatively
      Zola's built-in `build_search_index` with elasticlunr, but Pagefind's index
      scales better and the UI is nicer.
- [ ] **Heading anchors.** `insert_anchor_links = "heading"` (or `= "right"`)
      in `[markdown]` gives every heading a copyable link — table stakes for
      technical posts people cite. Style the `.zola-anchor` to appear on hover.
- [ ] **Table of contents for long posts.** `nixos-for-who` is 7KB of prose;
      a `page.toc`-driven `<details>` TOC above the fold (rendered only when the
      post has 3+ headings) costs ~10 template lines.
- [ ] **Archive/all-posts view.** With `paginate_by = 10`, older posts fall off
      the homepage into pagination limbo. A compact `/archive/` (year → title list,
      no summaries) is the page long-time readers actually bookmark.
- [ ] **Footnote back-links & styling.** If/when posts use footnotes, Zola's
      default markup benefits from `[markdown] bottom_footnotes = true` plus a
      return-arrow style. Cheap to do now, before the first footnoted post.
- [ ] **Privacy-respecting analytics.** Right now you have zero signal on
      readership. GoatCounter (free, no-cookie, ~3KB script or even pixel-only
      mode) fits the site's ethos; even just Cloudflare's server-side analytics
      (if you adopt §5's proxying) answers "did anyone read this" without any
      client JS.
- [ ] **`security.txt`.** You publish a PGP key and care about verifiable
      contact — `/.well-known/security.txt` (RFC 9116) is the machine-readable
      version: `Contact:`, `Encryption: https://blog.finnrut.is/pgp.asc`,
      `Expires:`, and sign the file with the key itself. One static file; GitHub
      Pages serves `.well-known/` fine.

## 7. CI / infrastructure polish

- [ ] **Scheduled link checking.** lychee runs only on push, so external links
      rot silently between posts. Add a weekly `schedule:` workflow that runs
      lychee against the _built site_ (not just markdown) and opens an issue on
      failure (`lycheeverse/lychee-action` has `createIssue` built in).
- [ ] **PR preview deploys.** CI builds the site but reviewers can't see it.
      Cheapest: upload the `--base-url`-rewritten build as an artifact and link it
      in a PR comment. Nicer: Cloudflare Pages preview deployments (free, automatic
      per-PR URLs) — and it would replace GitHub Pages entirely, unlocking §5's
      headers as a side effect.
- [ ] **Feed validation in CI.** The Atom/RSS templates are hand-maintained
      and the comments show you've already been bitten by byte-level XML issues.
      `xmllint --noout` plus the W3C feed validator's CLI cousin
      (`feedvalidator`/`flycheck` via a Python step) would lock in correctness.
- [ ] **OG card visual regression.** Store a reference render of one card and
      compare with a perceptual hash in CI — font or Pillow bumps in nixpkgs can
      shift rendering without failing anything today.
- [ ] **Lighthouse URL coverage.** The audit hits `/`, one post, and `/tags/` —
      add `/about/` (custom template, icon grid) and one _tag_ page, the two
      templates currently never audited.

## 8. Housekeeping (small, do anytime)

- [x] Two posts (`fractured-mind.md`, `ramblings-about-theodicy.md`) have
      uncommitted local modifications — commit or stash so deploys match the tree.
- [ ] `--base-url` flag in `gen_og_cards.py` is declared "(unused)" — drop it
      or use it, half-dead flags confuse future-you.
- [ ] `author_twitter = "@Multipixelone"` powers `twitter:site`/`creator`;
      if X stops mattering to you, the tags are harmless but the profile row +
      meta could be retired together.
- [ ] Consider `humans.txt` for the same audience as the build badge — people
      who view source. You clearly enjoy this class of easter egg.
