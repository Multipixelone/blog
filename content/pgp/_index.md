+++
title = "PGP key"
description = "Finn Rutis' OpenPGP key — fingerprint A673 0AC1 3BDD F8FF 95E4 5173 59BF 38D0 5371 C5E9 — for encrypted mail and signature verification."
template = "pgp.html"
sort_by = "date"
+++

Use this key to send me encrypted mail, or to check that something signed by
`Finn Rutis <me@finnrut.is>` really came from me.

## Fingerprint

{{ pgp_fingerprint() }}

This is the only part of the page worth trusting on its own. Key servers can
serve you anything; a fingerprint you have verified out of band cannot be
faked.

The whole listing, as `gpg --list-keys` prints it:

```text
pub   ed25519/0x59BF38D05371C5E9 2026-07-03 [SC]
      Key fingerprint = A673 0AC1 3BDD F8FF 95E4  5173 59BF 38D0 5371 C5E9
uid                   [ unknown] Finn Rutis <me@finnrut.is>
sub   cv25519/0xAAA9C569134AE81A 2026-07-03 [E]
```

## Fetching it

Any of these get you the same key. The web key directory lookup is the least
fussy:

```sh
gpg --locate-keys me@finnrut.is
```

Or pull it from a key server by fingerprint:

```sh
gpg --keyserver hkps://keys.openpgp.org \
    --recv-keys A6730AC13BDDF8FF95E4517359BF38D05371C5E9
```

## Verifying it

Whichever route you took, confirm the fingerprint before you use the key for
anything — and ideally confirm it with me over a channel that isn't email:

```sh
gpg --fingerprint 0x59BF38D05371C5E9
```

The output must match the fingerprint above, character for character. If it
doesn't, you have somebody else's key.
