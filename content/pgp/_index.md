+++
title = "PGP key"
description = "Finn Rutis' OpenPGP key — fingerprint A673 0AC1 3BDD F8FF 95E4 5173 59BF 38D0 5371 C5E9 — for encrypted mail and signature verification."
template = "pgp.html"
sort_by = "date"
+++

If you want to send me encrypted mail, or check that something signed by
`Finn Rutis <me@finnrut.is>` actually came from me, this is the key to use.

## Fingerprint

{{ pgp_fingerprint() }}

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
