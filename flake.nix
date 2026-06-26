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
            nativeBuildInputs = [ pkgs.zola ];
            buildPhase = "zola build --output-dir $out";
            dontInstall = true;
          };
        });

      devShells = forAllSystems (system:
        let pkgs = pkgsFor system; in
        {
          default = pkgs.mkShellNoCC {
            packages = [ pkgs.zola ];
          };
        });
    };
}
