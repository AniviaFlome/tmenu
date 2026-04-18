#!/usr/bin/env python3
"""Tests for tmenu"""

from tmenu import Action, Config, Selection, TMenu, load_config


class TestTMenu:
    def test_initialization(self):
        menu = TMenu(["item1", "item2", "item3"])
        assert "Exit" in menu.all_items
        assert menu.selected_index == 0
        assert isinstance(menu.config, Config)

    def test_initialization_with_config(self):
        menu = TMenu(["item1", "item2"], config=Config(width=80, height=15))
        assert menu.config.width == 80
        assert menu.config.height == 15

    def test_initialization_with_legacy_dict(self):
        menu = TMenu(["item1"], config={"width": 50, "height": 5})
        assert menu.config.width == 50
        assert menu.config.height == 5

    def test_submenu_has_back_option(self):
        menu = TMenu(["item1", "item2"], is_submenu=True)
        assert "← Back" in menu.all_items
        assert "Exit" in menu.all_items

    def test_order_preservation(self):
        items = ["zebra", "apple", "monkey", "banana"]
        menu = TMenu(items)
        user_items = [i for i in menu.all_items if i != "Exit"]
        assert user_items == items


class TestHandleSelection:
    def test_regular_item(self):
        menu = TMenu(["item1", "item2"])
        assert menu._handle_selection(0) == Selection(Action.COMMAND, "item1")

    def test_mapped_item(self):
        menu = TMenu(["Browser"], menu_items={"Browser": "firefox"})
        assert menu._handle_selection(0) == Selection(Action.COMMAND, "firefox")

    def test_exit(self):
        menu = TMenu(["item1"])
        idx = menu.all_items.index("Exit")
        assert menu._handle_selection(idx) == Selection(Action.EXIT)

    def test_back(self):
        menu = TMenu(["item1"], is_submenu=True)
        idx = menu.all_items.index("← Back")
        assert menu._handle_selection(idx) == Selection(Action.BACK)

    def test_submenu(self):
        subs = {"Apps": {"Browser": "firefox"}}
        menu = TMenu(["Apps"], menu_items={"Apps": "submenu:Apps"}, submenus=subs)
        assert menu._handle_selection(0) == Selection(Action.SUBMENU, "Apps", "Apps")

    def test_out_of_range(self):
        menu = TMenu(["item1"])
        assert menu._handle_selection(999) is None


class TestLoadConfig:
    def test_nonexistent_file(self):
        config, menu_items, submenus, title = load_config(
            "/nonexistent/path/config.toml"
        )
        assert isinstance(config, Config)
        assert isinstance(menu_items, dict)
        assert isinstance(submenus, dict)

    def test_color_names(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_text('[colors]\nforeground = "white"\nbackground = "black"\n')
        config, _, _, _ = load_config(str(f))
        assert config.foreground == 7
        assert config.background == 0

    def test_color_numbers(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_text(
            "[colors]\nforeground = 7\nbackground = -1\nselection_background = 6\n"
        )
        config, _, _, _ = load_config(str(f))
        assert config.foreground == 7
        assert config.background == -1
        assert config.selection_background == 6

    def test_invalid_color(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_text('[colors]\nforeground = "invalid_color"\n')
        config, _, _, _ = load_config(str(f))
        assert config.foreground == -1

    def test_display_without_colors(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_text('[display]\ncentered = false\nwidth = 80\ntitle = "Test"\n')
        config, _, _, title = load_config(str(f))
        assert config.centered is False
        assert config.width == 80
        assert title == "Test"


class TestIntegration:
    def test_menu_with_config(self, tmp_path):
        f = tmp_path / "config.toml"
        f.write_text('[colors]\nforeground = "cyan"\nbackground = "black"\n')
        config, _, _, _ = load_config(str(f))
        menu = TMenu(["test1", "test2", "test3"], config=config)
        assert menu.config.foreground == 6
        assert menu.config.background == 0

    def test_menu_basic_creation(self):
        items = ["firefox", "chromium", "brave", "vim", "emacs", "nano"]
        menu = TMenu(items)
        assert len(menu.all_items) == len(items) + 1
        assert "Exit" in menu.all_items
