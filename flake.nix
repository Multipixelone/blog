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
            ];
            buildPhase = ''
              zola build --output-dir $out

              # Decompress the committed Cooper fonts (woff2 -> ttf) for Pillow.
              mkdir -p fonts-ttf
              for f in Cooper-Black Cooper-Bold Cooper-Regular; do
                cp static/fonts/cooper/$f.woff2 fonts-ttf/
                woff2_decompress fonts-ttf/$f.woff2
              done

              python3 scripts/gen_og_cards.py \
                --out $out --font-dir fonts-ttf \
                --title "Finn Rutis" --base-url "https://blog.finnrut.is/"
            '';
            dontInstall = true;
          };
        });

      devShells = forAllSystems (system:
        let pkgs = pkgsFor system; in
        {
          default = pkgs.mkShellNoCC {
            packages = [
              pkgs.zola
              (pkgs.python3.withPackages (ps: [ ps.pillow ]))
              pkgs.woff2
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
