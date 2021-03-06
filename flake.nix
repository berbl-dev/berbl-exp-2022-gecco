{
  description = "berbl-exp-2022-gecco";

  inputs.berbl-exp.url = "github:berbl-dev/berbl-exp";

  outputs = { self, berbl-exp }: rec {
    defaultPackage.x86_64-linux =
      with import berbl-exp.inputs.berbl.inputs.nixpkgs { system = "x86_64-linux"; };

      let python = python39;
      in python.pkgs.buildPythonPackage rec {
        pname = "berbl-exp-2022-gecco";
        version = "0.1.0";

        src = self;

        # We use pyproject.toml.
        format = "pyproject";

        propagatedBuildInputs = with python.pkgs;
          [ berbl-exp.defaultPackage.x86_64-linux ];

        doCheck = false;
      };
  };
}
# TODO Maybe put export Python version from overlays so we can sync it
# automatedly (currently I have to put python = python39 everywhere, better
# would be something like python = overlay.python or similar).
