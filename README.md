<h1 align="center">blog.finnrut.is</h1>
<div align="center">

[![Build](https://img.shields.io/github/actions/workflow/status/Multipixelone/blog/ci.yml?style=for-the-badge&logo=github&label=build&color=a6e3a1&labelColor=313244&logoColor=cdd6f4)](https://github.com/Multipixelone/blog/actions)
[![Deploy](https://img.shields.io/github/actions/workflow/status/Multipixelone/blog/deploy.yml?style=for-the-badge&logo=githubactions&label=deploy&color=cba6f7&labelColor=313244&logoColor=cdd6f4)](https://github.com/Multipixelone/blog/actions)
[![License](https://img.shields.io/github/license/Multipixelone/blog?style=for-the-badge&logo=gnu&color=b4befe&labelColor=313244&logoColor=cdd6f4)](LICENSE)
[![Pages](https://img.shields.io/website?url=https%3A//blog.finnrut.is&style=for-the-badge&logo=githubpages&label=pages&color=fab387&labelColor=313244&logoColor=cdd6f4)](https://blog.finnrut.is)
![Zola](https://img.shields.io/badge/zola-static_site-94e2d5?style=for-the-badge&logo=zola&labelColor=313244&logoColor=cdd6f4)
![Nix](https://img.shields.io/badge/nix-flakes-89b4fa?style=for-the-badge&logo=nixos&labelColor=313244&logoColor=cdd6f4)

</div>

Finn Rutis' technical writings. A minimal markdown blog built with [Zola](https://www.getzola.org/) for static site generation and [Nix flakes](https://nixos.wiki/wiki/Flakes) for reproducible builds, deployed to GitHub Pages on every push to `main`.

## Develop

Requires a Nix environment with flakes enabled.

```sh
nix develop          # enter dev shell with zola
zola serve           # local server at http://localhost:1111
```

Or with [direnv](https://direnv.net/): allow the `.envrc` once, then `zola serve`.

## Build

```sh
nix build .#default  # outputs the static site to ./result
```

## Deploy

Pushes to `main` trigger the `Deploy` workflow, which builds the site and deploys to GitHub Pages at [blog.finnrut.is](https://blog.finnrut.is).

### One-time GitHub setup

In repo Settings → Pages, set **Source** to **GitHub Actions** (not "Deploy from a branch").

### Custom domain

`static/CNAME` contains `blog.finnrut.is`. Point DNS `blog.finnrut.is` → `Multipixelone.github.io` (CNAME record).

## CI/CD

The `CI` workflow runs on every push to non-`main` branches and on pull requests. The `Deploy` workflow runs only on pushes to `main` and publishes the built site to GitHub Pages.

The Nix flake runs these checks automatically:

- **nix flake check** — validates the flake and its outputs
- **site build** — the static site builds successfully from `.#default`

## Profile links

The footer's icon row and the About page's "Elsewhere" list are both rendered
from `[[extra.profiles]]` in `zola.toml`, so they can't drift apart. To add a
place, append a block there; if its `icon` isn't one `templates/macros/icons.html`
already draws, add an arm to that macro (anything unrecognised falls back to a
generic link glyph). Drop `footer = true` to list somewhere on About only.

## Feeds

Both formats are generated from the same page list, using the local templates in
`templates/{atom,rss}.xml` rather than Zola's built-ins (the built-ins title the
channel "Finn Rutis - Home" and omit per-item categories):

| Feed | Site-wide | Per tag |
| --- | --- | --- |
| RSS 2.0 | `/rss.xml` | `/tags/<slug>/rss.xml` |
| Atom | `/atom.xml` | `/tags/<slug>/atom.xml` |

All four are advertised with `<link rel="alternate">` on the pages they belong
to, so readers autodiscover them from the URL alone.

## Comments

There is no comment system. A post gets a comment section by pointing at its
announcement thread on Mastodon:

```yaml
extra:
  mastodon_status: "https://pony.social/@tunnelmaker/113456789012345678"
```

Without the key the section doesn't render at all. With it, the page ships a
plain link to the thread, and a script upgrades that in place by reading the
thread's public replies from the instance's API (`/api/v1/statuses/:id` and
`/api/v1/statuses/:id/context`). Reply bodies are rebuilt node by node against
a tag allowlist rather than assigned to `innerHTML`, content warnings stay
collapsed, and avatars are not loaded — they would mean image requests to every
instance a replier happens to be on.

Moderation is whatever the instance already does: delete a reply there and it
disappears here on the next load.

## Build provenance

The footer carries a "built from this repo at `<sha>`" badge linking to the exact
commit on GitHub. The revision travels in through `SITE_COMMIT`, which
`flake.nix` sets from the flake's own git revision (`self.rev`, or
`self.dirtyRev` on a dirty tree) — Nix sandboxes the build, so an inherited env
var wouldn't survive. Both workflows check out with `fetch-depth: 0` so that
revision resolves.

Nothing breaks without it: under `zola serve` and in ad-hoc builds `SITE_COMMIT`
is unset and the badge degrades to a plain link to the repository.

## PGP

`/pgp/` publishes the key's fingerprint, instructions to fetch and verify it, and
the armored key from `static/pgp.asc`. To rotate or re-export the key:

```sh
gpg --armor --export 0x59BF38D05371C5E9 > static/pgp.asc
```

That file is read optionally — the download button and key block appear only
when it exists, so removing it degrades the page to the fingerprint and the
fetch instructions instead of leaving a dead download link. The filename and the
fingerprint live in `[extra.pgp]` in `zola.toml`, which also feeds the About
page's fingerprint line.

## Social cards

Per-post Open Graph cards (1200×630) are generated at build time by
`scripts/gen_og_cards.py`, which reads the JSON-LD each post emits and draws an
"accent band" card with Pillow. Cooper (the only build-available font — Sabon Next
is served from R2 and absent from CI) is decompressed woff2→ttf via `woff2_decompress`
first. Output lands at `/og/<slug>.png`, with a site-wide `/og.png` default for the
homepage, tags, and about pages.

<details>
<summary>Project structure</summary>

```
content/               markdown posts and pages
templates/             Tera HTML templates (hand-rolled minimal theme), incl. 404.html
templates/atom.xml     feed templates, overriding Zola's built-ins
templates/rss.xml
templates/macros/      inline SVG icon set (footer, About, PGP page)
templates/shortcodes/  markdown-callable snippets
static/                CNAME, robots.txt, style.css, fonts, favicon
scripts/               build-time helpers (Open Graph card generator)
zola.toml              site configuration
flake.nix              Nix flake (devShell + site build derivation)
```

</details>

## License

See [LICENSE](LICENSE).