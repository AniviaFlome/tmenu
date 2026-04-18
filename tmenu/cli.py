"""CLI entry points and run modes."""

from __future__ import annotations

import argparse
import curses
import os
import shlex
import sys

from tmenu.config import _xdg_config_home, load_config
from tmenu.menu import TMenu
from tmenu.types import Action, Config


def _run_stdin_mode(title: str, config: Config) -> None:
    """Pipe mode: read items from stdin, print selection to stdout."""
    items = [line for line in sys.stdin.read().splitlines() if line.strip()]
    if not items:
        print("Error: No items received from stdin.", file=sys.stderr)
        sys.exit(1)

    menu = TMenu(items, config=config, title=title)

    try:
        with open("/dev/tty", "r") as tty:
            saved_fd = os.dup(0)
            os.dup2(tty.fileno(), 0)
            saved_stdin = sys.stdin
            sys.stdin = tty
            try:
                result = curses.wrapper(menu.run)
            except KeyboardInterrupt:
                sys.exit(130)
            finally:
                os.dup2(saved_fd, 0)
                os.close(saved_fd)
                sys.stdin = saved_stdin
    except OSError:
        print("Error: Cannot open /dev/tty for interactive input.", file=sys.stderr)
        sys.exit(1)

    if result is not None and result.action == Action.COMMAND:
        print(result.value)
        sys.exit(0)
    sys.exit(1)


def _run_config_mode(
    config: Config,
    menu_items: dict[str, str],
    submenus: dict[str, dict[str, str]],
    title: str,
) -> None:
    """Config mode: navigate menus and execute the selected command."""
    if not menu_items:
        cfg_path = _xdg_config_home() / "tmenu" / "config.toml"
        print(
            f"Error: No menu items found in configuration.\n"
            f"Please create a config file at {cfg_path}\n"
            f"with a [menu] section defining your menu items.",
            file=sys.stderr,
        )
        sys.exit(1)

    stack: list[tuple[str, str]] = []
    cur_items = menu_items
    cur_title = title

    while True:
        menu = TMenu(
            list(cur_items.keys()),
            config=config,
            menu_items=cur_items,
            submenus=submenus,
            title=cur_title,
            is_submenu=bool(stack),
        )

        try:
            sel = curses.wrapper(menu.run)
        except KeyboardInterrupt:
            sys.exit(130)

        if sel is None or sel.action == Action.EXIT:
            sys.exit(0)

        if sel.action == Action.BACK:
            if stack:
                stack.pop()
                if stack:
                    name, label = stack[-1]
                    cur_items = submenus[name]
                    cur_title = label
                else:
                    cur_items = menu_items
                    cur_title = title
            continue

        if sel.action == Action.SUBMENU:
            stack.append((sel.value, sel.label))
            cur_items = submenus[sel.value]
            cur_title = sel.label
            continue

        try:
            parts = shlex.split(sel.value)
            os.execvp(parts[0], parts)
        except FileNotFoundError:
            print(f"tmenu: command not found: {sel.value}", file=sys.stderr)
            sys.exit(127)
        except PermissionError:
            print(f"tmenu: permission denied: {sel.value}", file=sys.stderr)
            sys.exit(126)
        except Exception as e:
            print(f"tmenu: error executing command: {e}", file=sys.stderr)
            sys.exit(1)


def main() -> None:
    """CLI entry point."""
    parser = argparse.ArgumentParser(description="tmenu - A configurable terminal menu")
    parser.add_argument("-c", "--config", help="Path to configuration file")
    parser.add_argument(
        "--placeholder", help="Title to display when reading from stdin"
    )
    args = parser.parse_args()

    config, menu_items, submenus, title = load_config(args.config)

    if not sys.stdin.isatty():
        _run_stdin_mode(args.placeholder or "", config)
    else:
        _run_config_mode(config, menu_items, submenus, title)
