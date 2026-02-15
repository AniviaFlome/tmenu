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

  # Submodule for an ordered menu entry (preserves insertion order)
  menuItemType = types.submodule {
    options = {
      name = mkOption {
        type = types.str;
        description = "Display label for the menu item.";
      };
      command = mkOption {
        type = types.str;
        description = "Command to execute, or `submenu:NAME` to open a submenu.";
      };
    };
  };

  submenuType = types.submodule {
    options = {
      name = mkOption {
        type = types.str;
        description = "Submenu name (referenced via `submenu:NAME` in menuItems).";
      };
      items = mkOption {
        type = types.listOf menuItemType;
        default = [ ];
        description = "Ordered list of items in this submenu.";
      };
    };
  };

  # Convert a menu entry to a TOML key = value line
  itemToToml = item: "${builtins.toJSON item.name} = ${builtins.toJSON item.command}";

  # Generate [menu] section preserving list order
  menuSection = optionalString (cfg.menuItems != [ ]) (
    "[menu]\n" + concatMapStringsSep "\n" itemToToml cfg.menuItems + "\n"
  );

  # Generate [submenu.*] sections preserving list order
  submenuSections = concatMapStringsSep "\n" (
    sub:
    "[submenu.${builtins.toJSON sub.name}]\n" + concatMapStringsSep "\n" itemToToml sub.items + "\n"
  ) cfg.submenus;

  # The ordered menu/submenu TOML that we generate ourselves
  orderedToml = pkgs.writeText "menu.toml" (menuSection + submenuSections);

  hasConfig =
    cfg.settings != { } || cfg.menuItems != [ ] || cfg.submenus != [ ] || cfg.extraConfig != "";
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
          };
          colors = {
            foreground = "#cdd6f4";
            background = -1;
          };
        }
      '';
      description = ''
        Display, color, and other non-menu settings (serialized as TOML).

        Do **not** put `menu` or `submenu.*` sections here — use
        `menuItems` and `submenus` instead so that item order is preserved.
      '';
    };

    menuItems = mkOption {
      type = types.listOf menuItemType;
      default = [ ];
      example = literalExpression ''
        [
          { name = "Terminal"; command = "alacritty"; }
          { name = "Browser"; command = "firefox"; }
          { name = "System"; command = "submenu:System"; }
        ]
      '';
      description = ''
        Ordered list of main-menu items. Order is preserved in the
        generated config (unlike Nix attrsets, which sort alphabetically).
      '';
    };

    submenus = mkOption {
      type = types.listOf submenuType;
      default = [ ];
      example = literalExpression ''
        [
          {
            name = "System";
            items = [
              { name = "File Manager"; command = "thunar"; }
              { name = "System Monitor"; command = "htop"; }
            ];
          }
        ]
      '';
      description = ''
        Ordered list of submenus. Each submenu has a name and an ordered
        list of items. Reference a submenu from `menuItems` with
        `command = "submenu:NAME"`.
      '';
    };

    extraConfig = mkOption {
      type = types.lines;
      default = "";
      description = ''
        Extra configuration lines to append to the generated TOML configuration.
      '';
    };
  };

  config = mkIf cfg.enable {
    home.packages = [ cfg.package ];

    xdg.configFile."tmenu/config.toml" = mkIf hasConfig {
      source = pkgs.runCommand "config.toml" { } ''
        cat ${tomlFormat.generate "settings.toml" cfg.settings} > $out
        echo >> $out
        cat ${orderedToml} >> $out
        cat ${pkgs.writeText "extra.toml" cfg.extraConfig} >> $out
      '';
    };
  };
}
