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
        type = colorType;
        default = 7;
        description = "Foreground color for normal text.";
      };

      background = mkOption {
        type = types.int;
        default = -1;
        description = "Background color (-1 for terminal default).";
      };

      selectionForeground = mkOption {
        type = colorType;
        default = 0;
        description = "Foreground color for selected item.";
      };

      selectionBackground = mkOption {
        type = colorType;
        default = 6;
        description = "Background color for selected item.";
      };

      promptForeground = mkOption {
        type = colorType;
        default = 4;
        description = "Foreground color for prompt.";
      };
    };

    theme = {
      name = mkOption {
        type = types.str;
        default = "";
        description = "Predefined theme to use. Leave empty to use manual colors.";
      };

      dir = mkOption {
        type = types.str;
        default = "";
        description = "Directory path for custom themes.";
      };
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

      title = mkOption {
        type = types.str;
        default = "";
        description = "Menu title to display at the top.";
      };
    };

    figlet = {
      enable = mkOption {
        type = types.bool;
        default = false;
        description = "Enable ASCII art title with pyfiglet.";
      };

      font = mkOption {
        type = types.str;
        default = "standard";
        description = "Font to use for figlet (e.g., standard, slant, banner).";
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
      mkIf (cfg.extraConfig != { } || cfg.menuItems != { } || cfg.submenu != { })
        (
          let
            colorSettings = {
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
              inherit (cfg.display) title;
              theme = cfg.theme.name;
              figlet = cfg.figlet.enable;
              figlet_font = cfg.figlet.font;
              themes_dir = cfg.theme.dir;
            };

            submenuSettings = mapAttrs' (name: items: nameValuePair "submenu.${name}" items) cfg.submenu;

            finalSettings =
              cfg.extraConfig
              // {
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
