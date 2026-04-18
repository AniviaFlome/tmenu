"""Configuration and theme loading."""

from __future__ import annotations

import os
from pathlib import Path

try:
    import tomllib
except ImportError:
    import tomli as tomllib  # type: ignore[no-redef]

from tmenu.colors import parse_color
from tmenu.types import Config


def _xdg_config_home() -> Path:
    return Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))


def _load_toml(path: Path) -> dict | None:
    """Load a TOML file, returning None on failure."""
    try:
        with open(path, "rb") as f:
            return tomllib.load(f)
    except (OSError, tomllib.TOMLDecodeError):
        return None


def load_theme(theme_name: str) -> dict | None:
    """Search for a theme TOML in XDG config, package dir, and XDG data dirs."""
    candidates = [
        _xdg_config_home() / "tmenu" / "themes" / f"{theme_name}.toml",
        Path(__file__).parent / "themes" / f"{theme_name}.toml",
    ]
    for d in os.environ.get("XDG_DATA_DIRS", "/usr/local/share:/usr/share").split(":"):
        if d:
            candidates.append(Path(d) / "tmenu" / "themes" / f"{theme_name}.toml")

    for path in candidates:
        if path.exists():
            data = _load_toml(path)
            if data is not None:
                return data
    return None


def _load_custom_menus(
    menu_dir: str,
) -> tuple[dict[str, str], dict[str, dict[str, str]]]:
    """Load .toml menu files from a directory."""
    items: dict[str, str] = {}
    subs: dict[str, dict[str, str]] = {}

    if not menu_dir:
        return items, subs

    dirpath = Path(menu_dir).expanduser()
    if not dirpath.is_dir():
        return items, subs

    for path in sorted(dirpath.glob("*.toml")):
        data = _load_toml(path)
        if data is None:
            continue
        if "menu" in data:
            items.update(data["menu"])
        for key, val in data.items():
            if key.startswith("submenu."):
                subs.setdefault(key[8:], {}).update(val)

    return items, subs


def _apply_colors(opts: Config, colors: dict) -> None:
    """Set color fields on *opts* from a ``{name: value}`` mapping."""
    for key, val in colors.items():
        if hasattr(opts, key):
            setattr(opts, key, parse_color(val))


def _apply_display(opts: Config, display: dict) -> str:
    """Set display fields on *opts* and return the title string."""
    _fields = {"centered", "width", "height", "figlet", "figlet_font", "theme_dir"}
    for key, val in display.items():
        if key in _fields:
            expected = type(getattr(opts, key))
            setattr(opts, key, expected(val))
    return str(display.get("title", ""))


def load_config(
    config_path: str | None = None,
) -> tuple[Config, dict[str, str], dict[str, dict[str, str]], str]:
    """Load configuration, menu items, submenus, and title from a TOML file.

    If no path is given, looks for ``$XDG_CONFIG_HOME/tmenu/config.toml``.
    Missing files are not an error — the Config dataclass defaults apply.
    """
    if config_path is None:
        default = _xdg_config_home() / "tmenu" / "config.toml"
        if default.exists():
            config_path = str(default)

    opts = Config()
    menu_items: dict[str, str] = {}
    submenus: dict[str, dict[str, str]] = {}
    title = ""

    data = _load_toml(Path(config_path)) if config_path else None
    if data is None:
        return opts, menu_items, submenus, title

    # Theme colors (lowest priority)
    display = data.get("display", {})
    theme_name = display.get("theme", "").strip()
    if theme_name:
        theme = load_theme(theme_name)
        if theme and "colors" in theme:
            _apply_colors(opts, theme["colors"])

    # Explicit colors override theme
    if "colors" in data:
        _apply_colors(opts, data["colors"])

    # Display settings + title
    if display:
        title = _apply_display(opts, display)

    # Menu items and submenus
    if "menu" in data:
        menu_items.update(data["menu"])
    for key, val in data.items():
        if key.startswith("submenu."):
            submenus[key[8:]] = dict(val)

    # Merge custom menus from theme_dir
    custom_items, custom_subs = _load_custom_menus(opts.theme_dir)
    menu_items.update(custom_items)
    for name, sub_items in custom_subs.items():
        submenus.setdefault(name, {}).update(sub_items)

    return opts, menu_items, submenus, title
