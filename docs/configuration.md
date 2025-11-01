# Configuration Guide

## Configuration File Format

tmenu uses INI format for configuration files. The configuration file contains sections with key-value pairs.

### Available Sections

- **`[display]`** - Display and layout settings
- **`[colors]`** - Color scheme configuration
- **`[menu]`** - Menu items and commands

## Custom Menu Imports

You can extend your menu configuration by adding custom menu files in a directory of your choice.

### Enabling Custom Menu Imports

1. Configure the menus directory in your `config.ini`:

```ini
[display]
# Using relative path (recommended)
themes_dir = menus

# Or using absolute path
# themes_dir = ~/.config/tmenu/menus
# themes_dir = /path/to/custom/menus
```

2. Create the menus directory:

```bash
# If using relative path 'menus'
mkdir -p ~/.config/tmenu/menus

# Or create your custom directory
# mkdir -p /path/to/custom/menus
```

3. Create `.ini` files with menu definitions:

**Example: `~/.config/tmenu/menus/development.ini`**

```ini
[menu]
# Add items to main menu
Dev Tools = submenu:DevTools

[submenu.DevTools]
# Custom submenu
Docker = docker desktop
Postman = postman
DBeaver = dbeaver
```

**Example: `~/.config/tmenu/menus/media.ini`**

```ini
[menu]
Media = submenu:Media

[submenu.Media]
Spotify = spotify
VLC = vlc
OBS = obs
```

### How It Works

- Set `themes_dir` in `[display]` section to enable custom menu imports
- All `.ini` files in the configured directory are loaded automatically
- Files are loaded in alphabetical order
- Menu items are merged with your main `config.ini`
- Custom menus can add new items or override existing ones
- Submenus with the same name are merged
- If `themes_dir` is not set, no custom menus are loaded

### Benefits

- **Modular**: Organize menus by category or purpose
- **Shareable**: Copy menu files between systems
- **Clean**: Keep main config simple, add complexity separately
- **Temporary**: Add/remove menu files without editing main config

## File Locations

tmenu searches for configuration files in the following order:

1. Path specified with `-c` flag
2. `~/.config/tmenu/config.ini`
3. `~/.tmenu.ini`
4. `./config.ini` (current directory)

The first file found is used.

## Display Configuration

Control the appearance and layout of the menu.

### Display Options

```ini
[display]
# Whether to center the menu on screen
centered = true

# Width of the menu in characters
width = 60

# Maximum number of items to show at once
height = 10
```

### Options Explained

- **`centered`** (boolean) - When `true`, centers the menu in the terminal window. When `false`, aligns to top-left corner.
- **`width`** (integer) - Width of the menu box in characters. Capped at terminal width minus 4.
- **`height`** (integer) - Maximum number of menu items to display at once. Use scroll to see more items.
- **`title`** (string) - Title text displayed at the top of the menu.

## Menu Items Configuration

Define custom menu items with labels and commands.

### Menu Format

```ini
[menu]
# Format: Label = command
Terminal = alacritty
Browser = firefox --new-window
Editor = nvim ~/notes.md
File Manager = thunar
Calculator = qalc
```

### Features

- **Labels** - Displayed in the menu for selection
- **Commands** - Executed when the item is selected
- **Arguments** - Commands can include arguments and flags
- **Shell expansion** - Supports `~` for home directory

### Submenus

Create hierarchical menus using submenus. Use `submenu:NAME` as the command to open a submenu.

```ini
[menu]
Applications = submenu:Applications
System = submenu:System
Terminal = alacritty

[submenu.Applications]
Browser = firefox
Editor = nvim
Email = thunderbird

[submenu.System]
Lock = swaylock
Logout = swaymsg exit
Shutdown = systemctl poweroff
```

#### Navigation

- Select a submenu item with **Enter** to open it
- Select **← Back** at the bottom of submenus to return to parent menu
- Select **Exit** at the bottom of any menu to exit the application
- Press **Escape** in a submenu to go back, or in main menu to exit

**Note:** "← Back" and "Exit" options are automatically added to your menus - you don't need to configure them.

