# Themes Guide

tmenu supports themes for easy color customization. The default theme is **catppuccin-mocha**.

## Using Themes

Set a theme in your `config.ini`:

```ini
[display]
theme = nord
```

That's it! The theme will be loaded automatically.

## Available Themes

### Catppuccin Family

**Catppuccin Mocha** (Dark, Warm)
```ini
theme = catppuccin-mocha
```

**Catppuccin Frappé** (Dark, Cool)
```ini
theme = catppuccin-frappe
```

**Catppuccin Macchiato** (Dark, Neutral)
```ini
theme = catppuccin-macchiato
```

**Catppuccin Latte** (Light)
```ini
theme = catppuccin-latte
```

### Popular Themes

**Gruvbox Dark** - Retro, warm colors
```ini
theme = gruvbox-dark
```

**Dracula** - Vibrant purple theme
```ini
theme = dracula
```

**Nord** - Cool, minimal Scandinavian theme
```ini
theme = nord
```

**Tokyo Night** - Modern dark theme
```ini
theme = tokyo-night
```

**One Dark** - Atom/VSCode default
```ini
theme = onedark
```

**Monokai** - Classic Sublime Text theme
```ini
theme = monokai
```

**Rosé Pine** - Cozy, low-contrast theme
```ini
theme = rose-pine
```

**Solarized Dark** - Popular precision color scheme
```ini
theme = solarized-dark
```

**Solarized Light** - Light variant
```ini
theme = solarized-light
```

## Creating Custom Themes

### 1. Create Theme Directory

```bash
mkdir -p ~/.config/tmenu/themes
```

### 2. Create Theme File

Create `~/.config/tmenu/themes/mytheme.ini`:

```ini
[colors]
# Color configuration
foreground = white
background = -1
selection_foreground = black
selection_background = cyan
prompt_foreground = blue
```

**Note:** Themes only contain colors. Display settings (centered, width, height, title) are configured in your main `config.ini`.

### 3. Use Your Theme

In your `config.ini`:
```ini
[display]
theme = mytheme
```

## Theme Locations

tmenu searches for themes in this order:

1. **`~/.config/tmenu/themes/`** - User themes (highest priority)
2. **`./themes/`** - Bundled themes (in tmenu directory)

User themes override bundled themes with the same name.

## Color Values

Colors can be specified as:

- **Hex codes** (requires `pip install x256`):
  - `#cdd6f4` - Full hex color
  - `89b4fa` - Hex without # also works
  - Automatically converted to nearest xterm-256 color
  
- **Numbers**: 0-255 (xterm-256 colors)
  - 0-7 = basic colors (black, red, green, yellow, blue, magenta, cyan, white)
  - 8-15 = bright variants
  - 16-231 = 216 color cube
  - 232-255 = grayscale ramp

- **Special**: -1 (terminal default/transparent)

**Note:** Hex colors require the `x256` Python library. Install with `pip install x256`. Without it, themes will fall back to basic colors.

## Overriding Theme Colors

You can load a theme and override specific colors:

```ini
[display]
theme = nord

[colors]
# Override just the selection color
selection_background = magenta
```

Config colors override theme colors.

## Theme Examples

All themes contain only a `[colors]` section. Display settings are separate.

### Minimal Theme
```ini
[colors]
foreground = white
background = -1
selection_foreground = black
selection_background = cyan
prompt_foreground = blue
```

### Colorful Theme
```ini
[colors]
foreground = green
background = -1
selection_foreground = black
selection_background = yellow
prompt_foreground = magenta
```

### High Contrast Theme
```ini
[colors]
foreground = white
background = 0
selection_foreground = white
selection_background = red
prompt_foreground = yellow
```

### Why Themes Don't Have Display Settings

Themes are focused on **colors only**. This means:
- Display settings (width, height, centered) stay in your main config
- You can switch themes without changing your layout
- Multiple users can use the same theme with different layouts

## Tips

### Testing Themes

Quickly test themes by editing your config:

```bash
# Edit config
nano ~/.config/tmenu/config.ini

# Change theme line
theme = tokyo-night

# Run tmenu to see it
tmenu
```

### Terminal Compatibility

- Most themes work best with 256-color terminals
- Some terminals may render colors differently
- Use `-1` for transparent backgrounds

### Creating Theme Collections

Organize themes by purpose:

```
~/.config/tmenu/themes/
├── work-light.ini      # For daytime work
├── work-dark.ini       # For night work
├── presentation.ini    # High contrast for demos
└── minimal.ini         # Distraction-free
```

Switch between them easily:
```ini
theme = work-dark
```

## Sharing Themes

Share your themes with others:

1. Copy your theme file
2. Share the `.ini` file
3. Others place it in `~/.config/tmenu/themes/`

## Troubleshooting

### Theme Not Loading

Check:
1. Theme file exists in `~/.config/tmenu/themes/` or `./themes/`
2. Theme name in config matches filename (without `.ini`)
3. Theme file is valid INI format

### Colors Look Wrong

- Verify your terminal supports colors
- Check terminal color scheme settings
- Try a different theme
- Use `-1` for background if colors clash

### Theme Partially Works

Themes can specify just colors, just display settings, or both. Missing sections use defaults or config values.
