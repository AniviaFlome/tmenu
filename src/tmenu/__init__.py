#!/usr/bin/env python3
"""
tmenu - A dmenu-like command executor for the terminal using ncurses
"""

import argparse
import curses
import os
import shlex
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# TOML parsing support
try:
    import tomllib  # Python 3.11+
except ImportError:
    try:
        import tomli as tomllib  # Fallback for older Python versions
    except ImportError:
        print("Error: TOML support requires Python 3.11+ or 'tomli' package", file=sys.stderr)
        print("Install with: pip install tomli", file=sys.stderr)
        sys.exit(1)

from x256 import x256

# Optional pyfiglet support for ASCII art titles
try:
    import pyfiglet

    PYFIGLET_AVAILABLE = True
except ImportError:
    PYFIGLET_AVAILABLE = False


def get_xdg_config_home() -> str:
    """Get XDG config directory, defaulting to ~/.config if not set."""
    return os.environ.get('XDG_CONFIG_HOME', os.path.expanduser('~/.config'))


def get_xdg_data_home() -> str:
    """Get XDG data directory, defaulting to ~/.local/share if not set."""
    return os.environ.get('XDG_DATA_HOME', os.path.expanduser('~/.local/share'))



class TMenu:
    """Terminal menu for selecting and executing commands."""

    def __init__(
        self,
        items: List[str],
        config: Optional[dict] = None,
        menu_items: Optional[Dict[str, str]] = None,
        submenus: Optional[Dict[str, Dict[str, str]]] = None,
        title: str = "",
        is_submenu: bool = False,
    ):
        """
        Initialize TMenu.

        Args:
            items: List of items to display
            config: Configuration dictionary with theme settings
            menu_items: Dictionary mapping display labels to commands
            submenus: Dictionary of submenu name to submenu items
            title: Menu title to display
            is_submenu: Whether this is a submenu (shows Back option)
        """
        self.all_items = list(items)

        # Add Back option for submenus and Exit for all menus
        if is_submenu:
            self.all_items.append("← Back")
        self.all_items.append("Exit")

        self.selected_index = 0
        self.scroll_offset = 0
        self.config = config or {}
        self.menu_items = menu_items or {}
        self.submenus = submenus or {}
        self.title = title
        self.centered = self.config.get("centered", True)
        self.is_submenu = is_submenu

        # For mouse support
        self.item_positions = []  # List of (y, start_x, end_x, item_index)
        self.last_click_time = 0
        self.last_click_item = None
        self.double_click_delay = 0.2  # 200ms for double-click detection

    def get_colors(self, stdscr) -> dict:
        """Initialize color pairs based on config."""
        colors = {}

        if curses.has_colors():
            curses.use_default_colors()

            # Parse colors from config or use defaults
            fg = self.config.get("foreground", 7)  # white
            bg = self.config.get("background", -1)  # terminal default
            sel_fg = self.config.get("selection_foreground", 0)  # black
            sel_bg = self.config.get("selection_background", 6)  # cyan
            prompt_fg = self.config.get("prompt_foreground", 4)  # blue

            # Initialize color pairs
            curses.init_pair(1, fg, bg)  # Normal text
            curses.init_pair(2, sel_fg, sel_bg)  # Selected item
            curses.init_pair(3, prompt_fg, bg)  # Prompt

            colors["normal"] = curses.color_pair(1)
            colors["selected"] = curses.color_pair(2)
            colors["prompt"] = curses.color_pair(3) | curses.A_BOLD
        else:
            colors["normal"] = curses.A_NORMAL
            colors["selected"] = curses.A_REVERSE
            colors["prompt"] = curses.A_BOLD

        return colors

    def render_figlet_title(self, title: str) -> List[str]:
        """Render title using pyfiglet if available and enabled."""
        if not PYFIGLET_AVAILABLE or not self.config.get("figlet", False):
            return [title]

        try:
            font = self.config.get("figlet_font", "standard")
            fig = pyfiglet.Figlet(font=font, width=self.config.get("width", 60))
            figlet_text = fig.renderText(title)
            # Split into lines and remove trailing empty lines
            lines = figlet_text.rstrip("\n").split("\n")
            return lines
        except Exception:
            # Fallback to plain title if figlet fails
            return [title]

    def draw(self, stdscr, colors: dict):
        """Draw the menu interface."""
        height, width = stdscr.getmaxyx()
        stdscr.clear()

        # Calculate menu dimensions and position
        menu_width = min(self.config.get("width", 60), width - 4)
        num_items = min(len(self.all_items), self.config.get("height", 10))

        # Calculate title height
        title_height = 0
        if self.title:
            title_lines = self.render_figlet_title(self.title)
            title_height = len(title_lines)

        # Menu height for items only (separator + items)
        items_height = num_items + 1  # +1 for separator

        # Always center vertically
        items_start_y = max(0, (height - items_height) // 2)
        start_y = max(0, items_start_y - title_height)

        if self.centered:
            # Center horizontally as well
            start_x = max(0, (width - menu_width) // 2)
        else:
            # Left-aligned, full width
            start_x = 0
            menu_width = width - 1

        current_y = start_y

        # Draw title if present (with optional figlet)
        if self.title:
            title_lines = self.render_figlet_title(self.title)
            for title_line in title_lines:
                if current_y >= height:
                    break
                # Center or left-align title line
                if self.centered:
                    title_x = start_x + max(0, (menu_width - len(title_line)) // 2)
                else:
                    title_x = start_x
                try:
                    display_line = (
                        title_line[:menu_width]
                        if len(title_line) > menu_width
                        else title_line
                    )
                    stdscr.addstr(
                        current_y,
                        title_x,
                        display_line,
                        colors["prompt"] | curses.A_BOLD,
                    )
                except curses.error:
                    pass
                current_y += 1

        # Draw separator
        sep_y = current_y
        if sep_y < height:
            separator = "─" * menu_width
            try:
                stdscr.addstr(sep_y, start_x, separator, colors["normal"])
            except curses.error:
                pass

        # Calculate visible lines
        visible_lines = min(len(self.all_items), height - sep_y - 1)
        if visible_lines <= 0:
            stdscr.refresh()
            return

        # Adjust scroll offset to keep selected item visible
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible_lines:
            self.scroll_offset = self.selected_index - visible_lines + 1

        # Clear item positions for mouse support
        self.item_positions = []

        # Calculate consistent indent for centered text alignment
        if self.centered:
            # Find the longest item in visible range for proper centering
            max_item_len = 0
            for i in range(visible_lines):
                item_index = i + self.scroll_offset
                if item_index >= len(self.all_items):
                    break
                item = self.all_items[item_index]
                truncated_len = min(len(item), menu_width - 2)
                max_item_len = max(max_item_len, truncated_len)
            # Calculate indent to center the text block
            text_indent = (menu_width - max_item_len) // 2
        else:
            text_indent = 0

        # Draw visible items
        for i in range(visible_lines):
            item_index = i + self.scroll_offset
            if item_index >= len(self.all_items):
                break

            item = self.all_items[item_index]
            y = sep_y + 1 + i

            # Truncate item if too long
            display_item = (
                item[: menu_width - 2] if len(item) > menu_width - 2 else item
            )

            # Apply consistent text indent for centered mode
            item_x = start_x + text_indent

            # Store position for mouse support
            if self.centered:
                self.item_positions.append(
                    (y, start_x, start_x + menu_width, item_index)
                )
            else:
                self.item_positions.append(
                    (y, item_x, item_x + len(display_item), item_index)
                )

            # Highlight selected item
            if item_index == self.selected_index:
                attr = colors["selected"]
                # Pad with spaces for full-width highlight
                display_item = " " * text_indent + display_item.ljust(
                    menu_width - text_indent
                )
                item_x = start_x
            else:
                attr = colors["normal"]

            try:
                stdscr.addstr(y, item_x, display_item[:menu_width], attr)
            except curses.error:
                pass

        # Draw scrollbar indicator if needed
        if len(self.all_items) > visible_lines:
            try:
                scroll_info = f" [{self.selected_index + 1}/{len(self.all_items)}]"
                stdscr.addstr(
                    sep_y,
                    start_x + menu_width - len(scroll_info),
                    scroll_info,
                    colors["normal"],
                )
            except curses.error:
                pass

        stdscr.refresh()

    def run(self, stdscr) -> Optional[str]:
        """
        Run the menu and return selected item.

        Args:
            stdscr: Curses window object

        Returns:
            Selected item or None if cancelled
        """
        curses.curs_set(0)  # Hide cursor
        stdscr.keypad(True)

        # Enable mouse support with explicit double-click
        mouse_mask = (
            curses.BUTTON1_CLICKED
            | curses.BUTTON1_DOUBLE_CLICKED
            | curses.BUTTON1_TRIPLE_CLICKED
        )
        curses.mousemask(mouse_mask)

        colors = self.get_colors(stdscr)

        while True:
            self.draw(stdscr, colors)

            try:
                key = stdscr.getch()
            except KeyboardInterrupt:
                return None

            # Handle input
            if key == ord("\n"):  # Enter
                if self.all_items and self.selected_index < len(self.all_items):
                    selected = self.all_items[self.selected_index]

                    # Handle special menu items
                    if selected == "← Back":
                        return "__GO_BACK__"
                    elif selected == "Exit":
                        return None

                    command = self.menu_items.get(selected, selected)

                    # Check if this is a submenu
                    if command.startswith("submenu:"):
                        submenu_name = command[8:]  # Remove 'submenu:' prefix
                        if submenu_name in self.submenus:
                            # Return signal to enter submenu with label
                            return f"__SUBMENU__{submenu_name}__{selected}"
                    else:
                        # Execute command
                        return command
                return None

            elif key == 27:  # Escape
                if self.is_submenu:
                    return "__GO_BACK__"
                return None

            elif key == ord("q"):  # Quit
                return None

            # Mouse support with double-click detection
            elif key == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, bstate = curses.getmouse()

                    # Check for native double-click first
                    is_native_double = bstate & curses.BUTTON1_DOUBLE_CLICKED

                    # Also handle single clicks for manual double-click detection
                    if bstate & curses.BUTTON1_CLICKED or is_native_double:
                        current_time = time.time()
                        # Check if click is on a menu item
                        for y, start_x, end_x, item_idx in self.item_positions:
                            if my == y and start_x <= mx < end_x:
                                # Check for double-click (native or manual)
                                is_manual_double = (
                                    self.last_click_item == item_idx
                                    and (current_time - self.last_click_time)
                                    < self.double_click_delay
                                )

                                if is_native_double or is_manual_double:
                                    # Double-click - execute item
                                    selected = self.all_items[item_idx]
                                    if selected == "← Back":
                                        return "__GO_BACK__"
                                    elif selected == "Exit":
                                        return None
                                    command = self.menu_items.get(selected, selected)
                                    if command.startswith("submenu:"):
                                        submenu_name = command[8:]
                                        if submenu_name in self.submenus:
                                            return (
                                                f"__SUBMENU__{submenu_name}__{selected}"
                                            )
                                    else:
                                        return command
                                else:
                                    # Single click - move selection and update click tracking
                                    self.selected_index = item_idx
                                    self.last_click_item = item_idx
                                    self.last_click_time = current_time
                                break
                except Exception as e:
                    pass

            # Vim keys: j/k for up/down
            elif key == ord("k"):  # Vim up
                if self.selected_index > 0:
                    self.selected_index -= 1

            elif key == ord("j"):  # Vim down
                if self.selected_index < len(self.all_items) - 1:
                    self.selected_index += 1

            # Vim keys: h/l or g/G for home/end
            elif key == ord("h") or key == ord("g"):  # Vim home/top
                self.selected_index = 0

            elif key == ord("l") or key == ord("G"):  # Vim end/bottom
                self.selected_index = max(0, len(self.all_items) - 1)

            # WASD keys: w/s for up/down
            elif key == ord("w"):  # WASD up
                if self.selected_index > 0:
                    self.selected_index -= 1

            elif key == ord("s"):  # WASD down
                if self.selected_index < len(self.all_items) - 1:
                    self.selected_index += 1

            # WASD keys: a/d for page up/down or home/end
            elif key == ord("a"):  # WASD left/home
                self.selected_index = 0

            elif key == ord("d"):  # WASD right/end
                self.selected_index = max(0, len(self.all_items) - 1)

            # Number keys 1-9 to execute items directly
            elif ord("1") <= key <= ord("9"):
                item_num = key - ord("1")  # 0-indexed
                if item_num < len(self.all_items):
                    # Execute the item directly
                    selected = self.all_items[item_num]
                    if selected == "← Back":
                        return "__GO_BACK__"
                    elif selected == "Exit":
                        return None
                    command = self.menu_items.get(selected, selected)
                    if command.startswith("submenu:"):
                        submenu_name = command[8:]
                        if submenu_name in self.submenus:
                            return f"__SUBMENU__{submenu_name}__{selected}"
                    else:
                        return command

            # Arrow keys and original shortcuts
            elif key == curses.KEY_UP or key == 16:  # Up or Ctrl+P
                if self.selected_index > 0:
                    self.selected_index -= 1

            elif key == curses.KEY_DOWN or key == 14:  # Down or Ctrl+N
                if self.selected_index < len(self.all_items) - 1:
                    self.selected_index += 1

            elif key == curses.KEY_PPAGE:  # Page Up
                self.selected_index = max(0, self.selected_index - 10)

            elif key == curses.KEY_NPAGE:  # Page Down
                self.selected_index = min(
                    len(self.all_items) - 1, self.selected_index + 10
                )

            elif key == curses.KEY_HOME or key == 1:  # Home or Ctrl+A
                self.selected_index = 0

            elif key == curses.KEY_END or key == 5:  # End or Ctrl+E
                self.selected_index = max(0, len(self.all_items) - 1)


def load_theme(theme_name: str) -> Optional[dict]:
    """Load a theme from various locations.

    Searches in order:
    1. $XDG_CONFIG_HOME/tmenu/themes/{theme_name}.toml (user config themes)
    2. $XDG_DATA_HOME/tmenu/themes/{theme_name}.toml (user data themes)
    3. System data directories from $XDG_DATA_DIRS (e.g., /usr/share, /nix/store/.../share)
    4. ./themes/{theme_name}.toml (development fallback - relative to script parent)

    Returns:
        Dictionary with theme config if theme found, None otherwise
    """
    theme_locations = [
        # User config directory
        os.path.join(get_xdg_config_home(), "tmenu", "themes", f"{theme_name}.toml"),
        # User data directory
        os.path.join(get_xdg_data_home(), "tmenu", "themes", f"{theme_name}.toml"),
    ]

    # Add system data directories from XDG_DATA_DIRS
    xdg_data_dirs = os.environ.get('XDG_DATA_DIRS', '/usr/local/share:/usr/share')
    for data_dir in xdg_data_dirs.split(':'):
        if data_dir:
            theme_locations.append(os.path.join(data_dir, "tmenu", "themes", f"{theme_name}.toml"))

    # Development fallback - relative to script location
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    theme_locations.append(os.path.join(parent_dir, "themes", f"{theme_name}.toml"))

    for theme_path in theme_locations:
        if os.path.exists(theme_path):
            try:
                with open(theme_path, "rb") as f:
                    return tomllib.load(f)
            except Exception:
                continue

    return None


def create_default_config():
    """Create default config file in $XDG_CONFIG_HOME/tmenu/ if it doesn't exist."""
    config_dir = os.path.join(get_xdg_config_home(), "tmenu")
    config_file = os.path.join(config_dir, "config.toml")

    # Don't create if it already exists
    if os.path.exists(config_file):
        return

    # Create directory if needed
    os.makedirs(config_dir, exist_ok=True)

    # Get path to default config file (in same directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_config_path = os.path.join(script_dir, "config.default.toml")

    try:
        # Read default config from file
        with open(default_config_path, "r") as f:
            default_config = f.read()

        # Write to user config
        with open(config_file, "w") as f:
            f.write(default_config)
    except Exception:
        pass  # Silently fail if we can't create config


def load_custom_menus(
    theme_dir: Optional[str] = None,
) -> Tuple[Dict[str, str], Dict[str, Dict[str, str]]]:
    """Load custom menu configurations from specified directory.

    Args:
        theme_dir: Path to theme directory. If None, no custom menus are loaded.

    Returns:
        Tuple of (menu_items dict, submenus dict)
    """
    menu_items = {}
    submenus = {}

    # Return empty if no directory specified
    if theme_dir is None:
        return menu_items, submenus

    # Expand user path
    theme_dir = os.path.expanduser(theme_dir)

    # Return empty if directory doesn't exist
    if not os.path.exists(theme_dir) or not os.path.isdir(theme_dir):
        return menu_items, submenus

    # Load all .toml files from theme directory
    try:
        for filename in sorted(os.listdir(theme_dir)):
            if filename.endswith(".toml"):
                menu_path = os.path.join(theme_dir, filename)
                try:
                    with open(menu_path, "rb") as f:
                        data = tomllib.load(f)

                    # Load menu items
                    if "menu" in data:
                        for label, command in data["menu"].items():
                            menu_items[label] = command

                    # Load submenus (keys starting with "submenu.")
                    for section_name, section_data in data.items():
                        if section_name.startswith("submenu."):
                            submenu_name = section_name[8:]  # Remove 'submenu.' prefix
                            if submenu_name not in submenus:
                                submenus[submenu_name] = {}
                            submenus[submenu_name].update(section_data)
                except Exception:
                    continue  # Skip invalid files
    except Exception:
        pass  # Silently fail if directory can't be read

    return menu_items, submenus


def load_config(
    config_path: Optional[str] = None,
) -> Tuple[dict, Dict[str, str], Dict[str, Dict[str, str]], str]:
    """Load configuration from file.

    Returns:
        Tuple of (config dict, menu_items dict, submenus dict, title string)
    """
    # Create default config if none exists
    if config_path is None:
        create_default_config()

    if config_path is None:
        # Try default locations
        config_locations = [
            os.path.join(get_xdg_config_home(), "tmenu", "config.toml"),
        ]
        for loc in config_locations:
            if os.path.exists(loc):
                config_path = loc
                break

    config = {}
    menu_items = {}
    submenus = {}
    title = ""

    data = None

    # Load config file
    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
        except Exception:
            pass  # Silently fail if config can't be loaded

    # First, check if config specifies a theme and load it
    theme_data = None
    if data and "display" in data and "theme" in data["display"]:
        theme_name = data["display"]["theme"]
        # Only load theme if name is not empty
        if theme_name and theme_name.strip():
            theme_data = load_theme(theme_name)

    # Load theme colors first (can be overridden by config)
    if theme_data and "colors" in theme_data:
        for key, value in theme_data["colors"].items():
            # Handle hex colors
            if isinstance(value, str):
                value = value.strip()
                # Check if it's a hex color
                if value.startswith("#") or (
                    len(value) == 6 and all(c in "0123456789abcdefABCDEF" for c in value)
                ):
                    # Use x256 library to convert hex to xterm-256
                    hex_color = value.lstrip("#").lower()
                    config[key] = x256.from_hex(hex_color)
                else:
                    # Try numeric value
                    try:
                        config[key] = int(value)
                    except ValueError:
                        config[key] = -1
            elif isinstance(value, int):
                config[key] = value

    # Now load config (overrides theme)
    if data:
        if "colors" in data:
            color_map = {
                "black": 0,
                "red": 1,
                "green": 2,
                "yellow": 3,
                "blue": 4,
                "magenta": 5,
                "cyan": 6,
                "white": 7,
            }

            for key, value in data["colors"].items():
                if isinstance(value, int):
                    config[key] = value
                elif isinstance(value, str):
                    try:
                        config[key] = int(value)
                    except ValueError:
                        config[key] = color_map.get(value.lower(), -1)

        if "display" in data:
            display = data["display"]
            if "centered" in display:
                config["centered"] = bool(display["centered"])
            if "width" in display:
                config["width"] = int(display["width"])
            if "height" in display:
                config["height"] = int(display["height"])
            if "title" in display:
                title = str(display["title"])
            if "figlet" in display:
                config["figlet"] = bool(display["figlet"])
            if "figlet_font" in display:
                config["figlet_font"] = str(display["figlet_font"])
            if "theme_dir" in display:
                config["theme_dir"] = str(display["theme_dir"])

        if "menu" in data:
            for label, command in data["menu"].items():
                menu_items[label] = command

        # Load submenus (sections like [submenu.Development])
        for section_name, section_data in data.items():
            if section_name.startswith("submenu."):
                submenu_name = section_name[8:]  # Remove 'submenu.' prefix
                submenus[submenu_name] = dict(section_data)

    # Load and merge custom menus if theme_dir is configured
    theme_dir = config.get("theme_dir")
    custom_menu_items, custom_submenus = load_custom_menus(theme_dir)
    menu_items.update(custom_menu_items)
    for submenu_name, submenu_items in custom_submenus.items():
        if submenu_name in submenus:
            submenus[submenu_name].update(submenu_items)
        else:
            submenus[submenu_name] = submenu_items

    return config, menu_items, submenus, title


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="tmenu - A configurable terminal menu")
    parser.add_argument("-c", "--config", help="Path to configuration file")

    args = parser.parse_args()

    # Load configuration
    config, menu_items, submenus, title = load_config(args.config)

    # Check if we have menu items
    if not menu_items:
        print("Error: No menu items found in configuration.", file=sys.stderr)
        print(
            f"Please create a config file at {get_xdg_config_home()}/tmenu/config.toml", file=sys.stderr
        )
        print("with a [menu] section defining your menu items.", file=sys.stderr)
        sys.exit(1)

    # Main menu loop with stack for submenu navigation
    menu_stack = []
    current_items = list(menu_items.keys())
    current_menu_items = menu_items
    current_title = title

    while True:
        # Determine if we're in a submenu
        is_submenu = len(menu_stack) > 0

        # Run menu
        menu = TMenu(
            current_items,
            config=config,
            menu_items=current_menu_items,
            submenus=submenus,
            title=current_title,
            is_submenu=is_submenu,
        )

        try:
            selection = curses.wrapper(menu.run)
        except KeyboardInterrupt:
            sys.exit(130)

        if selection == "__GO_BACK__":
            # Go back to previous menu
            if menu_stack:
                menu_stack.pop()
                if menu_stack:
                    # Return to submenu
                    submenu_name, submenu_label = menu_stack[-1]
                    current_items = list(submenus[submenu_name].keys())
                    current_menu_items = submenus[submenu_name]
                    current_title = submenu_label
                else:
                    # Return to main menu
                    current_items = list(menu_items.keys())
                    current_menu_items = menu_items
                    current_title = title
            continue
        elif selection and selection.startswith("__SUBMENU__"):
            # Enter submenu
            parts = selection.split("__")
            submenu_name = parts[2]
            submenu_label = parts[3] if len(parts) > 3 else submenu_name
            menu_stack.append((submenu_name, submenu_label))
            current_items = list(submenus[submenu_name].keys())
            current_menu_items = submenus[submenu_name]
            current_title = submenu_label
            continue
        elif selection:
            # Execute the command
            try:
                cmd_parts = shlex.split(selection)
                os.execvp(cmd_parts[0], cmd_parts)
            except FileNotFoundError:
                print(f"tmenu: command not found: {selection}", file=sys.stderr)
                sys.exit(127)
            except PermissionError:
                print(f"tmenu: permission denied: {selection}", file=sys.stderr)
                sys.exit(126)
            except Exception as e:
                print(f"tmenu: error executing command: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            # Exit selected or escaped from main menu
            sys.exit(0)


if __name__ == "__main__":
    main()
