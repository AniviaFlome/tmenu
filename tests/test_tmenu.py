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

        # Items should be sorted and include Exit option
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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
