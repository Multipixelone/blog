{
  description = "Finn Rutis' technical blog — built with Zola";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixpkgs-unstable";

  outputs = { self, nixpkgs }:
    let
      forAllSystems = f: nixpkgs.lib.genAttrs nixpkgs.lib.systems.flakeExposed f;
      pkgsFor = system: nixpkgs.legacyPackages.${system};
    in
    {
      packages = forAllSystems (system:
        let pkgs = pkgsFor system; in
        {
          default = pkgs.stdenvNoCC.mkDerivation {
            pname = "finn-blog";
            version = "0.1.0";
            src = ./.;
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
          };
        });
    };
}
