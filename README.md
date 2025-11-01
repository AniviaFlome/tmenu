# tmenu

A configurable terminal menu system, built with Python and ncurses.

## Features

- 🚀 **Fast and lightweight** - Built with Python and ncurses
- 🎯 **Centered display** - Beautiful centered menu interface
- 📋 **Configurable menu items** - Define your own menu with custom commands
- 🗂️ **Submenu support** - Organize commands in hierarchical submenus
- 📝 **Custom titles** - Set a title for your menu
- 🎨 **ASCII art titles** - Optional pyfiglet support for stylish headers
- 🌈 **Themeable** - Customize colors with configuration files
- ⌨️ **Multiple navigation styles** - Arrow keys, Vim (hjkl), WASD, numbers, and mouse
- 🖱️ **Mouse support** - Click to navigate and select items
- 🔙 **Built-in navigation** - Back and Exit buttons in every menu
- 📦 **Nix integration** - Easy installation with Nix flakes and Home Manager

## Installation

### Using Nix Flakes

```bash
nix run github:yourusername/tmenu
```

### Using Home Manager

Add to your `home.nix`:

```nix
{
  programs.tmenu = {
    enable = true;
    theme = "catppuccin-mocha";  # Optional theme
    
    # Custom menu items
    menuItems = {
      "Terminal" = "alacritty";
      "Browser" = "firefox";
      "Development" = "submenu:Development";  # Opens submenu
      "System" = "submenu:System";
    };
    
    # Display settings (optional)
    display = {
      centered = true;  # Center the menu (default)
      width = 60;       # Menu width
      height = 10;      # Max visible items
    };
    
    # Additional settings
    settings = {
      display = {
        title = "Main Menu";
      };
      "submenu.Development" = {
        "Code Editor" = "code";
        "Git GUI" = "gitg";
        "Terminal" = "alacritty --working-directory ~/projects";
      };
      "submenu.System" = {
        "File Manager" = "thunar";
        "System Monitor" = "htop";
        "Task Manager" = "gnome-system-monitor";
      };
    };
  };
}
```

Or with custom colors:

```nix
{
  programs.tmenu = {
    enable = true;
    
    menuItems = {
      "Code" = "code";
      "Terminal" = "kitty";
    };
    
    colors = {
      foreground = "white";
      background = -1;
      selectionForeground = "black";
      selectionBackground = "cyan";
      promptForeground = "blue";
    };
  };
}
```

### Using NixOS

Add to your `configuration.nix`:

```nix
{
  programs.tmenu.enable = true;
}
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/tmenu
cd tmenu

# Run tmenu
python src/tmenu.py

# Or make it executable
chmod +x src/tmenu.py
./src/tmenu.py

# Or copy to your PATH
cp src/tmenu.py ~/.local/bin/tmenu
```

### Optional Dependencies

For enhanced features, install these optional Python packages:

**Hex color support in themes:**
```bash
pip install x256
```
Enables hex color codes (e.g., `#89b4fa`) in theme files. Without this, themes will use basic terminal colors.

**ASCII art titles:**
```bash
pip install pyfiglet
```
Enables ASCII art headers with configurable fonts.

## Usage

### Basic Usage

Run tmenu with your configuration:

```bash
tmenu
```

tmenu will:
1. Load menu items from your config file (`~/.config/tmenu/config.ini`)
2. Display them in a centered menu with your custom title
3. Allow navigation into submenus
4. Execute the selected command

### Navigation

**Multiple navigation styles supported:**

- **Arrow Keys** / **Ctrl+N/P** - Navigate up/down
- **Vim keys** (`j`/`k`) - Navigate down/up
- **Vim keys** (`h`/`g` or `l`/`G`) - Jump to first/last item
- **WASD keys** (`w`/`s`) - Navigate up/down
- **WASD keys** (`a`/`d`) - Jump to first/last item
- **Numbers** (`1`-`9`) - Execute item 1-9 instantly
- **Mouse** - Double-click to execute (200ms delay)
- **Enter** - Select item, enter submenu, go back, or exit
- **Escape** - Go back to parent menu or exit
- **Page Up/Down** - Jump 10 items
- **Home/End** - Jump to first/last item

### Special Menu Items

- **← Back** - Appears at the bottom of submenus to return to parent menu
- **Exit** - Appears at the bottom of all menus to exit the application

### Configuration File

Specify a custom config file:

```bash
tmenu -c ~/.config/tmenu/custom.ini
```

## Keyboard Shortcuts

### Arrow Keys & Standard
| Key | Action |
|-----|--------|
| `↑` / `Ctrl+P` | Move selection up |
| `↓` / `Ctrl+N` | Move selection down |
| `Home` / `Ctrl+A` | Jump to first item |
| `End` / `Ctrl+E` | Jump to last item |
| `Page Up` | Move up 10 items |
| `Page Down` | Move down 10 items |
| `Enter` | Select current item |
| `Escape` | Go back or exit |

### Vim Keys
| Key | Action |
|-----|--------|
| `j` | Move selection down |
| `k` | Move selection up |
| `h` / `g` | Jump to first item |
| `l` / `G` | Jump to last item |

### WASD Keys
| Key | Action |
|-----|--------|
| `w` | Move selection up |
| `s` | Move selection down |
| `a` | Jump to first item |
| `d` | Jump to last item |

### Number Shortcuts
| Key | Action |
|-----|--------|
| `1`-`9` | Execute item 1-9 instantly |

