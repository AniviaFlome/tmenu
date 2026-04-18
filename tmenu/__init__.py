"""tmenu - dmenu for terminal"""

from tmenu.cli import main
from tmenu.colors import parse_color
from tmenu.config import load_config, load_theme
from tmenu.menu import TMenu
from tmenu.types import Action, Config, Selection

__all__ = [
    "TMenu",
    "Config",
    "Action",
    "Selection",
    "main",
    "load_config",
    "load_theme",
    "parse_color",
]
