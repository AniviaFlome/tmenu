{
  config,
  lib,
  pkgs,
  ...
}:

with lib;

let
  cfg = config.programs.tmenu;

  iniFormat = pkgs.formats.ini { };

  colorType = types.either types.int (
    types.enum [
      "black"
      "red"
      "green"
      "yellow"
      "blue"
      "magenta"
      "cyan"
      "white"
    ]
  );

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

    extraConfig = mkOption {
      inherit (iniFormat) type;
      default = { };
      example = literalExpression ''
        {
          colors = {
            foreground = "white";
            background = -1;
            selection_foreground = "black";
            selection_background = "cyan";
            prompt_foreground = "blue";
          };
        }
      '';
      description = ''
        Extra configuration for tmenu in INI format.
        See <link xlink:href="https://github.com/AniviaFlome/tmenu"/> for options.
      '';
    };

    colors = {
      foreground = mkOption {
        type = types.nullOr colorType;
        default = null;
        description = "Foreground color for normal text.";
      };

      background = mkOption {
        type = types.nullOr types.int;
        default = null;
        description = "Background color (-1 for terminal default).";
      };

      selectionForeground = mkOption {
        type = types.nullOr colorType;
        default = null;
        description = "Foreground color for selected item.";
      };

      selectionBackground = mkOption {
        type = types.nullOr colorType;
        default = null;
        description = "Background color for selected item.";
      };

      promptForeground = mkOption {
        type = types.nullOr colorType;
        default = null;
        description = "Foreground color for prompt.";
      };
    };

    theme = mkOption {
      type = types.nullOr (
        types.enum [
          "catppuccin-mocha"
          "gruvbox-dark"
          "dracula"
        ]
      );
      default = null;
      description = "Predefined theme to use. Overrides individual color settings.";
    };

    display = {
      centered = mkOption {
        type = types.bool;
        default = true;
        description = "Whether to center the menu on screen.";
      };

      width = mkOption {
        type = types.int;
        default = 60;
        description = "Width of the menu window.";
      };

      height = mkOption {
        type = types.int;
        default = 10;
        description = "Maximum number of items to display at once.";
      };
    };

    menuItems = mkOption {
      type = types.attrsOf types.str;
      default = { };
      example = literalExpression ''
        {
          "Terminal" = "alacritty";
          "Browser" = "firefox";
          "Text Editor" = "nvim";
          "Development" = "submenu:Development";
        }
      '';
      description = ''
        Menu items to display. Keys are labels shown in the menu,
        values are commands to execute when selected.
        Use "submenu:NAME" to link to a submenu.
      '';
    };

    submenu = mkOption {
      type = types.attrsOf (types.attrsOf types.str);
      default = { };
      example = literalExpression ''
        {
          Development = {
            "Code Editor" = "code";
            "Terminal" = "alacritty --working-directory ~/projects";
          };
          System = {
            "File Manager" = "thunar";
            "System Monitor" = "htop";
          };
        }
      '';
      description = ''
        Submenus for tmenu. Each attribute set becomes a [submenu.NAME] section.
        Keys are labels, values are commands to execute.
      '';
    };
  };

  config = mkIf cfg.enable {
    home.packages = [ cfg.package ];

    xdg.configFile."tmenu/config.ini" =
      mkIf (cfg.extraConfig != { } || cfg.colors != { } || cfg.theme != null || cfg.menuItems != { } || cfg.submenu != { })
        (
          if cfg.theme != null then
            {
              source = "${cfg.package}/themes/${cfg.theme}.ini";
            }
          else
            let
              colorSettings = filterAttrs (_: v: v != null) {
                inherit (cfg.colors) foreground;
                inherit (cfg.colors) background;
                selection_foreground = cfg.colors.selectionForeground;
                selection_background = cfg.colors.selectionBackground;
                prompt_foreground = cfg.colors.promptForeground;
              };

              displaySettings = {
                inherit (cfg.display) centered;
                inherit (cfg.display) width;
                inherit (cfg.display) height;
              };

              submenuSettings = mapAttrs' (name: items: nameValuePair "submenu.${name}" items) cfg.submenus;

              finalSettings =
                cfg.extraConfig
                // optionalAttrs (colorSettings != { }) {
                  colors = (cfg.extraConfig.colors or { }) // colorSettings;
                }
                // {
                  display = (cfg.extraConfig.display or { }) // displaySettings;
                }
                // optionalAttrs (cfg.menuItems != { }) {
                  menu = cfg.menuItems;
                }
                // submenuSettings;
            in
            {
              source = iniFormat.generate "tmenu-config.ini" finalSettings;
            }
        );
  };
}
