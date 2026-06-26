---
title: "Hello, world"
date: 2026-06-26
slug: "hello-world"
template: "page.html"
---

This is a small technical blog where I'll post notes, experiments, and things I figure out while working on systems and developer tooling.

<!-- more -->

I built this site with [Zola](https://www.getzola.org/), a fast static site generator written in Rust. The build and deployment are handled by Nix flakes and GitHub Pages, which keeps the setup reproducible and low-maintenance. No JavaScript on the front end, minimal styling, and a focus on readable text.

To build the site locally, I run:

```bash
nix build
```

That's it. The flake handles Zola and any other dependencies, so the same command works on any machine with Nix installed.

What to expect here: short posts about Nix, infrastructure, command-line tools, and whatever else I end up deep in. Nothing polished to a shine — just notes written while they're fresh.
