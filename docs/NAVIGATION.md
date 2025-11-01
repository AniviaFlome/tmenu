# Navigation Guide

tmenu supports multiple navigation styles to accommodate different user preferences.

## Arrow Keys (Standard)

Traditional navigation for most users:

- `↑` or `Ctrl+P` - Move up
- `↓` or `Ctrl+N` - Move down
- `Home` or `Ctrl+A` - Jump to first item
- `End` or `Ctrl+E` - Jump to last item
- `Page Up` - Move up 10 items
- `Page Down` - Move down 10 items

## Vim Keys

For Vim users:

- `j` - Move down
- `k` - Move up
- `h` or `g` - Jump to first item (top)
- `l` or `G` - Jump to last item (bottom)

## WASD Keys

Gaming-style navigation:

- `w` - Move up
- `s` - Move down
- `a` - Jump to first item (left/home)
- `d` - Jump to last item (right/end)

## Number Shortcuts

Instant execution for first 9 items:

- `1` - **Execute** first item instantly
- `2` - **Execute** second item instantly
- `3` - **Execute** third item instantly
- ... and so on up to `9`

**Note:** 
- Number keys execute items directly - no need to press Enter!
- If your menu has fewer items than the number pressed, nothing happens
- Perfect for frequently-used menus where you know the position

## Mouse Support

Full mouse support with double-click execution:

1. **Single Click** - Move selection to the clicked item (highlights it)
2. **Double-Click** - Execute the item (200ms double-click window)

You can:
- Single-click to preview/select items
- Double-click to execute commands or enter submenus
- Double-click "← Back" to return to parent menu
- Double-click "Exit" to quit

**Double-click timing:**
- 200ms (0.2 seconds) window for double-click detection
- Quick and responsive for fast navigation
- Still prevents accidental activations

## Universal Keys

These work across all navigation styles:

- `Enter` - Activate selected item
- `Escape` - Go back (submenu) or exit (main menu)

## Tips

### Mixing Navigation Styles

You can freely mix different navigation methods:
- Use mouse to quickly jump to an area
- Use Vim keys for precise navigation
- Use numbers for instant access

### Efficient Navigation

**Instant execution:**
- Press `1` to **instantly execute** first item
- Press `2` to **instantly execute** second item
- Numbers bypass selection - direct execution!
- Perfect for muscle memory with consistent menus

**Quick jumps:**
- Use `g`/`h`/`a` for top
- Use `G`/`l`/`d` for bottom

**Smooth scrolling:**
- Use `j`/`k` or `w`/`s` for single-item movement
- Use arrow keys if that's more comfortable

**Mouse users:**
- Single-click to preview (move selection)
- Double-click within 200ms to execute
- Quick double-clicks for responsive navigation

### Accessibility

Different input methods ensure tmenu is accessible:
- **Keyboard-only users** - Full functionality via keys
- **Mouse-only users** - Complete control with clicks
- **Hybrid users** - Mix and match as needed
