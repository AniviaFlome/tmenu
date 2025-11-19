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

    settings = mkOption {
      type = tomlFormat.type;
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
            Applications = "submenu:Applications";
          };
          submenu.Applications = {
            Browser = "firefox";
            Editor = "nvim";
            "File Manager" = "thunar";
          };
        }
      '';
      description = ''
        Configuration for tmenu in TOML format.
        This uses a freeform type allowing any valid TOML structure.
        See <link xlink:href="https://github.com/AniviaFlome/tmenu"/> for available options.
      '';
    };

    # Legacy structured options for backward compatibility
    extraConfig = mkOption {
      inherit (tomlFormat) type;
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
        Extra configuration for tmenu in TOML format.
        This is merged with 'settings'. Use 'settings' for the main configuration.
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

    xdg.configFile."tmenu/config.toml" =
      mkIf (cfg.settings != { } || cfg.extraConfig != { } || cfg.menuItems != { } || cfg.submenu != { })
        (
          let
            # Build config from structured options
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
              theme = cfg.display.theme.name;
              theme_dir = cfg.display.theme.dir;
              figlet = cfg.display.figlet.enable;
              figlet_font = cfg.display.figlet.font;
            };

            submenuSettings = mapAttrs' (name: items: nameValuePair "submenu.${name}" items) cfg.submenu;

            # Merge settings: settings takes priority, then extraConfig, then structured options
            finalSettings =
              # Start with structured options (lowest priority)
              (optionalAttrs (cfg.display.theme.name == "") {
                colors = colorSettings;
              })
              // {
                display = displaySettings;
              }
              // optionalAttrs (cfg.menuItems != { }) {
                menu = cfg.menuItems;
              }
              // submenuSettings
              # Then overlay extraConfig
              // cfg.extraConfig
              # Finally overlay settings (highest priority)
              // cfg.settings;
          in
          {
            source = tomlFormat.generate "tmenu-config.toml" finalSettings;
          }
        );
  };
}
