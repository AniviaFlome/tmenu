# Figlet ASCII Art Titles

tmenu supports optional ASCII art titles using [pyfiglet](https://github.com/pwaller/pyfiglet).

## Installation

Install pyfiglet to enable ASCII art titles:

```bash
pip install pyfiglet
```

Or with Nix:
```bash
nix-shell -p python3Packages.pyfiglet
```

## Configuration

Enable figlet in your `config.ini`:

```ini
[display]
title = TMENU
figlet = true
figlet_font = slant
```

## Available Fonts

Popular figlet fonts:

- **standard** - Classic figlet font
- **slant** - Slanted text (recommended)
- **banner** - Large banner style
- **big** - Big letters
- **block** - Block letters
- **bubble** - Bubble letters
- **digital** - Digital display style
- **isometric1** - 3D isometric
- **letters** - Simple letters
- **mini** - Compact style
- **small** - Small letters
- **smslant** - Small slant

### View All Fonts

List all available fonts:
```bash
pyfiglet -l
```

Test a font:
```bash
pyfiglet -f slant "TMENU"
```

## Examples

### Slant Font (Recommended)
```ini
[display]
title = TMENU
figlet = true
figlet_font = slant
width = 80
```

Output:
```
     __________  ___________   ____  __
    /_  __/ __ \/  _/ ____/ | / / / / /
     / / / /_/ // // __/ /  |/ / / / / 
    / / / _, _// // /___/ /|  / /_/ /  
   /_/ /_/ |_/___/_____/_/ |_/\____/   
```

### Banner Font
```ini
[display]
title = MENU
figlet = true
figlet_font = banner
width = 80
```

### Big Font
```ini
[display]
title = Menu
figlet = true
figlet_font = big
width = 80
```

## Tips

### Width Adjustment

ASCII art titles can be wide. Increase your menu width:

```ini
[display]
width = 80  # or even 100 for larger fonts
figlet = true
```

### Short Titles

Keep titles short (1-6 characters) for best results:
- ✅ "MENU", "TMENU", "APPS"
- ⚠️ "My Application Launcher" (too long)

### Font Selection

- **Narrow terminals** → Use `mini`, `small`, or `smslant`
- **Wide terminals** → Use `banner`, `big`, or `isometric1`
- **Standard size** → Use `standard` or `slant`

### Disable for Submenus

You might want figlet only on the main menu:

```ini
[display]
title = MAIN
figlet = true

# Title will show as plain text in submenus
```

## Troubleshooting

### "Module not found" Error

Install pyfiglet:
```bash
pip install pyfiglet
```

### Title Too Wide

1. Use a shorter title
2. Increase `width` setting
3. Choose a narrower font (e.g., `smslant`, `mini`)

### Title Not Showing

Check:
1. Is `figlet = true` in config?
2. Is `title` set in `[display]` section?
3. Is pyfiglet installed? Test: `python -c "import pyfiglet"`

### Graceful Fallback

If pyfiglet is not installed, tmenu automatically falls back to regular text titles. No errors!

## ASCII Art Examples

Try these titles with different fonts:

```bash
# Slant
pyfiglet -f slant "TMENU"

# Banner  
pyfiglet -f banner "MENU"

# Digital
pyfiglet -f digital "APPS"

# Isometric
pyfiglet -f isometric1 "SYS"
```
