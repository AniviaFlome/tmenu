# tmenu

Vibe coded for personal use. Use it if you want.

## Installation

### Using Nix Flakes

```
tmenu.url = "github:AniviaFlome/tmenu";
```

### Using Home Manager

Add to your `home.nix`:

```nix
{
  imports = [ inputs.tmenu.homeManagerModules.default ];

  programs.tmenu = {
    enable = true;

    display = {
      centered = true;
      width = 60;
      height = 10;
      title = "Tmenu";
      figlet = {
        enable = true;
        font = "standard";
      };
      theme = {
        name = "catppuccin-mocha";
      };
    };

    menuItems = {
      "Terminal" = "alacritty";
      "Browser" = "firefox";
      "System" = "submenu:System";
    };

    submenu.System = {
      "File Manager" = "thunar";
      "System Monitor" = "htop";
      "Task Manager" = "gnome-system-monitor";
    };
  };
}
```

### Using NixOS

Add to your `configuration.nix`:

```nix
{
  imports = [ inputs.tmenu.nixosModules.default ];

  programs.tmenu.enable = true;
}
```

### Manual Installation

```bash
# Clone the repository
git clone https://github.com/AniviaFlome/tmenu
cd tmenu

# Run tmenu
python src/tmenu.py

# Or make it executable
chmod +x src/tmenu.py
./src/tmenu.py

# Or copy to your PATH
cp src/tmenu.py ~/.local/bin/tmenu
```

### Dependencies

x256
pyfiglet (optional)

## Usage

### Basic Usage

Run tmenu with your configuration:

```bash
tmenu
```

tmenu will:

1. Load menu items from your config file (`~/.config/tmenu/config.toml`)
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

## Keyboard Shortcuts

### Arrow Keys & Standard

| Key               | Action              |
| ----------------- | ------------------- |
| `↑` / `Ctrl+P`    | Move selection up   |
| `↓` / `Ctrl+N`    | Move selection down |
| `Home` / `Ctrl+A` | Jump to first item  |
| `End` / `Ctrl+E`  | Jump to last item   |
| `Page Up`         | Move up 10 items    |
| `Page Down`       | Move down 10 items  |
| `Enter`           | Select current item |
| `Escape`          | Go back or exit     |
| `Q`               | Exit                |

### Vim Keys

| Key       | Action              |
| --------- | ------------------- |
| `j`       | Move selection down |
| `k`       | Move selection up   |
| `h` / `g` | Jump to first item  |
| `l` / `G` | Jump to last item   |

### WASD Keys

| Key | Action              |
| --- | ------------------- |
| `w` | Move selection up   |
| `s` | Move selection down |
| `a` | Jump to first item  |
| `d` | Jump to last item   |

### Number Shortcuts

| Key     | Action                     |
| ------- | -------------------------- |
| `1`-`9` | Execute item 1-9 instantly |

### Mouse

| Action       | Effect                         |
| ------------ | ------------------------------ |
| Single click | Move selection to item         |
| Double-click | Execute the item (200ms delay) |

## Configuration

Configuration is stored in TOML format. tmenu looks for configuration in:

1. `~/.config/tmenu/config.toml`

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
theme = "nord"
```

### Custom Themes

Create your own themes in `~/.config/tmenu/themes/`:

```bash
mkdir -p ~/.config/tmenu/themes
```

Create `~/.config/tmenu/themes/mytheme.toml`:

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

1. `~/.config/tmenu/themes/` (user themes - highest priority)
2. `./themes/` (bundled themes)

### First Run

On first run, tmenu automatically creates `~/.config/tmenu/config.toml` with default settings if it doesn't exist.

### Custom Menu Imports

You can add additional menu items without editing your main `config.toml` by creating custom menu files.

**1. Enable custom themes in your config.toml:**

```toml
[display]
# Relative path (relative to ~/.config/tmenu/)
themes_dir = "menus"

# Current directory
# themes_dir = "./menus"

# Absolute paths also work
# themes_dir = "~/.local/share/tmenu/menus"
```

## Development

### Using Nix

```bash
# Enter development shell
nix-shell

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
