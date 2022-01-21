{
  description = "berbl-exp-2022-evostar";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
  inputs.berbl-exp = {
    type = "path";
    path = "/home/david/Projekte/berbl/berbl-exp";
  };
  # TODO inputs.berbl.url = "github:dpaetzel/berbl-exp";

  outputs = { self, nixpkgs, berbl-exp }: {

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
