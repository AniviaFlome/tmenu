{
  description = "tmenu - A dmenu-like command executor for the terminal";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-unstable";
    treefmt-nix.url = "github:numtide/treefmt-nix";
  };

  outputs =
    {
      self,
      nixpkgs,
      treefmt-nix,
      ...
    }:
    let
      systems = [
        "x86_64-linux"
        "aarch64-linux"
        "x86_64-darwin"
      ];
      eachSystem = f: nixpkgs.lib.genAttrs systems (system: f system nixpkgs.legacyPackages.${system});

      treefmtEval = eachSystem (_system: pkgs: treefmt-nix.lib.evalModule pkgs ./treefmt.nix);
    in
    {
      packages = eachSystem (
        _system: pkgs: {
          default = pkgs.callPackage ./package.nix { };
        }
      );

      apps = eachSystem (
        system: _pkgs: {
          default = {
            type = "app";
            program = "${self.packages.${system}.default}/bin/tmenu";
          };
        }
      );

      formatter = eachSystem (system: _pkgs: treefmtEval.${system}.config.build.wrapper);

      checks = eachSystem (
        system: _pkgs: {
          formatting = treefmtEval.${system}.config.build.check self;
        }
      );

      homeManagerModules = {
        tmenu = import ./nix/home-manager-module.nix;
        default = self.homeManagerModules.tmenu;
      };

      nixosModules = {
        tmenu = import ./nix/nixos-module.nix;
        default = self.nixosModules.tmenu;
      };
    };
}
