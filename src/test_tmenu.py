#!/usr/bin/env python3
"""
Tests for tmenu
"""

import pytest
from tmenu import TMenu, get_path_commands, load_config
import os


class TestTMenu:
    """Test cases for TMenu class."""
    
    def test_initialization(self):
        """Test TMenu initialization."""
        items = ["item1", "item2", "item3"]
        menu = TMenu(items, prompt="> ")
        
        assert menu.all_items == sorted(items)
        assert menu.filtered_items == sorted(items)
        assert menu.prompt == "> "
        assert menu.query == ""
        assert menu.selected_index == 0
    
    def test_filter_items_empty_query(self):
        """Test filtering with empty query returns all items."""
        items = ["apple", "banana", "cherry"]
        menu = TMenu(items)
        
        result = menu.filter_items("")
        assert result == menu.all_items
    
    def test_filter_items_exact_match(self):
        """Test filtering with exact match."""
        items = ["apple", "banana", "cherry"]
        menu = TMenu(items)
        
        result = menu.filter_items("banana")
        assert result == ["banana"]
    
    def test_filter_items_fuzzy_match(self):
        """Test fuzzy matching."""
        items = ["firefox", "chromium", "brave", "safari"]
        menu = TMenu(items)
        
        # Should match firefox
        result = menu.filter_items("ff")
        assert "firefox" in result
        
        # Should match chromium
        result = menu.filter_items("chr")
        assert "chromium" in result
    
    def test_filter_items_no_match(self):
        """Test filtering with no matches."""
        items = ["apple", "banana", "cherry"]
        menu = TMenu(items)
        
        result = menu.filter_items("xyz")
        assert result == []
    
    def test_filter_items_case_insensitive(self):
        """Test case-insensitive filtering."""
        items = ["Apple", "Banana", "Cherry"]
        menu = TMenu(items)
        
        result = menu.filter_items("apple")
        assert len(result) == 1
        assert result[0].lower() == "apple"
        
        result = menu.filter_items("BANANA")
        assert len(result) == 1
        assert result[0].lower() == "banana"
    
    def test_filter_items_partial_match(self):
        """Test partial matching."""
        items = ["test_one", "test_two", "other"]
        menu = TMenu(items)
        
        result = menu.filter_items("test")
        assert len(result) == 2
        assert "test_one" in result
        assert "test_two" in result
    
    def test_sorting(self):
        """Test that items are sorted."""
        items = ["zebra", "apple", "monkey", "banana"]
        menu = TMenu(items)
        
        assert menu.all_items == ["apple", "banana", "monkey", "zebra"]


class TestGetPathCommands:
    """Test cases for get_path_commands function."""
    
    def test_get_path_commands_returns_list(self):
        """Test that get_path_commands returns a list."""
        commands = get_path_commands()
        assert isinstance(commands, list)
    
    def test_get_path_commands_not_empty(self):
        """Test that PATH has some commands."""
        commands = get_path_commands()
        # Most systems should have at least some commands in PATH
        assert len(commands) > 0
    
    def test_get_path_commands_common_commands(self):
        """Test that common commands are found."""
        commands = get_path_commands()
        # These commands should exist on most Unix-like systems
        common_commands = ["ls", "cat", "echo"]
        found = [cmd for cmd in common_commands if cmd in commands]
        # At least one common command should be found
        assert len(found) > 0


class TestLoadConfig:
    """Test cases for load_config function."""
    
    def test_load_config_nonexistent_file(self):
        """Test loading config from nonexistent file."""
        config = load_config("/nonexistent/path/config.ini")
        assert config == {}
    
    def test_load_config_color_names(self, tmp_path):
        """Test loading config with color names."""
        config_file = tmp_path / "config.ini"
        config_file.write_text("""
[colors]
foreground = white
background = black
""")
        
        config = load_config(str(config_file))
        assert config["foreground"] == 7  # white
        assert config["background"] == 0  # black
    
    def test_load_config_color_numbers(self, tmp_path):
        """Test loading config with color numbers."""
        config_file = tmp_path / "config.ini"
        config_file.write_text("""
[colors]
foreground = 7
background = -1
selection_background = 6
""")
        
        config = load_config(str(config_file))
        assert config["foreground"] == 7
        assert config["background"] == -1
        assert config["selection_background"] == 6
    
    def test_load_config_invalid_color(self, tmp_path):
        """Test loading config with invalid color name."""
        config_file = tmp_path / "config.ini"
        config_file.write_text("""
[colors]
foreground = invalid_color
""")
        
        config = load_config(str(config_file))
        assert config["foreground"] == -1  # defaults to -1 for invalid


class TestIntegration:
    """Integration tests."""
    
    def test_menu_with_config(self, tmp_path):
        """Test creating menu with config."""
        config_file = tmp_path / "config.ini"
        config_file.write_text("""
[colors]
foreground = cyan
background = black
""")
        
        config = load_config(str(config_file))
        items = ["test1", "test2", "test3"]
        menu = TMenu(items, config=config)
        
        assert menu.config["foreground"] == 6  # cyan
        assert menu.config["background"] == 0  # black
    
    def test_menu_filtering_workflow(self):
        """Test a typical filtering workflow."""
        items = ["firefox", "chromium", "brave", "vim", "emacs", "nano"]
        menu = TMenu(items)
        
        # Start with all items
        assert len(menu.filtered_items) == 6
        
        # Filter for browsers
        menu.query = "f"
        menu.filtered_items = menu.filter_items(menu.query)
        assert "firefox" in menu.filtered_items
        
        # More specific
        menu.query = "fi"
        menu.filtered_items = menu.filter_items(menu.query)
        assert "firefox" in menu.filtered_items
        assert "chromium" not in menu.filtered_items


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
