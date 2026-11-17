+++
title = "PGP key"
description = "Finn Rutis' OpenPGP key — fingerprint A673 0AC1 3BDD F8FF 95E4 5173 59BF 38D0 5371 C5E9 — for encrypted mail and signature verification."
template = "pgp.html"
sort_by = "date"
+++

If you want to send me encrypted mail, or check that something signed by
`Finn Rutis <me@finnrut.is>` actually came from me, this is the key to use.

## Fingerprint

{{ <pgp_fingerprint /> }}

## Getting it

The easiest way is a web key directory lookup:

```sh
gpg --locate-keys me@finnrut.is
```

Or grab it from a key server:

```sh
gpg --keyserver hkps://keys.openpgp.org \
    --recv-keys A6730AC13BDDF8FF95E4517359BF38D05371C5E9
```

Either way, check that the fingerprint matches the one above before you use
it. If you can, double-check it with me over something that isn't
email.

## Post signatures

Each signed post links to its Markdown source and a detached signature, with
commands for checking them in the post's verification endnote. The signature
covers the source, not the rendered HTML, images or external content.

Before trusting it, check the full fingerprint above through an independent
channel. A "Good signature" from this fingerprint is what you want. A trust or
identity warning only means you haven't certified the key; it isn't a bad
signature. "BAD signature" means the file has changed.

The site doesn't verify anything in your browser; you run the checks yourself.
