{
  projectRootFile = "flake.nix";

  programs = {
    nixfmt.enable = true;
    prettier.enable = true;
    black.enable = true;
    isort.enable = true;
    deadnix.enable = true;
    statix.enable = true;
  };
}
