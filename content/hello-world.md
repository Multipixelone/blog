---
title: "Hello, world"
date: 2026-06-25
slug: "hello-world"
template: "page.html"
---

This is my long overdue blog where I'll post notes, projects, and things that might eventually be helpful to future surfers of the net.

<!-- more -->

I built this site with [Zola](https://www.getzola.org/), a fast static site generator written in Rust. The build and deployment are handled by Nix flakes and GitHub Pages, which keeps the setup reproducible and low-maintenance. No JavaScript on the front end, minimal styling, and a focus on readable text.

To build the site locally, I run:

```bash
nix build
```

The flake handles Zola and any other dependencies, so the same command works on any machine with Nix installed.

Expect nothing consistant. Expect random ramblings, expect writings that don't make a lot of sense to anyone but me. As long as one person somewhere eventually finds it helpful: that's the bar to clear.