### Mouse
| Action | Effect |
|--------|--------|
| Single click | Move selection to item |
| Double-click | Execute the item (200ms delay) |

## Configuration

Configuration is stored in INI format. tmenu looks for configuration in:

1. `~/.config/tmenu/config.ini`
2. `~/.tmenu.ini`
3. `./config.ini`

Or specify with `-c` flag.

### Example Configuration

```ini
[display]
# Display settings
centered = true
width = 60
height = 10
title = Main Menu

# Theme (default: catppuccin-mocha)
theme = catppuccin-mocha

# Optional: ASCII art title (requires pyfiglet)
figlet = false
figlet_font = standard

[menu]
# Main menu items
Terminal = alacritty
Browser = firefox
Development = submenu:Development
System = submenu:System
Text Editor = nvim

[submenu.Development]
# Development tools submenu
Code Editor = code
Git GUI = gitg
Terminal = alacritty --working-directory ~/projects
Database = dbeaver

[submenu.System]
# System management submenu
File Manager = thunar
System Monitor = htop
Task Manager = gnome-system-monitor
Calculator = qalc
```

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
  - Format: `Label = command`
  - Use `submenu:NAME` to create a submenu entry
  - Commands are executed when selected
  - Supports commands with arguments (e.g., `Editor = nvim ~/notes.md`)

- **`[submenu.NAME]`** - Submenu definitions
  - Create sections named `[submenu.NAME]` for each submenu
  - Same format as main menu: `Label = command`
  - Can be nested by using `submenu:` in submenu items

## Themes

tmenu includes many built-in themes that you can use by setting `theme` in your config:

```ini
[display]
theme = nord
```

### Available Themes

**Catppuccin**
- `catppuccin-mocha` - Mocha (dark, warm)
- `catppuccin-frappe` - Frappé (dark, cool)
- `catppuccin-macchiato` - Macchiato (dark, neutral)
- `catppuccin-latte` - Latte (light)

**Popular Dark Themes**
- `gruvbox-dark` - Gruvbox Dark (retro, warm)
- `dracula` - Dracula (vibrant purple)
- `nord` - Nord (cool, minimal)
- `tokyo-night` - Tokyo Night (modern)
- `onedark` - One Dark (Atom/VSCode)
- `monokai` - Monokai (classic)
- `rose-pine` - Rosé Pine (cozy)

**Light Themes**
- `solarized-light` - Solarized Light
- `catppuccin-latte` - Catppuccin Latte

### Custom Themes

Create your own themes in `~/.config/tmenu/themes/`:

```bash
mkdir -p ~/.config/tmenu/themes
```

Create `~/.config/tmenu/themes/mytheme.ini`:
```ini
[colors]
foreground = white
background = -1
selection_foreground = black
selection_background = cyan
prompt_foreground = blue
```

Then use it:
```ini
[display]
theme = mytheme
```

**Note:** Themes only contain colors. Display settings (centered, width, height, title) stay in your main config.

Themes are located in:
1. `~/.config/tmenu/themes/` (user themes - highest priority)
2. `./themes/` (bundled themes)

### First Run

On first run, tmenu automatically creates `~/.config/tmenu/config.ini` with default settings if it doesn't exist. The default theme is **catppuccin-mocha**.

### Custom Menu Imports

You can add additional menu items without editing your main `config.ini` by creating custom menu files.

**1. Enable custom menus in your config.ini:**

```ini
[display]
# Relative path (relative to ~/.config/tmenu/)
themes_dir = menus

# Current directory
# themes_dir = ./menus

# Parent directory
# themes_dir = ../shared-menus

# Absolute paths also work
# themes_dir = ~/.local/share/tmenu/menus
# themes_dir = /etc/tmenu/menus
```

**2. Create the directory and menu files:**

```bash
# If using relative path
mkdir -p ~/.config/tmenu/menus

# Or if using absolute path
# mkdir -p ~/path/to/your/menus
```

**3. Create custom menu files** (e.g., `~/.config/tmenu/menus/games.ini`):

```ini
[menu]
# Add to main menu
Games = submenu:Games

[submenu.Games]
# Custom submenu
Steam = steam
Lutris = lutris
```

All `.ini` files in the configured `menus_dir` are automatically loaded and merged with your main config. This is useful for:
- Organizing menus into separate files
- Sharing menu configurations between systems
- Adding temporary menu items without modifying main config

## Development

### Using Nix

```bash
# Enter development shell
nix develop

# Run tmenu
python src/tmenu.py

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

# Format code
black tmenu.py
```

### Available Development Commands

- `black tmenu.py` - Format code
- `flake8 tmenu.py` - Lint code
- `mypy tmenu.py` - Type check code
- `pytest` - Run tests
- `pytest --cov` - Run tests with coverage

## Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=tmenu

# Run specific test
pytest test_tmenu.py::test_filter_items
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

MIT License - See LICENSE file for details

## Similar Projects

- [dmenu](https://tools.suckless.org/dmenu/) - The original dmenu for X11
- [fzf](https://github.com/junegunn/fzf) - Command-line fuzzy finder
- [rofi](https://github.com/davatorium/rofi) - Window switcher and application launcher
- [bemenu](https://github.com/Cloudef/bemenu) - Dynamic menu library and client

## Acknowledgments

Inspired by dmenu and designed for terminal workflows.
