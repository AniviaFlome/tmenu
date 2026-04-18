"""Core types and data structures."""

from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import NamedTuple


class Action(enum.Enum):
    EXIT = enum.auto()
    BACK = enum.auto()
    SUBMENU = enum.auto()
    COMMAND = enum.auto()


class Selection(NamedTuple):
    action: Action
    value: str = ""
    label: str = ""


class ItemPosition(NamedTuple):
    y: int
    x_start: int
    x_end: int
    idx: int


class ColorScheme(NamedTuple):
    normal: int
    selected: int
    prompt: int


@dataclass
class Config:
    """Display and color configuration with sensible defaults."""

    foreground: int = 7  # white
    background: int = -1  # terminal default
    selection_foreground: int = 0  # black
    selection_background: int = 6  # cyan
    prompt_foreground: int = 4  # blue
    centered: bool = True
    width: int = 60
    height: int = 10
    figlet: bool = False
    figlet_font: str = "standard"
    theme_dir: str = ""
