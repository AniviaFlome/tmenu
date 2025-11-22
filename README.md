# tmenu

Vibe coded for personal use. Use it if you want.

## Installation

tmenu is packaged as a standard Python package with `pyproject.toml`.

### Option 1: Using Nix Flakes (Recommended for NixOS users)

Add to your flake inputs:

```nix
{
  inputs.tmenu.url = "github:AniviaFlome/tmenu";
}
```

Then either:

**A. Using Home Manager** (recommended):

```nix
{
  imports = [ inputs.tmenu.homeManagerModules.default ];

  programs.tmenu = {
    enable = true;

    settings = {
      display = {
        centered = true;
        width = 60;
        height = 10;
        title = "Tmenu";
        theme = "catppuccin-mocha";
        figlet = false;
      };

      menu = {
        Terminal = "alacritty";
        Browser = "firefox";
        System = "submenu:System";
      };

      "submenu.System" = {
        "File Manager" = "thunar";
        "System Monitor" = "htop";
      };
    };
  };
}
```

**B. Using NixOS** (system-wide):

```nix
{
  imports = [ inputs.tmenu.nixosModules.default ];

  programs.tmenu.enable = true;
}
```

**C. Direct installation in home.packages and environemnt.systemPackages**:

```nix
{
  home.packages = [ inputs.tmenu.packages.${pkgs.stdenv.hostPlatform.system}.default ];
}
```

**D. Using Overlay**:

Apply the overlay to add tmenu to your nixpkgs:

```nix
{
  nixpkgs.overlays = [ inputs.tmenu.overlays.default ];

  # Then use it like any other package
  environment.systemPackages = [ pkgs.tmenu ];
  # or in home-manager
  home.packages = [ pkgs.tmenu ];
}
```

### Option 2: Using pip

```bash
# Install from source
git clone https://github.com/AniviaFlome/tmenu
cd tmenu
pip install .

# Run tmenu
tmenu
```

**Dependencies** (automatically installed by pip):

- x256
- pyfiglet
- tomli (for Python < 3.11)

## Usage

### Basic Usage

Run tmenu with your configuration:

```bash
tmenu
```

tmenu will:

1. Load menu items from your config file (`$XDG_CONFIG_HOME/tmenu/config.toml`)
2. Display them in a centered menu with your custom title
3. Allow navigation into submenus
4. Execute the selected command

### Special Menu Items

- **← Back** - Appears at the bottom of submenus to return to parent menu
- **Exit** - Appears at the bottom of all menus to exit the application

### Configuration File

Specify a custom config file:

```bash
tmenu -c ~/.config/tmenu/custom.toml
```

### dmenu-like Usage (Piping Options)

tmenu can also work like `dmenu` by reading options from stdin via pipes. When used this way, tmenu displays the piped options as a menu and **prints** the selected option to stdout instead of executing it.

**Basic example:**

```bash
echo -e 'option 1\noption 2\noption 3' | tmenu
```

**With custom title:**

```bash
echo -e 'red\ngreen\nblue' | tmenu --placeholder "Select a color"
```

**Real-world examples:**

```bash
# Select a file
ls | tmenu --placeholder "Select file"

# Select from command output
git branch | tmenu --placeholder "Select branch"

# Chain with other commands
selected=$(find . -type f | tmenu --placeholder "Choose file")
echo "You selected: $selected"

# Select and open in editor
vim "$(find ~/notes -name '*.md' | tmenu --placeholder 'Select note')"
```

**Features when using stdin:**

- All keyboard shortcuts still work (vim keys, WASD, mouse, etc.)
- Themes and display settings are loaded from your config (if present)
- The `--placeholder` flag sets the menu title
- Selected item is printed to stdout (not executed)
- Exit code 0 on successful selection, 1 on cancel/escape

## Keyboard Shortcuts

**Note:** Navigation keys (arrow, vim, WASD) support **wraparound** - pressing down at the bottom wraps to top, and pressing up at the top wraps to bottom.

### Arrow Keys & Standard

| Key               | Action                                          |
| ----------------- | ----------------------------------------------- |
| `↑` / `Ctrl+P`    | Move selection up (wraps)                       |
| `↓` / `Ctrl+N`    | Move selection down (wraps)                     |
| `Home` / `Ctrl+A` | Jump to first item                              |
| `End` / `Ctrl+E`  | Jump to last item                               |
| `Page Up`         | Move up 10 items                                |
| `Page Down`       | Move down 10 items                              |
| `Enter`           | Select current item                             |
| `Escape` / `E`    | Go back (submenu) or exit (main menu)           |
| `Q`               | Go back (submenu) or exit (main menu)           |



