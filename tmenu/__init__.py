#!/usr/bin/env python3
"""
tmenu - dmenu for terminal
"""

import argparse
import curses
import os
import shlex
import sys
from typing import Dict, List, Optional, Tuple

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore

from x256 import x256  # type: ignore

try:
    import pyfiglet  # type: ignore
except ImportError:
    pyfiglet = None  # type: ignore

__all__ = ["TMenu", "main", "load_config", "load_theme"]


def get_xdg_config_home() -> str:
    """Get XDG config directory, defaulting to ~/.config if not set."""
    return os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))


DEFAULTS: dict = {
    "foreground": 7,  # white
    "background": -1,  # terminal default
    "selection_foreground": 0,  # black
    "selection_background": 6,  # cyan
    "prompt_foreground": 4,  # blue
    "centered": True,
    "width": 60,
    "height": 10,
    "figlet": False,
    "figlet_font": "standard",
}


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

        if is_submenu:
            self.all_items.append("← Back")
        self.all_items.append("Exit")

        self.selected_index = 0
        self.scroll_offset = 0
        self.config = {**DEFAULTS, **(config or {})}
        self.menu_items = menu_items or {}
        self.submenus = submenus or {}
        self.title = title
        self.centered = self.config["centered"]
        self.is_submenu = is_submenu

        self.item_positions: List[Tuple[int, int, int, int]] = []

    def _move_up(self):
        """Move selection up with wraparound."""
        if self.selected_index > 0:
            self.selected_index -= 1
        else:
            self.selected_index = len(self.all_items) - 1

    def _move_down(self):
        """Move selection down with wraparound."""
        if self.selected_index < len(self.all_items) - 1:
            self.selected_index += 1
        else:
            self.selected_index = 0

    def _handle_selection(self, item_index: int) -> Optional[str]:
        """Handle selection of an item. Returns command or special string."""
        if item_index >= len(self.all_items):
            return None
        selected = self.all_items[item_index]
        if selected == "← Back":
            return "__GO_BACK__"
        elif selected == "Exit":
            return None
        command = self.menu_items.get(selected, selected)
        if command and command.startswith("submenu:"):
            submenu_name = command[8:]
            if submenu_name in self.submenus:
                return f"__SUBMENU__{submenu_name}__{selected}"
        return command

    def get_colors(self, stdscr) -> dict:
        """Initialize color pairs based on config."""
        colors = {}

        if curses.has_colors():
            curses.use_default_colors()

            fg = self.config["foreground"]
            bg = self.config["background"]
            sel_fg = self.config["selection_foreground"]
            sel_bg = self.config["selection_background"]
            prompt_fg = self.config["prompt_foreground"]

            curses.init_pair(1, fg, bg)
            curses.init_pair(2, sel_fg, sel_bg)
            curses.init_pair(3, prompt_fg, bg)

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
        if pyfiglet is None or not self.config["figlet"]:
            return [title]

        try:
            font = self.config["figlet_font"]
            width = self.config["width"]
            fig = pyfiglet.Figlet(font=font, width=width)
            figlet_text = fig.renderText(title)

            lines = figlet_text.rstrip("\n").split("\n")
            return lines
        except Exception:
            return [title]

    def draw(self, stdscr, colors: dict):
        """Draw the menu interface."""
        height, width = stdscr.getmaxyx()
        stdscr.clear()

        menu_width = min(self.config["width"], width - 4)
        num_items = min(len(self.all_items), self.config["height"])

        title_lines = self.render_figlet_title(self.title) if self.title else []
        title_height = len(title_lines)

        items_height = num_items + 1

        items_start_y = max(0, (height - items_height) // 2)
        start_y = max(0, items_start_y - title_height)

        if self.centered:

            start_x = max(0, (width - menu_width) // 2)
        else:

            start_x = 0
            menu_width = width - 1

        current_y = start_y

        for title_line in title_lines:
            if current_y >= height:
                break

            if self.centered:
                offset = max(0, (menu_width - len(title_line)) // 2)
                title_x = start_x + offset
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

        sep_y = current_y
        if sep_y < height:
            separator = "─" * menu_width
            try:
                stdscr.addstr(sep_y, start_x, separator, colors["normal"])
            except curses.error:
                pass

        visible_lines = min(len(self.all_items), height - sep_y - 1)
        if visible_lines <= 0:
            stdscr.refresh()
            return

        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible_lines:
            self.scroll_offset = self.selected_index - visible_lines + 1

        self.item_positions = []

        if self.centered:
            max_item_len = 0
            for i in range(visible_lines):
                item_index = i + self.scroll_offset
                if item_index >= len(self.all_items):
                    break
                item = self.all_items[item_index]
                truncated_len = min(len(item), menu_width - 2)
                max_item_len = max(max_item_len, truncated_len)

            text_indent = (menu_width - max_item_len) // 2
        else:
            text_indent = 0

        for i in range(visible_lines):
            item_index = i + self.scroll_offset
            if item_index >= len(self.all_items):
                break

            item = self.all_items[item_index]
            y = sep_y + 1 + i

            display_item = (
                item[: menu_width - 2] if len(item) > menu_width - 2 else item
            )

            item_x = start_x + text_indent

            if self.centered:
                self.item_positions.append(
                    (y, start_x, start_x + menu_width, item_index)
                )
            else:
                self.item_positions.append(
                    (y, item_x, item_x + len(display_item), item_index)
                )

            if item_index == self.selected_index:
                attr = colors["selected"]
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

        if len(self.all_items) > visible_lines:
            try:
                idx = self.selected_index + 1
                total = len(self.all_items)
                scroll_info = f" [{idx}/{total}]"
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
        curses.curs_set(0)
        stdscr.keypad(True)

        mouse_mask = curses.BUTTON1_CLICKED | curses.BUTTON1_DOUBLE_CLICKED
        if hasattr(curses, "BUTTON4_PRESSED"):
            mouse_mask |= curses.BUTTON4_PRESSED
        if hasattr(curses, "BUTTON5_PRESSED"):
            mouse_mask |= curses.BUTTON5_PRESSED
        curses.mousemask(mouse_mask)

        colors = self.get_colors(stdscr)

        while True:
            self.draw(stdscr, colors)

            try:
                key = stdscr.getch()
            except KeyboardInterrupt:
                return None

            if key == ord("\n"):
                result = self._handle_selection(self.selected_index)
                if result is not None or (
                    self.all_items and self.all_items[self.selected_index] == "Exit"
                ):
                    return result
                return None

            elif key in (27, ord("e"), ord("q")):
                return "__GO_BACK__" if self.is_submenu else None

            elif key == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, bstate = curses.getmouse()

                    if (
                        hasattr(curses, "BUTTON4_PRESSED")
                        and bstate & curses.BUTTON4_PRESSED
                    ):
                        self._move_up()
                    elif (
                        hasattr(curses, "BUTTON5_PRESSED")
                        and bstate & curses.BUTTON5_PRESSED
                    ):
                        self._move_down()

                    elif bstate & (
                        curses.BUTTON1_CLICKED | curses.BUTTON1_DOUBLE_CLICKED
                    ):
                        is_double = bool(bstate & curses.BUTTON1_DOUBLE_CLICKED)
                        for y, start_x, end_x, item_idx in self.item_positions:
                            if my == y and start_x <= mx < end_x:
                                if is_double:

                                    result = self._handle_selection(item_idx)
                                    if (
                                        result is not None
                                        or self.all_items[item_idx] == "Exit"
                                    ):
                                        return result
                                else:

                                    self.selected_index = item_idx
                                break
                except Exception:
                    pass

            elif key in (ord("k"), curses.KEY_UP, 16):
                self._move_up()

            elif key in (ord("j"), curses.KEY_DOWN, 14):
                self._move_down()

            elif key in (ord("g"), curses.KEY_HOME, 1):
                self.selected_index = 0

            elif key in (ord("G"), curses.KEY_END, 5):
                self.selected_index = max(0, len(self.all_items) - 1)

            elif ord("1") <= key <= ord("9"):
                item_num = key - ord("1")
                if item_num < len(self.all_items):
                    result = self._handle_selection(item_num)
                    if result is not None or self.all_items[item_num] == "Exit":
                        return result

            elif key == curses.KEY_PPAGE:
                self.selected_index = max(0, self.selected_index - 10)

            elif key == curses.KEY_NPAGE:
                self.selected_index = min(
                    len(self.all_items) - 1, self.selected_index + 10
                )


def _parse_color_value(value) -> int:
    """Convert a color value (hex string, color name, or int) to a terminal color number.

    Supports:
    - Hex colors: "#cba6f7" or "cba6f7"
    - Integer values: 6, -1
    - Named colors: "red", "cyan", etc.

    Returns:
        Terminal color number (int), or -1 for unrecognized values.
    """
    if isinstance(value, int):
        return value

    if isinstance(value, str):
        value = value.strip()

        if value.startswith("#") or (
            len(value) == 6 and all(c in "0123456789abcdefABCDEF" for c in value)
        ):
            hex_color = value.lstrip("#").lower()
            return x256.from_hex(hex_color)

        try:
            return int(value)
        except ValueError:
            pass

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
        return color_map.get(value.lower(), -1)

    return -1


def load_theme(theme_name: str) -> Optional[dict]:
    """Load a theme from various locations.

    Searches in order:
    1. $XDG_CONFIG_HOME/tmenu/themes/{theme_name}.toml
    2. Package installation directory (bundled themes via pip)
    3. System data directories from $XDG_DATA_DIRS

    Returns:
        Dictionary with theme config if theme found, None otherwise
    """
    theme_locations = [
        os.path.join(get_xdg_config_home(), "tmenu", "themes", f"{theme_name}.toml"),
    ]

    script_dir = os.path.dirname(os.path.abspath(__file__))
    theme_locations.append(os.path.join(script_dir, "themes", f"{theme_name}.toml"))

    xdg_data_dirs = os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share")
    for data_dir in xdg_data_dirs.split(":"):
        if data_dir:
            theme_locations.append(
                os.path.join(data_dir, "tmenu", "themes", f"{theme_name}.toml")
            )

    for theme_path in theme_locations:
        if os.path.exists(theme_path):
            try:
                with open(theme_path, "rb") as f:
                    return tomllib.load(f)
            except Exception:
                continue

    return None


def create_default_config():
    """Create default config in $XDG_CONFIG_HOME/tmenu/."""
    config_dir = os.path.join(get_xdg_config_home(), "tmenu")
    config_file = os.path.join(config_dir, "config.toml")

    if os.path.exists(config_file):
        return

    os.makedirs(config_dir, exist_ok=True)

    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_config_path = os.path.join(script_dir, "config.default.toml")

    try:
        with open(default_config_path, "r") as f:
            default_config = f.read()

        with open(config_file, "w") as f:
            f.write(default_config)
    except Exception:
        pass


def load_custom_menus(
    theme_dir: Optional[str] = None,
) -> Tuple[Dict[str, str], Dict[str, Dict[str, str]]]:
    """Load custom menu configurations from specified directory.

    Args:
        theme_dir: Path to theme directory.

    Returns:
        Tuple of (menu_items dict, submenus dict)
    """
    menu_items: Dict[str, str] = {}
    submenus: Dict[str, Dict[str, str]] = {}

    if theme_dir is None:
        return menu_items, submenus

    theme_dir = os.path.expanduser(theme_dir)

    if not os.path.exists(theme_dir) or not os.path.isdir(theme_dir):
        return menu_items, submenus

    try:
        for filename in sorted(os.listdir(theme_dir)):
            if filename.endswith(".toml"):
                menu_path = os.path.join(theme_dir, filename)
                try:
                    with open(menu_path, "rb") as f:
                        data = tomllib.load(f)

                    if "menu" in data:
                        for label, command in data["menu"].items():
                            menu_items[label] = command

                    for section_name, section_data in data.items():
                        if section_name.startswith("submenu."):
                            submenu_name = section_name[8:]
                            if submenu_name not in submenus:
                                submenus[submenu_name] = {}
                            submenus[submenu_name].update(section_data)
                except Exception:
                    continue
    except Exception:
        pass

    return menu_items, submenus


def _parse_display_config(display: dict, config: dict) -> str:
    """Parse the [display] section into config dict. Returns the title string.

    Args:
        display: The raw display section from the TOML data.
        config: The config dict to populate (mutated in place).

    Returns:
        The title string from the display section, or empty string.
    """

    display_fields = {
        "centered": bool,
        "width": int,
        "height": int,
        "figlet": bool,
        "figlet_font": str,
        "theme_dir": str,
    }
    for key, cast in display_fields.items():
        if key in display:
            config[key] = cast(display[key])

    return str(display.get("title", ""))


def load_config(
    config_path: Optional[str] = None,
) -> Tuple[dict, Dict[str, str], Dict[str, Dict[str, str]], str]:
    """Load configuration from file.

    Returns:
        Tuple of (config dict, menu_items dict, submenus dict, title string)
    """
    if config_path is None:

        create_default_config()
        default_path = os.path.join(get_xdg_config_home(), "tmenu", "config.toml")
        if os.path.exists(default_path):
            config_path = default_path

    config: dict = {}
    menu_items: Dict[str, str] = {}
    submenus: Dict[str, Dict[str, str]] = {}
    title = ""

    data = None

    if config_path and os.path.exists(config_path):
        try:
            with open(config_path, "rb") as f:
                data = tomllib.load(f)
        except Exception:
            pass

    if data and "display" in data and "theme" in data["display"]:
        theme_name = data["display"]["theme"]

        if theme_name and theme_name.strip():
            theme_data = load_theme(theme_name)

            if theme_data and "colors" in theme_data:
                for key, value in theme_data["colors"].items():
                    config[key] = _parse_color_value(value)

    if data and "colors" in data:
        for key, value in data["colors"].items():
            config[key] = _parse_color_value(value)

    if data:
        if "display" in data:
            title = _parse_display_config(data["display"], config)

        if "menu" in data:
            for label, command in data["menu"].items():
                menu_items[label] = command

        for section_name, section_data in data.items():
            if section_name.startswith("submenu."):
                submenu_name = section_name[8:]
                submenus[submenu_name] = dict(section_data)

    theme_dir = config.get("theme_dir")
    custom_menu_items, custom_submenus = load_custom_menus(theme_dir)
    menu_items.update(custom_menu_items)
    for submenu_name, submenu_items in custom_submenus.items():
        if submenu_name in submenus:
            submenus[submenu_name].update(submenu_items)
        else:
            submenus[submenu_name] = submenu_items

    return config, menu_items, submenus, title


def read_stdin_items() -> List[str]:
    """Read menu items from stdin.

    Returns:
        List of non-empty lines from stdin
    """
    items = []
    for line in sys.stdin:
        line = line.rstrip("\n\r")
        if line:
            items.append(line)
    return items


def _run_stdin_mode(args, config: dict) -> None:
    """Run tmenu in stdin/pipe mode (dmenu-like).

    Reads items from stdin, displays a selection menu, and prints
    the selected item to stdout.
    """
    stdin_items = read_stdin_items()

    if not stdin_items:
        print("Error: No items received from stdin.", file=sys.stderr)
        sys.exit(1)

    title = args.placeholder if args.placeholder else ""

    menu = TMenu(
        stdin_items,
        config=config,
        menu_items={},
        submenus={},
        title=title,
        is_submenu=False,
    )

    try:
        with open("/dev/tty", "r") as tty_input:
            # dup2 required because curses reads from fd 0 directly
            old_stdin_fd = os.dup(0)
            os.dup2(tty_input.fileno(), 0)
            old_stdin = sys.stdin
            sys.stdin = tty_input

            try:
                selection = curses.wrapper(menu.run)
            except KeyboardInterrupt:
                sys.exit(130)
            finally:

                os.dup2(old_stdin_fd, 0)
                os.close(old_stdin_fd)
                sys.stdin = old_stdin
    except (OSError, IOError):
        print("Error: Cannot open /dev/tty for interactive input.", file=sys.stderr)
        sys.exit(1)

    if selection and not selection.startswith("__"):
        print(selection)
        sys.exit(0)
    else:
        sys.exit(1)


def _run_config_mode(
    args,
    config: dict,
    menu_items: Dict[str, str],
    submenus: Dict[str, Dict[str, str]],
    title: str,
) -> None:
    """Run tmenu in config mode (command executor).

    Displays menu items from config, supports submenus, and executes
    the selected command.
    """
    if not menu_items:
        print("Error: No menu items found in configuration.", file=sys.stderr)
        config_path = f"{get_xdg_config_home()}/tmenu/config.toml"
        print(
            f"Please create a config file at {config_path}",
            file=sys.stderr,
        )
        print("with a [menu] section defining your menu items.", file=sys.stderr)
        sys.exit(1)

    menu_stack: List[Tuple[str, str]] = []
    current_items = list(menu_items.keys())
    current_menu_items: Dict[str, str] = menu_items
    current_title = title

    while True:
        is_submenu = len(menu_stack) > 0

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
            if menu_stack:
                menu_stack.pop()
                if menu_stack:
                    submenu_name, submenu_label = menu_stack[-1]
                    current_items = list(submenus[submenu_name].keys())
                    current_menu_items = submenus[submenu_name]
                    current_title = submenu_label
                else:
                    current_items = list(menu_items.keys())
                    current_menu_items = menu_items
                    current_title = title
            continue
        elif selection and selection.startswith("__SUBMENU__"):
            parts = selection.split("__")
            submenu_name = parts[2]
            submenu_label = parts[3] if len(parts) > 3 else submenu_name
            menu_stack.append((submenu_name, submenu_label))
            current_items = list(submenus[submenu_name].keys())
            current_menu_items = submenus[submenu_name]
            current_title = submenu_label
            continue
        elif selection:
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
            sys.exit(0)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="tmenu - A configurable terminal menu")
    parser.add_argument("-c", "--config", help="Path to configuration file")
    parser.add_argument(
        "--placeholder", help="Title to display when reading from stdin"
    )

    args = parser.parse_args()

    config, menu_items, submenus, title = load_config(args.config)

    if not sys.stdin.isatty():
        _run_stdin_mode(args, config)
    else:
        _run_config_mode(args, config, menu_items, submenus, title)
