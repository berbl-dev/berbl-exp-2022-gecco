{
  description = "berbl-exp-2022-evostar";

  # 2022-01-24
  inputs.nixpkgs.url =
    "github:NixOS/nixpkgs/8ca77a63599ed951d6a2d244c1d62092776a3fe1";
  inputs.berbl-exp = {
    type = "path";
    path = "/home/david/Projekte/berbl/berbl-exp";
  };
  # TODO inputs.berbl.url = "github:dpaetzel/berbl-exp";

  inputs.overlays.url = "github:dpaetzel/overlays";

  outputs = { self, nixpkgs, berbl-exp, overlays }: rec {
    defaultPackage.x86_64-linux =
      with import nixpkgs { system = "x86_64-linux"; };

      let python = python39;
      in python.pkgs.buildPythonPackage rec {
        pname = "berbl-exp-2022-evostar";
        version = "0.1.0";

        src = self;

        # We use pyproject.toml.
        format = "pyproject";

        propagatedBuildInputs = with python.pkgs;
          [ berbl-exp.defaultPackage.x86_64-linux ];

        doCheck = false;

        meta = with lib; {
          description =
            "Experiments for the BERBL paper submitted to Evostar 2022";
          license = licenses.gpl3;
        };
      };
  };
}
# TODO Maybe put export Python version from overlays so we can sync it
# automatedly (currently I have to put python = python39 everywhere, better
# would be something like python = overlay.python or similar).
