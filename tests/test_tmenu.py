#!/usr/bin/env python3
"""
Tests for tmenu
"""

import pytest

from tmenu import TMenu, load_config


class TestTMenu:
    """Test cases for TMenu class."""

    def test_initialization(self):
        """Test TMenu initialization."""
        items = ["item1", "item2", "item3"]
        menu = TMenu(items)

        # Items should include Exit option
        assert "Exit" in menu.all_items
        assert menu.selected_index == 0
        assert isinstance(menu.config, dict)

    def test_initialization_with_config(self):
        """Test TMenu initialization with config."""
        items = ["item1", "item2"]
        config = {"width": 60, "height": 10}
        menu = TMenu(items, config=config)

        assert menu.config["width"] == 60
        assert menu.config["height"] == 10

    def test_submenu_has_back_option(self):
        """Test that submenus have Back option."""
        items = ["item1", "item2"]
        menu = TMenu(items, is_submenu=True)

        assert "← Back" in menu.all_items
        assert "Exit" in menu.all_items

    def test_order_preservation(self):
        """Test that items preserve original order (not sorted)."""
        items = ["zebra", "apple", "monkey", "banana"]
        menu = TMenu(items)

        # Check that the initial items preserve original order (before Exit is added)
        all_items_without_exit = [item for item in menu.all_items if item != "Exit"]
        assert all_items_without_exit == ["zebra", "apple", "monkey", "banana"]


class TestHandleSelection:
    """Test cases for TMenu._handle_selection()."""

    def test_regular_item_returns_item(self):
        """Selecting a regular item returns its label (no menu_items mapping)."""
        menu = TMenu(["item1", "item2"])
        result = menu._handle_selection(0)
        assert result == "item1"

    def test_mapped_item_returns_command(self):
        """Selecting a mapped item returns the command from menu_items."""
        menu = TMenu(["Browser"], menu_items={"Browser": "firefox"})
        result = menu._handle_selection(0)
        assert result == "firefox"

    def test_exit_returns_none(self):
        """Selecting Exit returns None."""
        menu = TMenu(["item1"])
        exit_index = menu.all_items.index("Exit")
        result = menu._handle_selection(exit_index)
        assert result is None

    def test_back_returns_go_back(self):
        """Selecting '← Back' returns the __GO_BACK__ sentinel."""
        menu = TMenu(["item1"], is_submenu=True)
        back_index = menu.all_items.index("← Back")
        result = menu._handle_selection(back_index)
        assert result == "__GO_BACK__"

    def test_submenu_item_returns_submenu_sentinel(self):
        """Selecting a submenu item returns the __SUBMENU__ sentinel."""
        submenus = {"Apps": {"Browser": "firefox"}}
        menu = TMenu(
            ["Apps"],
            menu_items={"Apps": "submenu:Apps"},
            submenus=submenus,
        )
        result = menu._handle_selection(0)
        assert result == "__SUBMENU__Apps__Apps"

    def test_out_of_range_returns_none(self):
        """Selecting an out-of-range index returns None."""
        menu = TMenu(["item1"])
        result = menu._handle_selection(999)
        assert result is None


class TestLoadConfig:
    """Test cases for load_config function."""

    def test_load_config_nonexistent_file(self):
        """Test loading config from nonexistent file."""
        config, menu_items, submenus, title = load_config(
            "/nonexistent/path/config.toml"
        )
        assert isinstance(config, dict)
        assert isinstance(menu_items, dict)
        assert isinstance(submenus, dict)

    def test_load_config_color_names(self, tmp_path):
        """Test loading config with color names."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            """
[colors]
foreground = "white"
background = "black"
"""
        )

        config, menu_items, submenus, title = load_config(str(config_file))
        assert config["foreground"] == 7  # white
        assert config["background"] == 0  # black

    def test_load_config_color_numbers(self, tmp_path):
        """Test loading config with color numbers."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            """
[colors]
foreground = 7
background = -1
selection_background = 6
"""
        )

        config, menu_items, submenus, title = load_config(str(config_file))
        assert config["foreground"] == 7
        assert config["background"] == -1
        assert config["selection_background"] == 6

    def test_load_config_invalid_color(self, tmp_path):
        """Test loading config with invalid color name."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            """
[colors]
foreground = "invalid_color"
"""
        )

        config, menu_items, submenus, title = load_config(str(config_file))
        assert config["foreground"] == -1  # defaults to -1 for invalid

    def test_load_config_display_without_colors(self, tmp_path):
        """Test loading config with display section but no colors section."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            """
[display]
centered = false
width = 80
title = "Test"
"""
        )

        config, menu_items, submenus, title = load_config(str(config_file))
        assert config["centered"] is False
        assert config["width"] == 80
        assert title == "Test"


class TestIntegration:
    """Integration tests."""

    def test_menu_with_config(self, tmp_path):
        """Test creating menu with config."""
        config_file = tmp_path / "config.toml"
        config_file.write_text(
            """
[colors]
foreground = "cyan"
background = "black"
"""
        )

        config, menu_items, submenus, title = load_config(str(config_file))
        items = ["test1", "test2", "test3"]
        menu = TMenu(items, config=config)

        assert menu.config["foreground"] == 6  # cyan
        assert menu.config["background"] == 0  # black

    def test_menu_basic_creation(self):
        """Test basic menu creation."""
        items = ["firefox", "chromium", "brave", "vim", "emacs", "nano"]
        menu = TMenu(items)

        # Menu should have the items plus Exit
        assert len(menu.all_items) == len(items) + 1  # +1 for Exit
        assert "Exit" in menu.all_items
