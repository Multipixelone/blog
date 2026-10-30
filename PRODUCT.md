# Product

<!-- impeccable:product-schema 1 -->

## Platform

web

## Users

Mostly Finn and their friends. The blog is a personal accountability journal: Finn writes to turn chaotic thoughts into something permanent, and friends read along. Strangers arriving from Mastodon, search, RSS or finnrut.is are welcome but secondary; the site should never be tuned for them at the expense of the writing feeling personal.

## Product Purpose

blog.finnrut.is is Finn Rutis' writing room. It holds technical notes (Nix, infrastructure, software, small projects like Album Graph), essays on AI ethics, and personal writing about the human condition, faith and the stories people tell each other. Success is that Finn keeps writing and publishing, and that a post is comfortable to read start to finish, including long technical ones with code.

## Positioning

The only place where a musical theatre performer writes long-form, first-person, about both Nix flakes and theodicy. The voice is casual and candid ("Hope you enjoy :-)", "a theatre kid who works w/ AI has a couple opinions abt robots"); posts are personal, not a portfolio or a tutorial mill.

## Operating Context

- Static site built with Zola from Markdown in `content/`, with Tera templates in `templates/` and hand-written CSS in `static/style.css`.
- Built reproducibly with Nix flakes and deployed to GitHub Pages on every push to `main`.
- CI runs accessibility checks (pa11y) and spell checks (typos).
- Posts include long prose, code blocks, Markdown alerts (note, tip, important, warning, caution), tags and dated archives.
- Social cards are rendered dark, at 2x.

## Capabilities and Constraints

- Reader-facing theme toggle already exists and persists the reader's choice.
- **Dark is the default.** Every reader gets the dark theme on first paint regardless of OS preference. The light theme remains available through the toggle and is remembered once chosen.
- No accounts, comments or forms.
- Licensed fonts (Sabon Next, PragmataPro) load from `fonts.finnrut.is`; Cooper is local OFL.

## Brand Commitments

- Same person as finnrut.is (Finn Rutis, they/them), presented as a sibling site: recognisably the same identity, but its own room for writing rather than the performer's callboard.
- `MAIN_WEBSITE.md` is the design record of finnrut.is. This blog was the original source of that design; the two have since diverged. Future design work should keep what works on the blog and bring it into a more consistent brand identity with `MAIN_WEBSITE.md`.
- Binding difference from the main site: the main site is light only; this blog is **dark by default** with an optional light theme. The main site's "Daylight Rule" and its rejection of dark mode do not apply here.
- Footer has already been ported from the main website.

## Evidence on Hand

- Published posts: "Ramblings About Theodicy", "Fractured Mind: Who can I talk to about this", "Exploring my Library: Album Graph", plus the About page.
- `AUDIT.md` records a prior design/accessibility audit.

## Accessibility & Inclusion

Automated pa11y checks run in CI; both themes must stay readable and pass contrast for body text and links.
