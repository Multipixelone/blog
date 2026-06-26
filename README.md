# blog.finnrut.is

Finn Rutis' technical writings. A minimal markdown blog built with [Zola](https://www.getzola.org/) and [Nix flakes](https://nixos.wiki/wiki/Flakes), deployed to GitHub Pages.

## Develop

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

## Structure

```
content/    markdown posts and pages
templates/  Tera HTML templates (hand-rolled minimal theme)
static/     CNAME, robots.txt, style.css, 404.html
zola.toml   site configuration
flake.nix   Nix flake (devShell + site build derivation)
```

## License

See [LICENSE](LICENSE).
