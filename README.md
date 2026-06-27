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

<details>
<summary>Project structure</summary>

```
content/    markdown posts and pages
templates/  Tera HTML templates (hand-rolled minimal theme)
static/     CNAME, robots.txt, style.css, 404.html
zola.toml   site configuration
flake.nix   Nix flake (devShell + site build derivation)
```

</details>

## License

See [LICENSE](LICENSE).