{
  config,
  lib,
  pkgs,
  ...
}:

with lib;

let
  cfg = config.programs.tmenu;
  tomlFormat = pkgs.formats.toml { };
in
{
  options.programs.tmenu = {
    enable = mkEnableOption "dmenu for terminal";

    package = mkOption {
      type = types.package;
      default = pkgs.callPackage ./package.nix { };
      defaultText = literalExpression "pkgs.tmenu";
      description = "The tmenu package to use.";
    };

    settings = mkOption {
      inherit (tomlFormat) type;
      default = { };
      example = literalExpression ''
        {
          display = {
            centered = true;
            width = 60;
            height = 10;
            title = "Main Menu";
            theme = "catppuccin-mocha";
            figlet = false;
            figlet_font = "standard";
          };
          menu = {
            Terminal = "alacritty";
            Browser = "firefox";
            Editor = "nvim";
          };
          # You can define any custom submenus
          "submenu.MyCustomSubmenu" = {
            "Custom Item 1" = "command1";
            "Custom Item 2" = "command2";
          };
        }
      '';
      description = ''
        Configuration for tmenu in TOML format.

        Accepts any valid TOML structure. You can define custom menus, submenus,
        colors, and display settings - the freeform type auto-generates all options.
      '';
    };
  };

  config = mkIf cfg.enable {
    home.packages = [ cfg.package ];

    xdg.configFile."tmenu/config.toml" = mkIf (cfg.settings != { }) {
      source = tomlFormat.generate "config.toml" cfg.settings;
    };
  };
}
