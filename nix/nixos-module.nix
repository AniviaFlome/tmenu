{ config, lib, pkgs, ... }:

with lib;

let
  cfg = config.programs.tmenu;
in
{
  options.programs.tmenu = {
    enable = mkEnableOption "tmenu, a dmenu-like command executor for the terminal";
    
    package = mkOption {
      type = types.package;
      default = pkgs.callPackage ./package.nix { };
      defaultText = literalExpression "pkgs.tmenu";
      description = "The tmenu package to use.";
    };
  };
  
  config = mkIf cfg.enable {
    environment.systemPackages = [ cfg.package ];
  };
}
