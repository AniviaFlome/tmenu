"""TMenu: interactive terminal menu."""

from __future__ import annotations

import curses

try:
    import pyfiglet  # type: ignore[import-untyped]
except ImportError:
    pyfiglet = None

from tmenu.types import Action, ColorScheme, Config, ItemPosition, Selection

_LABEL_BACK = "← Back"
_LABEL_EXIT = "Exit"
_SUBMENU_PREFIX = "submenu:"

_KEYS_UP = frozenset({ord("k"), curses.KEY_UP, 16})  # k, Up, Ctrl-P
_KEYS_DOWN = frozenset({ord("j"), curses.KEY_DOWN, 14})  # j, Down, Ctrl-N
_KEYS_HOME = frozenset({ord("g"), curses.KEY_HOME, 1})  # g, Home, Ctrl-A
_KEYS_END = frozenset({ord("G"), curses.KEY_END, 5})  # G, End, Ctrl-E
_KEYS_QUIT = frozenset({27, ord("e"), ord("q")})  # Esc, e, q


class TMenu:
    """Interactive terminal menu with keyboard and mouse navigation."""

    def __init__(
        self,
        items: list[str],
        config: Config | dict | None = None,
        menu_items: dict[str, str] | None = None,
        submenus: dict[str, dict[str, str]] | None = None,
        title: str = "",
        is_submenu: bool = False,
    ):
        self.all_items = list(items)
        if is_submenu:
            self.all_items.append(_LABEL_BACK)
        self.all_items.append(_LABEL_EXIT)

        self.selected_index = 0
        self.scroll_offset = 0
        self.menu_items = menu_items or {}
        self.submenus = submenus or {}
        self.title = title
        self.is_submenu = is_submenu
        self._positions: list[ItemPosition] = []

        if isinstance(config, Config):
            self.config = config
        else:
            merged = {**Config().__dict__, **(config or {})}
            self.config = Config(
                **{k: v for k, v in merged.items() if k in Config.__dataclass_fields__}
            )

    # ── Navigation ──────────────────────────────────────────────────────────

    def _move_up(self) -> None:
        if self.selected_index > 0:
            self.selected_index -= 1
        else:
            self.selected_index = len(self.all_items) - 1

    def _move_down(self) -> None:
        if self.selected_index < len(self.all_items) - 1:
            self.selected_index += 1
        else:
            self.selected_index = 0

    # ── Selection ────────────────────────────────────────────────────────────

    def _handle_selection(self, index: int) -> Selection | None:
        """Resolve what a given index means. Returns None for invalid indices."""
        if index >= len(self.all_items):
            return None

        item = self.all_items[index]
        if item == _LABEL_BACK:
            return Selection(Action.BACK)
        if item == _LABEL_EXIT:
            return Selection(Action.EXIT)

        command = self.menu_items.get(item, item)
        if command.startswith(_SUBMENU_PREFIX):
            name = command[len(_SUBMENU_PREFIX) :]
            if name in self.submenus:
                return Selection(Action.SUBMENU, name, item)

        return Selection(Action.COMMAND, command)

    # ── Rendering ────────────────────────────────────────────────────────────

    def _init_colors(self, stdscr) -> ColorScheme:
        cfg = self.config
        if curses.has_colors():
            curses.use_default_colors()
            curses.init_pair(1, cfg.foreground, cfg.background)
            curses.init_pair(2, cfg.selection_foreground, cfg.selection_background)
            curses.init_pair(3, cfg.prompt_foreground, cfg.background)
            return ColorScheme(
                normal=curses.color_pair(1),
                selected=curses.color_pair(2),
                prompt=curses.color_pair(3) | curses.A_BOLD,
            )
        return ColorScheme(
            normal=curses.A_NORMAL,
            selected=curses.A_REVERSE,
            prompt=curses.A_BOLD,
        )

    def _render_title(self) -> list[str]:
        if not self.title:
            return []
        if pyfiglet is None or not self.config.figlet:
            return [self.title]
        try:
            fig = pyfiglet.Figlet(font=self.config.figlet_font, width=self.config.width)
            return fig.renderText(self.title).rstrip("\n").split("\n")
        except Exception:
            return [self.title]

    def _draw(self, stdscr, colors: ColorScheme) -> None:
        term_h, term_w = stdscr.getmaxyx()
        stdscr.clear()

        cfg = self.config
        menu_w = min(cfg.width, term_w - 4)

        title_lines = self._render_title()
        items_height = min(len(self.all_items), cfg.height) + 1

        items_start_y = max(0, (term_h - items_height) // 2)
        start_y = max(0, items_start_y - len(title_lines))

        if cfg.centered:
            start_x = max(0, (term_w - menu_w) // 2)
        else:
            start_x = 0
            menu_w = term_w - 1

        # Title
        y = start_y
        for line in title_lines:
            if y >= term_h:
                break
            tx = (
                start_x + max(0, (menu_w - len(line)) // 2) if cfg.centered else start_x
            )
            try:
                stdscr.addstr(y, tx, line[:menu_w], colors.prompt)
            except curses.error:
                pass
            y += 1

        # Separator
        sep_y = y
        if sep_y < term_h:
            try:
                stdscr.addstr(sep_y, start_x, "─" * menu_w, colors.normal)
            except curses.error:
                pass

        # Scrollable item list
        visible = min(len(self.all_items), term_h - sep_y - 1)
        if visible <= 0:
            stdscr.refresh()
            return

        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible:
            self.scroll_offset = self.selected_index - visible + 1

        if cfg.centered:
            max_len = max(
                (
                    min(len(self.all_items[i + self.scroll_offset]), menu_w - 2)
                    for i in range(visible)
                    if i + self.scroll_offset < len(self.all_items)
                ),
                default=0,
            )
            indent = (menu_w - max_len) // 2
        else:
            indent = 0

        self._positions = []
        for i in range(visible):
            idx = i + self.scroll_offset
            if idx >= len(self.all_items):
                break

            item = self.all_items[idx]
            iy = sep_y + 1 + i
            display = item[: menu_w - 2] if len(item) > menu_w - 2 else item
            ix = start_x + indent

            if cfg.centered:
                self._positions.append(ItemPosition(iy, start_x, start_x + menu_w, idx))
            else:
                self._positions.append(ItemPosition(iy, ix, ix + len(display), idx))

            if idx == self.selected_index:
                attr = colors.selected
                display = " " * indent + display.ljust(menu_w - indent)
                ix = start_x
            else:
                attr = colors.normal

            try:
                stdscr.addstr(iy, ix, display[:menu_w], attr)
            except curses.error:
                pass

        if len(self.all_items) > visible:
            info = f" [{self.selected_index + 1}/{len(self.all_items)}]"
            try:
                stdscr.addstr(sep_y, start_x + menu_w - len(info), info, colors.normal)
            except curses.error:
                pass

        stdscr.refresh()

    # ── Input handling ───────────────────────────────────────────────────────

    def _handle_mouse(self, bstate: int, mx: int, my: int) -> Selection | None:
        if hasattr(curses, "BUTTON4_PRESSED") and bstate & curses.BUTTON4_PRESSED:
            self._move_up()
            return None
        if hasattr(curses, "BUTTON5_PRESSED") and bstate & curses.BUTTON5_PRESSED:
            self._move_down()
            return None

        if bstate & (curses.BUTTON1_CLICKED | curses.BUTTON1_DOUBLE_CLICKED):
            is_double = bool(bstate & curses.BUTTON1_DOUBLE_CLICKED)
            for pos in self._positions:
                if my == pos.y and pos.x_start <= mx < pos.x_end:
                    if is_double:
                        return self._handle_selection(pos.idx)
                    self.selected_index = pos.idx
                    break
        return None

    def run(self, stdscr) -> Selection | None:
        """Run the interactive menu loop. Returns a Selection or None if cancelled."""
        curses.curs_set(0)
        stdscr.keypad(True)

        mouse_mask = curses.BUTTON1_CLICKED | curses.BUTTON1_DOUBLE_CLICKED
        if hasattr(curses, "BUTTON4_PRESSED"):
            mouse_mask |= curses.BUTTON4_PRESSED
        if hasattr(curses, "BUTTON5_PRESSED"):
            mouse_mask |= curses.BUTTON5_PRESSED
        curses.mousemask(mouse_mask)

        colors = self._init_colors(stdscr)

        while True:
            self._draw(stdscr, colors)

            try:
                key = stdscr.getch()
            except KeyboardInterrupt:
                return None

            if key == ord("\n"):
                result = self._handle_selection(self.selected_index)
                if result is not None:
                    return result

            elif key in _KEYS_QUIT:
                return Selection(Action.BACK) if self.is_submenu else None

            elif key == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, bstate = curses.getmouse()
                    result = self._handle_mouse(bstate, mx, my)
                    if result is not None:
                        return result
                except curses.error:
                    pass

            elif key in _KEYS_UP:
                self._move_up()
            elif key in _KEYS_DOWN:
                self._move_down()
            elif key in _KEYS_HOME:
                self.selected_index = 0
            elif key in _KEYS_END:
                self.selected_index = len(self.all_items) - 1
            elif key == curses.KEY_PPAGE:
                self.selected_index = max(0, self.selected_index - 10)
            elif key == curses.KEY_NPAGE:
                self.selected_index = min(
                    len(self.all_items) - 1, self.selected_index + 10
                )
            elif ord("1") <= key <= ord("9"):
                result = self._handle_selection(key - ord("1"))
                if result is not None:
                    return result