### Vim Keys

| Key       | Action                      |
| --------- | --------------------------- |
| `j`       | Move selection down (wraps) |
| `k`       | Move selection up (wraps)   |
| `h` / `g` | Jump to first item          |
| `l` / `G` | Jump to last item           |

### WASD Keys

| Key | Action                      |
| --- | --------------------------- |
| `w` | Move selection up (wraps)   |
| `s` | Move selection down (wraps) |
| `a` | Jump to first item          |
| `d` | Jump to last item           |

### Number Shortcuts

| Key     | Action                     |
| ------- | -------------------------- |
| `1`-`9` | Execute item 1-9 instantly |

### Mouse

| Action         | Effect                         |
| -------------- | ------------------------------ |
| Single click   | Move selection to item         |
| Double-click   | Execute the item (200ms delay) |
| Scroll wheel ↑ | Move selection up (wraps)      |
| Scroll wheel ↓ | Move selection down (wraps)    |

## Configuration

Configuration is stored in TOML format. tmenu looks for configuration in:

1. `$XDG_CONFIG_HOME/tmenu/config.toml` (defaults to `~/.config/tmenu/config.toml`)

Or specify with `-c` flag.

### Configuration Sections

- **`[display]`** - Display settings
  - `centered` - Center the menu on screen (true/false)
  - `width` - Menu width in characters
  - `height` - Maximum number of visible items
  - `title` - Menu title to display at the top
  - `theme` - Theme name to load (optional, e.g., nord, dracula)
  - `figlet` - Enable ASCII art title with pyfiglet (true/false)
  - `figlet_font` - Font to use for figlet (e.g., standard, slant, banner)
  - `themes_dir` - Directory path for custom menu imports (optional)

- **`[colors]`** - Color settings (optional if using a theme)
  - `foreground` - Normal text color
  - `background` - Background color (-1 for transparent)
  - `selection_foreground` - Selected item text color
  - `selection_background` - Selected item background color
  - `prompt_foreground` - Prompt text color
  - Note: Only needed if you want to override theme colors or not use a theme

- **`[menu]`** - Main menu items
  - Format: `Label = "command"`
  - Use `submenu:NAME` to create a submenu entry
  - Commands are executed when selected
  - Supports commands with arguments (e.g., `Editor = "nvim ~/notes.md"`)

- **`[submenu.NAME]`** - Submenu definitions
  - Create sections named `[submenu.NAME]` for each submenu
  - Same format as main menu: `Label = "command"`
  - Can be nested by using `submenu:` in submenu items

## Themes

tmenu includes many built-in themes that you can use by setting `theme` in your config:

```toml
[display]
theme = "catppuccin-mocha"
```

### Custom Themes

Create your own themes in `$XDG_CONFIG_HOME/tmenu/themes/` (defaults to `~/.config/tmenu/themes/`):

```bash
mkdir -p "${XDG_CONFIG_HOME:-$HOME/.config}"/tmenu/themes
```

Create `$XDG_CONFIG_HOME/tmenu/themes/mytheme.toml`:

```toml
[colors]
foreground = "white"
background = -1
selection_foreground = "black"
selection_background = "cyan"
prompt_foreground = "blue"
```

Then use it:

```toml
[display]
theme = "mytheme"
```

**Note:** Themes only contain colors. Display settings (centered, width, height, title) stay in your main config.

Themes are located in:

1. `$XDG_CONFIG_HOME/tmenu/themes/` (user themes - highest priority)
2. Package installation directory (bundled themes when installed via pip/setuptools)
3. System data directories from `$XDG_DATA_DIRS` (bundled themes when installed via Nix)

### First Run

On first run, tmenu automatically creates `$XDG_CONFIG_HOME/tmenu/config.toml` (defaults to `~/.config/tmenu/config.toml`) with default settings if it doesn't exist.

### Custom Menu Imports

You can add additional menu items without editing your main `config.toml` by creating custom menu files.

**1. Enable custom themes in your config.toml:**

```toml
[display]
# Relative path (relative to $XDG_CONFIG_HOME/tmenu/)
themes_dir = "menus"

# Absolute paths also work
# themes_dir = "~/.local/share/tmenu/menus"
```

## Development

### Using Nix

```bash
# Enter development shell
nix-shell

# Run tmenu
python -m tmenu

# Run tests
pytest

# Format code
nix fmt

# Build package
nix build
```

### Using shell.nix

```bash
# Enter development shell
nix-shell

# Run tmenu
python tmenu.py

# Run tests
pytest
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
