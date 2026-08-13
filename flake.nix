{
  description = "Finn Rutis' technical blog — built with Zola";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs }:
    let
      forAllSystems = f: nixpkgs.lib.genAttrs nixpkgs.lib.systems.flakeExposed f;
      pkgsFor = system: nixpkgs.legacyPackages.${system};

      # Commit the site was built from, surfaced by the footer's build badge.
      # `self.rev` needs a clean tree; a dirty one falls back to `self.dirtyRev`
      # ("<rev>-dirty"), and a non-git build to "" — which the template renders
      # as a plain link to the repo. Nix sandboxes the build, so this has to
      # travel in as a derivation attribute rather than an inherited env var.
      commit = self.rev or self.dirtyRev or "";
    in
    {
      packages = forAllSystems (system:
        let pkgs = pkgsFor system; in
        {
          default = pkgs.stdenvNoCC.mkDerivation {
            pname = "finn-blog";
            version = "0.1.0";
            src = ./.;
            SITE_COMMIT = commit;
            nativeBuildInputs = [
              pkgs.zola
              # Open Graph card generation: Pillow draws the cards, woff2 supplies
              # woff2_decompress (Cooper ships as woff2; Pillow needs ttf).
              (pkgs.python3.withPackages (ps: [ ps.pillow ]))
              pkgs.woff2
              # Static search: indexes the built HTML, no service and no runtime.
              pkgs.pagefind
            ];
            # Pages, social cards and search index. Shared with CI's audit job,
            # which builds the same site against a localhost base URL.
            buildPhase = "bash scripts/build.sh $out";
            dontInstall = true;
          };
        });

      devShells = forAllSystems (system:
        let pkgs = pkgsFor system; in
        {
          default = pkgs.mkShellNoCC {
            packages = [
              pkgs.zola
              # pillow: OG cards. feedparser + libxslt: scripts/check_feeds.py.
              # pyyaml: scripts/check_frontmatter.py reads YAML front matter.
              (pkgs.python3.withPackages (ps: [ ps.pillow ps.feedparser ps.pyyaml ]))
              pkgs.woff2
              pkgs.pagefind
              pkgs.libxslt
            ];
            # Give `zola serve` the same footer badge the real build gets from
            # `self.rev` — with the same "-dirty" convention.
            shellHook = ''
              SITE_COMMIT="$(git rev-parse HEAD 2>/dev/null || true)"
              if [ -n "$SITE_COMMIT" ] && ! git diff --quiet HEAD 2>/dev/null; then
                SITE_COMMIT="$SITE_COMMIT-dirty"
              fi
              export SITE_COMMIT
            '';
          };
        });
    };
}
