"""Color parsing utilities."""

from __future__ import annotations

from x256 import x256  # type: ignore[import-untyped]

NAMED_COLORS: dict[str, int] = {
    "black": 0,
    "red": 1,
    "green": 2,
    "yellow": 3,
    "blue": 4,
    "magenta": 5,
    "cyan": 6,
    "white": 7,
}


def _is_hex6(s: str) -> bool:
    return len(s) == 6 and all(c in "0123456789abcdefABCDEF" for c in s)


def parse_color(value: int | str) -> int:
    """Convert a hex string, color name, or int to a 256-color terminal number."""
    if isinstance(value, int):
        return value
    if not isinstance(value, str):
        return -1

    value = value.strip()

    if value.startswith("#") or _is_hex6(value):
        return x256.from_hex(value.lstrip("#").lower())

    try:
        return int(value)
    except ValueError:
        return NAMED_COLORS.get(value.lower(), -1)
