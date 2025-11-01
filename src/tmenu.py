#!/usr/bin/env python3
"""
tmenu - A dmenu-like command executor for the terminal using ncurses
"""

import argparse
import configparser
import curses
import os
import sys
import time
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import shlex
from x256 import x256
import configparser
import argparse

# Optional pyfiglet support for ASCII art titles
try:
    import pyfiglet
    PYFIGLET_AVAILABLE = True
except ImportError:
    PYFIGLET_AVAILABLE = False


class TMenu:
    """Terminal menu for selecting and executing commands."""

    def __init__(self, items: List[str], config: Optional[dict] = None, 
                 menu_items: Optional[Dict[str, str]] = None,
                 submenus: Optional[Dict[str, Dict[str, str]]] = None,
                 title: str = "",
                 is_submenu: bool = False):
        """
        Initialize TMenu.
        
        Args:
            items: List of items to display
            config: Configuration dictionary with theme settings
            menu_items: Dictionary mapping display labels to commands
            submenus: Dictionary of submenu name to submenu items
            title: Menu title to display
            is_submenu: Whether this is a submenu (shows Back option)
        """
        self.all_items = sorted(items)
        
        # Add Back option for submenus and Exit for all menus
        if is_submenu:
            self.all_items.append("← Back")
        self.all_items.append("Exit")
        
        self.selected_index = 0
        self.scroll_offset = 0
        self.config = config or {}
        self.menu_items = menu_items or {}
        self.submenus = submenus or {}
        self.title = title
        self.centered = self.config.get('centered', True)
        self.is_submenu = is_submenu
        
        # For mouse support
        self.item_positions = []  # List of (y, start_x, end_x, item_index)
        self.last_click_time = 0
        self.last_click_item = None
        self.double_click_delay = 0.2  # 200ms for double-click detection
        
    
    def get_colors(self, stdscr) -> dict:
        """Initialize color pairs based on config."""
        colors = {}
        
        if curses.has_colors():
            curses.use_default_colors()
            
            # Parse colors from config or use defaults
            fg = self.config.get('foreground', 7)  # white
            bg = self.config.get('background', -1)  # terminal default
            sel_fg = self.config.get('selection_foreground', 0)  # black
            sel_bg = self.config.get('selection_background', 6)  # cyan
            prompt_fg = self.config.get('prompt_foreground', 4)  # blue
            
            # Initialize color pairs
            curses.init_pair(1, fg, bg)  # Normal text
            curses.init_pair(2, sel_fg, sel_bg)  # Selected item
            curses.init_pair(3, prompt_fg, bg)  # Prompt
            
            colors['normal'] = curses.color_pair(1)
            colors['selected'] = curses.color_pair(2)
            colors['prompt'] = curses.color_pair(3) | curses.A_BOLD
        else:
            colors['normal'] = curses.A_NORMAL
            colors['selected'] = curses.A_REVERSE
            colors['prompt'] = curses.A_BOLD
        
        return colors
    
    def render_figlet_title(self, title: str) -> List[str]:
        """Render title using pyfiglet if available and enabled."""
        if not PYFIGLET_AVAILABLE or not self.config.get('figlet', False):
            return [title]
        
        try:
            font = self.config.get('figlet_font', 'standard')
            fig = pyfiglet.Figlet(font=font, width=self.config.get('width', 60))
            figlet_text = fig.renderText(title)
            # Split into lines and remove trailing empty lines
            lines = figlet_text.rstrip('\n').split('\n')
            return lines
        except Exception:
            # Fallback to plain title if figlet fails
            return [title]
    
    def draw(self, stdscr, colors: dict):
        """Draw the menu interface."""
        height, width = stdscr.getmaxyx()
        stdscr.clear()
        
        # Calculate menu dimensions and position
        menu_width = min(self.config.get('width', 60), width - 4)
        num_items = min(len(self.all_items), self.config.get('height', 10))
        
        # Calculate title height
        title_height = 0
        if self.title:
            title_lines = self.render_figlet_title(self.title)
            title_height = len(title_lines)
        
        # Menu height for items only (separator + items)
        items_height = num_items + 1  # +1 for separator
        
        if self.centered:
            # Center the items, then place title above
            items_start_y = max(0, (height - items_height) // 2)
            start_y = max(0, items_start_y - title_height)
            start_x = max(0, (width - menu_width) // 2)
        else:
            start_y = 0
            start_x = 0
            menu_width = width - 1
        
        current_y = start_y
        
        # Draw title if present (with optional figlet)
        if self.title:
            title_lines = self.render_figlet_title(self.title)
            for title_line in title_lines:
                if current_y >= height:
                    break
                # Center or left-align title line
                if self.centered:
                    title_x = start_x + max(0, (menu_width - len(title_line)) // 2)
                else:
                    title_x = start_x
                try:
                    display_line = title_line[:menu_width] if len(title_line) > menu_width else title_line
                    stdscr.addstr(current_y, title_x, display_line, colors['prompt'] | curses.A_BOLD)
                except curses.error:
                    pass
                current_y += 1
        
        
        # Draw separator
        sep_y = current_y
        if sep_y < height:
            separator = "─" * menu_width
            try:
                stdscr.addstr(sep_y, start_x, separator, colors['normal'])
            except curses.error:
                pass
        
        # Calculate visible lines
        visible_lines = min(len(self.all_items), height - sep_y - 1)
        if visible_lines <= 0:
            stdscr.refresh()
            return
        
        # Adjust scroll offset to keep selected item visible
        if self.selected_index < self.scroll_offset:
            self.scroll_offset = self.selected_index
        elif self.selected_index >= self.scroll_offset + visible_lines:
            self.scroll_offset = self.selected_index - visible_lines + 1
        
        # Clear item positions for mouse support
        self.item_positions = []
        
        # Draw visible items
        for i in range(visible_lines):
            item_index = i + self.scroll_offset
            if item_index >= len(self.all_items):
                break
            
            item = self.all_items[item_index]
            y = sep_y + 1 + i
            
            # Truncate item if too long
            display_item = item[:menu_width-2] if len(item) > menu_width-2 else item
            
            # Center items if centered mode
            if self.centered:
                item_x = start_x + (menu_width - len(display_item)) // 2
            else:
                item_x = start_x
            
            # Store position for mouse support
            if self.centered:
                self.item_positions.append((y, start_x, start_x + menu_width, item_index))
            else:
                self.item_positions.append((y, item_x, item_x + len(display_item), item_index))
            
            # Highlight selected item
            if item_index == self.selected_index:
                attr = colors['selected']
                if self.centered:
                    # Pad for centered display
                    display_item = display_item.center(menu_width)
                else:
                    display_item = display_item.ljust(menu_width)
                item_x = start_x
            else:
                attr = colors['normal']
            
            try:
                stdscr.addstr(y, item_x, display_item[:menu_width], attr)
            except curses.error:
                pass
        
        # Draw scrollbar indicator if needed
        if len(self.all_items) > visible_lines:
            try:
                scroll_info = f" [{self.selected_index + 1}/{len(self.all_items)}]"
                stdscr.addstr(sep_y, start_x + menu_width - len(scroll_info), scroll_info, colors['normal'])
            except curses.error:
                pass
        
        stdscr.refresh()
    
    def run(self, stdscr) -> Optional[str]:
        """
        Run the menu and return selected item.
        
        Args:
            stdscr: Curses window object
            
        Returns:
            Selected item or None if cancelled
        """
        curses.curs_set(0)  # Hide cursor
        stdscr.keypad(True)
        
        # Enable mouse support with explicit double-click
        mouse_mask = (
            curses.BUTTON1_CLICKED | 
            curses.BUTTON1_DOUBLE_CLICKED | 
            curses.BUTTON1_TRIPLE_CLICKED
        )
        curses.mousemask(mouse_mask)
        
        colors = self.get_colors(stdscr)
        
        while True:
            self.draw(stdscr, colors)
            
            try:
                key = stdscr.getch()
            except KeyboardInterrupt:
                return None
            
            # Handle input
            if key == ord('\n'):  # Enter
                if self.all_items and self.selected_index < len(self.all_items):
                    selected = self.all_items[self.selected_index]
                    
                    # Handle special menu items
                    if selected == "← Back":
                        return "__GO_BACK__"
                    elif selected == "Exit":
                        return None
                    
                    command = self.menu_items.get(selected, selected)
                    
                    # Check if this is a submenu
                    if command.startswith('submenu:'):
                        submenu_name = command[8:]  # Remove 'submenu:' prefix
                        if submenu_name in self.submenus:
                            # Return signal to enter submenu
                            return f"__SUBMENU__{submenu_name}__{selected}"
                    else:
                        # Execute command
                        return command
                return None
            
            elif key == 27:  # Escape
                if self.is_submenu:
                    return "__GO_BACK__"
                return None
            
            # Mouse support with double-click detection
            elif key == curses.KEY_MOUSE:
                try:
                    _, mx, my, _, bstate = curses.getmouse()
                    
                    # Check for native double-click first
                    is_native_double = bstate & curses.BUTTON1_DOUBLE_CLICKED
                    
                    # Also handle single clicks for manual double-click detection
                    if bstate & curses.BUTTON1_CLICKED or is_native_double:
                        current_time = time.time()
                        # Check if click is on a menu item
                        for y, start_x, end_x, item_idx in self.item_positions:
                            if my == y and start_x <= mx < end_x:
                                # Check for double-click (native or manual)
                                is_manual_double = (
                                    self.last_click_item == item_idx and
                                    (current_time - self.last_click_time) < self.double_click_delay
                                )
                                
                                if is_native_double or is_manual_double:
                                    # Double-click - execute item
                                    selected = self.all_items[item_idx]
                                    if selected == "← Back":
                                        return "__GO_BACK__"
                                    elif selected == "Exit":
                                        return None
                                    command = self.menu_items.get(selected, selected)
                                    if command.startswith('submenu:'):
                                        submenu_name = command[8:]
                                        if submenu_name in self.submenus:
                                            return f"__SUBMENU__{submenu_name}__{selected}"
                                    else:
                                        return command
                                else:
                                    # Single click - move selection and update click tracking
                                    self.selected_index = item_idx
                                    self.last_click_item = item_idx
                                    self.last_click_time = current_time
                                break
                except Exception as e:
                    pass
            
            # Vim keys: j/k for up/down
            elif key == ord('k'):  # Vim up
                if self.selected_index > 0:
                    self.selected_index -= 1
            
            elif key == ord('j'):  # Vim down
                if self.selected_index < len(self.all_items) - 1:
                    self.selected_index += 1
            
            # Vim keys: h/l or g/G for home/end
            elif key == ord('h') or key == ord('g'):  # Vim home/top
                self.selected_index = 0
            
            elif key == ord('l') or key == ord('G'):  # Vim end/bottom
                self.selected_index = max(0, len(self.all_items) - 1)
            
            # WASD keys: w/s for up/down
            elif key == ord('w'):  # WASD up
                if self.selected_index > 0:
                    self.selected_index -= 1
            
            elif key == ord('s'):  # WASD down
                if self.selected_index < len(self.all_items) - 1:
                    self.selected_index += 1
            
            # WASD keys: a/d for page up/down or home/end
            elif key == ord('a'):  # WASD left/home
                self.selected_index = 0
            
            elif key == ord('d'):  # WASD right/end
                self.selected_index = max(0, len(self.all_items) - 1)
            
            # Number keys 1-9 to execute items directly
            elif ord('1') <= key <= ord('9'):
                item_num = key - ord('1')  # 0-indexed
                if item_num < len(self.all_items):
                    # Execute the item directly
                    selected = self.all_items[item_num]
                    if selected == "← Back":
                        return "__GO_BACK__"
                    elif selected == "Exit":
                        return None
                    command = self.menu_items.get(selected, selected)
                    if command.startswith('submenu:'):
                        submenu_name = command[8:]
                        if submenu_name in self.submenus:
                            return f"__SUBMENU__{submenu_name}__{selected}"
                    else:
                        return command
            
            # Arrow keys and original shortcuts
            elif key == curses.KEY_UP or key == 16:  # Up or Ctrl+P
                if self.selected_index > 0:
                    self.selected_index -= 1
            
            elif key == curses.KEY_DOWN or key == 14:  # Down or Ctrl+N
                if self.selected_index < len(self.all_items) - 1:
                    self.selected_index += 1
            
            elif key == curses.KEY_PPAGE:  # Page Up
                self.selected_index = max(0, self.selected_index - 10)
            
            elif key == curses.KEY_NPAGE:  # Page Down
                self.selected_index = min(len(self.all_items) - 1, self.selected_index + 10)
            
            elif key == curses.KEY_HOME or key == 1:  # Home or Ctrl+A
                self.selected_index = 0
            
            elif key == curses.KEY_END or key == 5:  # End or Ctrl+E
                self.selected_index = max(0, len(self.all_items) - 1)




def load_theme(theme_name: str) -> Optional[configparser.ConfigParser]:
    """Load a theme from various locations.
    
    Searches in order:
    1. ~/.config/tmenu/themes/{theme_name}.ini
    2. ./themes/{theme_name}.ini (bundled themes)
    
    Returns:
        ConfigParser object if theme found, None otherwise
    """
    # Get the parent directory for bundled themes
    script_dir = os.path.dirname(os.path.abspath(__file__))
    parent_dir = os.path.dirname(script_dir)
    
    theme_locations = [
        os.path.expanduser(f'~/.config/tmenu/themes/{theme_name}.ini'),  # User themes
        os.path.join(parent_dir, 'themes', f'{theme_name}.ini'),  # Bundled themes
    ]
    
    for theme_path in theme_locations:
        if os.path.exists(theme_path):
            parser = configparser.ConfigParser()
            try:
                parser.read(theme_path)
                return parser
            except Exception:
                continue
    
    return None


def create_default_config():
    """Create default config file in ~/.config/tmenu/ if it doesn't exist."""
    config_dir = os.path.expanduser('~/.config/tmenu')
    config_file = os.path.join(config_dir, 'config.ini')
    
    # Don't create if it already exists
    if os.path.exists(config_file):
        return
    
    # Create directory if needed
    os.makedirs(config_dir, exist_ok=True)
    
    # Get path to default config file (in same directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_config_path = os.path.join(script_dir, 'config.default.ini')
    
    try:
        # Read default config from file
        with open(default_config_path, 'r') as f:
            default_config = f.read()
        
        # Write to user config
        with open(config_file, 'w') as f:
            f.write(default_config)
    except Exception:
        pass  # Silently fail if we can't create config


def load_custom_menus(themes_dir: Optional[str] = None) -> Tuple[Dict[str, str], Dict[str, Dict[str, str]]]:
    """Load custom menu configurations from specified directory.
    
    Args:
        themes_dir: Path to themes directory. If None, no custom menus are loaded.
    
    Returns:
        Tuple of (menu_items dict, submenus dict)
    """
    menu_items = {}
    submenus = {}
    
    # Return empty if no directory specified
    if themes_dir is None:
        return menu_items, submenus
    
    # Expand user path
    themes_dir = os.path.expanduser(themes_dir)
    
    # Return empty if directory doesn't exist
    if not os.path.exists(themes_dir) or not os.path.isdir(themes_dir):
        return menu_items, submenus
    
    # Load all .ini files from themes directory
    try:
        for filename in sorted(os.listdir(themes_dir)):
            if filename.endswith('.ini'):
                menu_path = os.path.join(themes_dir, filename)
                parser = configparser.ConfigParser()
                try:
                    parser.read(menu_path)
                    
                    # Load menu items
                    if 'menu' in parser:
                        for label, command in parser['menu'].items():
                            menu_items[label] = command
                    
                    # Load submenus
                    for section in parser.sections():
                        if section.startswith('submenu.'):
                            submenu_name = section[8:]  # Remove 'submenu.' prefix
                            if submenu_name not in submenus:
                                submenus[submenu_name] = {}
                            submenus[submenu_name].update(dict(parser[section]))
                except Exception:
                    continue  # Skip invalid files
    except Exception:
        pass  # Silently fail if directory can't be read
    
    return menu_items, submenus


def load_config(config_path: Optional[str] = None) -> Tuple[dict, Dict[str, str], Dict[str, Dict[str, str]], str]:
    """Load configuration from file.
    
    Returns:
        Tuple of (config dict, menu_items dict, submenus dict, title string)
    """
    # Create default config if none exists
    if config_path is None:
        create_default_config()
    
    if config_path is None:
        # Try default locations
        config_locations = [
            os.path.expanduser('~/.config/tmenu/config.ini'),
            os.path.expanduser('~/.tmenu.ini'),
            'config.ini',
        ]
        for loc in config_locations:
            if os.path.exists(loc):
                config_path = loc
                break
    
    config = {}
    menu_items = {}
    submenus = {}
    title = ""
    
    parser = configparser.ConfigParser()
    
    # First, check if config specifies a theme
    theme_parser = None
    if config_path and os.path.exists(config_path):
        parser.read(config_path)
        if 'display' in parser and 'theme' in parser['display']:
            theme_name = parser['display']['theme']
            theme_parser = load_theme(theme_name)
    
    # Load theme colors first (can be overridden by config)
    if theme_parser and 'colors' in theme_parser:
        for key, value in theme_parser['colors'].items():
            value = value.strip()
            # Check if it's a hex color
            if value.startswith('#') or (len(value) == 6 and all(c in '0123456789abcdefABCDEF' for c in value)):
                # Use x256 library to convert hex to xterm-256
                hex_color = value.lstrip('#').lower()
                config[key] = x256.from_hex(hex_color)
            else:
                # Numeric value or special (-1 for transparent)
                try:
                    config[key] = int(value)
                except ValueError:
                    config[key] = -1
    
    # Now load config (overrides theme)
    if config_path and os.path.exists(config_path):
        if 'colors' in parser:
            color_map = {
                'black': 0, 'red': 1, 'green': 2, 'yellow': 3,
                'blue': 4, 'magenta': 5, 'cyan': 6, 'white': 7,
            }
            
            for key, value in parser['colors'].items():
                try:
                    config[key] = int(value)
                except ValueError:
                    config[key] = color_map.get(value.lower(), -1)
        
        if 'display' in parser:
            if 'centered' in parser['display']:
                config['centered'] = parser['display'].getboolean('centered')
            if 'width' in parser['display']:
                config['width'] = int(parser['display']['width'])
            if 'height' in parser['display']:
                config['height'] = int(parser['display']['height'])
            if 'title' in parser['display']:
                title = parser['display']['title']
            if 'figlet' in parser['display']:
                config['figlet'] = parser['display'].getboolean('figlet')
            if 'figlet_font' in parser['display']:
                config['figlet_font'] = parser['display']['figlet_font']
            if 'themes_dir' in parser['display']:
                config['themes_dir'] = parser['display']['themes_dir']
        
        if 'menu' in parser:
            for label, command in parser['menu'].items():
                menu_items[label] = command
        
        # Load submenus (sections like [submenu.Development])
        for section in parser.sections():
            if section.startswith('submenu.'):
                submenu_name = section[8:]  # Remove 'submenu.' prefix
                submenus[submenu_name] = dict(parser[section])
    
    # Load and merge custom menus if themes_dir is configured
    themes_dir = config.get('themes_dir')
    custom_menu_items, custom_submenus = load_custom_menus(themes_dir)
    menu_items.update(custom_menu_items)
    for submenu_name, submenu_items in custom_submenus.items():
        if submenu_name in submenus:
            submenus[submenu_name].update(submenu_items)
        else:
            submenus[submenu_name] = submenu_items
    
    return config, menu_items, submenus, title


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='tmenu - A configurable terminal menu'
    )
    parser.add_argument(
        '-c', '--config',
        help='Path to configuration file'
    )
    
    args = parser.parse_args()
    
    # Load configuration
    config, menu_items, submenus, title = load_config(args.config)
    
    # Check if we have menu items
    if not menu_items:
        print("Error: No menu items found in configuration.", file=sys.stderr)
        print("Please create a config file at ~/.config/tmenu/config.ini", file=sys.stderr)
        print("with a [menu] section defining your menu items.", file=sys.stderr)
        sys.exit(1)
    
    # Main menu loop with stack for submenu navigation
    menu_stack = []
    current_items = list(menu_items.keys())
    current_menu_items = menu_items
    current_title = title
    
    while True:
        # Determine if we're in a submenu
        is_submenu = len(menu_stack) > 0
        
        # Run menu
        menu = TMenu(current_items, config=config, menu_items=current_menu_items, 
                    submenus=submenus, title=current_title, is_submenu=is_submenu)
        
        try:
            selection = curses.wrapper(menu.run)
        except KeyboardInterrupt:
            sys.exit(130)
        
        if selection == "__GO_BACK__":
            # Go back to previous menu
            if menu_stack:
                menu_stack.pop()
                if menu_stack:
                    # Return to submenu
                    submenu_name = menu_stack[-1]
                    current_items = list(submenus[submenu_name].keys())
                    current_menu_items = submenus[submenu_name]
                    current_title = title
                else:
                    # Return to main menu
                    current_items = list(menu_items.keys())
                    current_menu_items = menu_items
                    current_title = title
            continue
        elif selection and selection.startswith("__SUBMENU__"):
            # Enter submenu
            parts = selection.split("__")
            submenu_name = parts[2]
            menu_stack.append(submenu_name)
            current_items = list(submenus[submenu_name].keys())
            current_menu_items = submenus[submenu_name]
            current_title = title
            continue
        elif selection:
            # Execute the command
            try:
                cmd_parts = shlex.split(selection)
                os.execvp(cmd_parts[0], cmd_parts)
            except FileNotFoundError:
                print(f"tmenu: command not found: {selection}", file=sys.stderr)
                sys.exit(127)
            except PermissionError:
                print(f"tmenu: permission denied: {selection}", file=sys.stderr)
                sys.exit(126)
            except Exception as e:
                print(f"tmenu: error executing command: {e}", file=sys.stderr)
                sys.exit(1)
        else:
            # Exit selected or escaped from main menu
            sys.exit(0)


if __name__ == '__main__':
    main()
