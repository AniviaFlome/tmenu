# Usage Guide

## Basic Usage

### Running tmenu

The simplest way to use tmenu is to just run it:

```bash
tmenu
```

By default, tmenu will:
1. Load menu items from your config file (`~/.config/tmenu/config.ini`)
2. Display them in a centered menu interface with title
3. Add "← Back" button at the bottom of submenus
4. Add "Exit" button at the bottom of all menus
5. Execute the selected command

You can then navigate using:
1. **Arrow keys** (↑/↓), **Vim keys** (j/k), or **WASD** (w/s) to move up/down
2. **Numbers 1-9** to execute items instantly (no need to press Enter)
3. **Mouse double-click** to execute items (200ms double-click window)
4. **Enter** to execute the selected command or navigate
5. Select "← Back" to return to parent menu
6. Select "Exit" to quit the application

### Configuring Your Menu

Create `~/.config/tmenu/config.ini`:

```ini
[display]
centered = true
width = 60
height = 10
title = Main Menu

[menu]
Terminal = alacritty
Browser = firefox
Development = submenu:Development
System = submenu:System

[submenu.Development]
Code Editor = code
Git GUI = gitg
Terminal = alacritty --working-directory ~/projects

[submenu.System]
File Manager = thunar
System Monitor = htop
Lock Screen = swaylock
```

Now when you run `tmenu`, you'll see your custom menu centered on the screen!

### Using Submenus

Organize your commands into logical groups:

1. **Create submenus** by adding `[submenu.NAME]` sections
2. **Link to submenus** using `Label = submenu:NAME` in your main menu
3. **Navigate** with Enter to open submenus
4. **Go back** by selecting the "← Back" option at the bottom
5. **Exit anytime** by selecting the "Exit" option at the bottom

Example navigation:
```
Main Menu
━━━━━━━━━━━━━━━━━━━━━━
  Terminal
  Browser
  Development    ← Press Enter
  Exit
```

Enters submenu:
```
Main Menu
━━━━━━━━━━━━━━━━━━━━━━
  Code Editor
  Git GUI
  Terminal
  ← Back         ← Select to go back
  Exit
```

## Advanced Usage

### Integration with Shell

Add to your `.bashrc` or `.zshrc`:

```bash
# Quick menu launcher with keybind
alias tm='tmenu'

# Bind to a key (example for bash)
bind -x '"\C-t": tmenu'
```

### Example Menu Configurations

#### Simple Launcher
```ini
[display]
title = Quick Launch
centered = true

[menu]
Terminal = alacritty
Browser = firefox
Files = thunar
Editor = nvim
```

#### Window Manager Menu
```ini
[display]
title = System Menu
centered = true

[menu]
Applications = submenu:Applications
System = submenu:System
Settings = submenu:Settings

[submenu.Applications]
Browser = firefox
Terminal = alacritty
Email = thunderbird
Chat = discord

[submenu.System]
Lock = swaylock
Logout = swaymsg exit
Reboot = systemctl reboot
Shutdown = systemctl poweroff

[submenu.Settings]
Display = arandr
Audio = pavucontrol
Network = nm-connection-editor
```

## Configuration

### Using Configuration Files

Create `~/.config/tmenu/config.ini`:

```ini
[colors]
foreground = white
background = -1
selection_foreground = black
selection_background = cyan
prompt_foreground = blue
```

Or specify a config file:

```bash
tmenu -c /path/to/config.ini
```

### Using Themes

Copy a theme to your config location:

```bash
mkdir -p ~/.config/tmenu
cp themes/catppuccin-mocha.ini ~/.config/tmenu/config.ini
```

Or with Home Manager:

```nix
programs.tmenu = {
  enable = true;
  theme = "catppuccin-mocha";
};
```

## Tips and Tricks

### Fuzzy Matching

tmenu uses fuzzy matching, which means you don't need to type the exact name. For example:
- Type "ff" to find "firefox"
- Type "gcm" to find "git-commit"
- Type "nvim" to find "nvim" or "neovim"

### Quick Navigation

- Press `Ctrl+A` or `Home` to jump to the first item
- Press `Ctrl+E` or `End` to jump to the last item
- Press `Page Up`/`Page Down` to move 10 items at a time

### Clearing Input

- Press `Ctrl+U` to clear the entire input line
- Press `Ctrl+W` to delete the last word
- Press `Backspace` to delete the last character

### Combining with Other Commands

tmenu works in pipelines:

```bash
# Select and execute
ls | tmenu -i - | xargs cat

# Multiple selections (requires external tools like fzf's multi-select)
# Note: tmenu currently supports single selection only
```