### Example Menu Configurations

#### Complete Menu with Submenus

```ini
[display]
title = Main Menu
centered = true
width = 60
height = 10

[menu]
Terminal = alacritty
Browser = firefox
Development = submenu:Development
System = submenu:System
Settings = submenu:Settings

[submenu.Development]
Code Editor = code
Git GUI = gitg
Terminal = alacritty --working-directory ~/projects
Database = dbeaver
API Client = insomnia

[submenu.System]
File Manager = thunar
System Monitor = htop
Task Manager = gnome-system-monitor
Lock Screen = swaylock
Logout = swaymsg exit
Shutdown = systemctl poweroff

[submenu.Settings]
Display = arandr
Audio = pavucontrol
Network = nm-connection-editor
Bluetooth = blueman-manager
```

#### Nested Submenus

```ini
[menu]
Main Item = command
More Options = submenu:More

[submenu.More]
Sub Item = command
Even More = submenu:EvenMore

[submenu.EvenMore]
Deep Item = command
```

## Color Configuration

### Basic Colors

Available color names:

- `black` (0)
- `red` (1)
- `green` (2)
- `yellow` (3)
- `blue` (4)
- `magenta` (5)
- `cyan` (6)
- `white` (7)

You can also use:

- Numbers 0-7 for the colors above
- `-1` for terminal default (transparent background)

### Color Options

```ini
[colors]
# Normal text color
foreground = white

# Background color (-1 = terminal default)
background = -1

# Selected item foreground
selection_foreground = black

# Selected item background
selection_background = cyan

# Prompt color
prompt_foreground = blue
```

## Examples

### Minimal Configuration

```ini
[colors]
foreground = white
background = -1
```

### High Contrast

```ini
[colors]
foreground = white
background = black
selection_foreground = white
selection_background = blue
prompt_foreground = yellow
```

### Solarized Dark

```ini
[colors]
foreground = 6  # cyan
background = -1
selection_foreground = 0  # black
selection_background = 3  # yellow
prompt_foreground = 4  # blue
```

### Gruvbox

```ini
[colors]
foreground = 7  # white/grey
background = -1
selection_foreground = 0  # black
selection_background = 3  # yellow/orange
prompt_foreground = 2  # green
```

## Nix Configuration

### Home Manager

Using Home Manager provides a declarative way to configure tmenu:

```nix
programs.tmenu = {
  enable = true;

  # Use a predefined theme
  theme = "catppuccin-mocha";

  # Or configure colors manually
  colors = {
    foreground = "white";
    background = -1;
    selectionForeground = "black";
    selectionBackground = "cyan";
    promptForeground = "blue";
  };

  # Or use raw settings
  settings = {
    colors = {
      foreground = 7;
      background = -1;
      selection_foreground = 0;
      selection_background = 6;
      prompt_foreground = 4;
    };
  };
};
```

### Available Themes

Built-in themes:

- `catppuccin-mocha`
- `gruvbox-dark`
- `dracula`

## Terminal Compatibility

### True Color Support

tmenu uses standard terminal colors (0-7) which work on all terminals. For more colors, your terminal must support 256-color or true color mode.

Check your terminal:

```bash
echo $TERM
```

Common values:

- `xterm-256color` - 256 color support
- `screen-256color` - tmux/screen with 256 colors
- `tmux-256color` - tmux with 256 colors

### Testing Colors

Test your configuration:

```bash
echo -e "test\nitem" | tmenu -i - -c ~/.config/tmenu/config.ini
```

## Troubleshooting

### Colors Not Showing

1. Check terminal color support: `echo $TERM`
2. Try using color numbers instead of names
3. Ensure terminal supports colors: `tput colors`

### Config Not Loading

1. Check file exists: `ls -la ~/.config/tmenu/config.ini`
2. Check file permissions: `chmod 644 ~/.config/tmenu/config.ini`
3. Verify INI syntax: no spaces around `=`

### Wrong Colors

1. Some terminals interpret colors differently
2. Try using explicit numbers (0-7) instead of names
3. Check terminal color scheme
