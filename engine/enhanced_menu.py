#!/usr/bin/env python3
"""
Enhanced menu system for Patchwork Isles.
Provides improved navigation, visual feedback, and user experience.
"""

import sys
import time
from typing import List, Dict, Callable, Optional, Any
from pathlib import Path

try:
    from ui_enhancements import (
        print_banner, print_choice_menu, print_section_header,
        get_input_with_prompt, print_warning, print_success, 
        print_error, print_info, clear_screen, typewriter_text,
        show_loading_animation, create_fancy_box
    )
    UI_ENHANCEMENTS_AVAILABLE = True
except ImportError:
    UI_ENHANCEMENTS_AVAILABLE = False


class MenuItem:
    """Represents a menu item with action and metadata."""
    
    def __init__(self, title: str, action: Callable, description: str = "", 
                 hotkey: str = "", enabled: bool = True, icon: str = ""):
        self.title = title
        self.action = action
        self.description = description
        self.hotkey = hotkey.lower()
        self.enabled = enabled
        self.icon = icon
    
    def __str__(self):
        icon_part = f"{self.icon} " if self.icon else ""
        hotkey_part = f"[{self.hotkey.upper()}] " if self.hotkey else ""
        return f"{icon_part}{hotkey_part}{self.title}"


class Menu:
    """Enhanced menu system with navigation and styling."""
    
    def __init__(self, title: str, subtitle: str = ""):
        self.title = title
        self.subtitle = subtitle
        self.items: List[MenuItem] = []
        self.selected_index = 0
        self.show_descriptions = True
        self.auto_clear = True
    
    def add_item(self, title: str, action: Callable, description: str = "", 
                 hotkey: str = "", enabled: bool = True, icon: str = "") -> 'Menu':
        """Add a menu item. Returns self for chaining."""
        item = MenuItem(title, action, description, hotkey, enabled, icon)
        self.items.append(item)
        return self
    
    def add_separator(self, title: str = "─" * 40) -> 'Menu':
        """Add a visual separator."""
        self.add_item(title, lambda: None, enabled=False)
        return self
    
    def add_back_option(self, action: Callable = None) -> 'Menu':
        """Add a back/return option."""
        if action is None:
            action = lambda: "back"
        self.add_item("◀ Back", action, "Return to previous menu", "b", True, "🔙")
        return self
    
    def add_quit_option(self, action: Callable = None) -> 'Menu':
        """Add a quit option."""
        if action is None:
            action = lambda: sys.exit(0)
        self.add_item("Quit", action, "Exit the game", "q", True, "🚪")
        return self
    
    def display(self):
        """Display the menu."""
        if self.auto_clear:
            if UI_ENHANCEMENTS_AVAILABLE:
                clear_screen()
        
        if UI_ENHANCEMENTS_AVAILABLE:
            print_banner(self.title, self.subtitle)
        else:
            print(f"\\n{'=' * 60}")
            print(f"{self.title.center(60)}")
            if self.subtitle:
                print(f"{self.subtitle.center(60)}")
            print('=' * 60)
        
        # Build menu choices for display
        display_items = []
        for i, item in enumerate(self.items):
            if not item.enabled and item.title.startswith(('─', '━', '═')):
                # Skip separators for choice display
                continue
            display_items.append(str(item))
        
        if UI_ENHANCEMENTS_AVAILABLE:
            print_choice_menu(display_items, "Choose an option:", self.selected_index + 1)
        else:
            print("\\nChoose an option:")
            for i, item_text in enumerate(display_items, 1):
                marker = "▶" if i == self.selected_index + 1 else " "
                print(f"{marker} {i}. {item_text}")
        
        # Show description for selected item
        if self.show_descriptions and self.selected_index < len(self.items):
            selected_item = self.items[self.selected_index]
            if selected_item.description and selected_item.enabled:
                if UI_ENHANCEMENTS_AVAILABLE:
                    create_fancy_box(selected_item.description, "Description")
                else:
                    print(f"\\n📝 {selected_item.description}")
    
    def get_input(self) -> str:
        """Get user input for menu navigation."""
        if UI_ENHANCEMENTS_AVAILABLE:
            return get_input_with_prompt("Select option (number or hotkey)")
        else:
            return input("\\nSelect option (number or hotkey): ").strip()
    
    def handle_input(self, choice: str) -> Any:
        """Handle user input and execute appropriate action."""
        choice = choice.lower().strip()
        
        # Handle hotkeys
        for item in self.items:
            if item.hotkey and choice == item.hotkey and item.enabled:
                return item.action()
        
        # Handle numeric selection
        if choice.isdigit():
            index = int(choice) - 1
            enabled_items = [item for item in self.items if item.enabled]
            
            if 0 <= index < len(enabled_items):
                return enabled_items[index].action()
        
        # Handle navigation keys
        if choice in ['up', 'u', 'w']:
            self.move_selection(-1)
            return "continue"
        elif choice in ['down', 'd', 's']:
            self.move_selection(1)
            return "continue"
        elif choice in ['enter', '']:
            if self.selected_index < len(self.items):
                selected_item = self.items[self.selected_index]
                if selected_item.enabled:
                    return selected_item.action()
        
        if UI_ENHANCEMENTS_AVAILABLE:
            print_warning("Invalid selection. Please try again.")
        else:
            print("⚠️  Invalid selection. Please try again.")
        
        return "continue"
    
    def move_selection(self, direction: int):
        """Move the selection cursor."""
        enabled_indices = [i for i, item in enumerate(self.items) if item.enabled]
        
        if not enabled_indices:
            return
        
        current_pos = enabled_indices.index(self.selected_index) if self.selected_index in enabled_indices else 0
        new_pos = (current_pos + direction) % len(enabled_indices)
        self.selected_index = enabled_indices[new_pos]
    
    def run(self) -> Any:
        """Run the menu loop."""
        while True:
            self.display()
            choice = self.get_input()
            result = self.handle_input(choice)
            
            if result != "continue":
                return result
            
            time.sleep(0.1)  # Brief pause for better UX


class GameMenu:
    """Main game menu system."""
    
    def __init__(self):
        self.current_menu = None
        self.menu_stack = []
    
    def create_main_menu(self, start_game_action: Callable, 
                        load_game_action: Callable,
                        options_action: Callable) -> Menu:
        """Create the main game menu."""
        menu = Menu("PATCHWORK ISLES", "A tag/trait-driven interactive fiction")
        
        menu.add_item("New Game", start_game_action, 
                     "Start a new adventure in the Patchwork Isles", "n", True, "🎮")
        menu.add_item("Continue", load_game_action,
                     "Load your saved progress", "c", True, "💾")
        menu.add_item("Options", options_action,
                     "Configure game settings", "o", True, "⚙️")
        menu.add_separator()
        menu.add_quit_option()
        
        return menu
    
    def create_character_creation_menu(self, starts_data: List[Dict]) -> Menu:
        """Create character creation/start selection menu."""
        menu = Menu("CHARACTER CREATION", "Choose your starting scenario")
        
        for start in starts_data:
            if not start.get("locked", False):
                title = start.get("title", "Unknown Start")
                description = start.get("blurb", "No description available.")
                
                # Create action that returns the start ID
                action = lambda start_id=start.get("id"): start_id
                
                menu.add_item(title, action, description, icon="🎭")
        
        menu.add_separator()
        menu.add_back_option()
        
        return menu
    
    def create_pause_menu(self, save_action: Callable, load_action: Callable,
                         options_action: Callable, resume_action: Callable,
                         quit_action: Callable) -> Menu:
        """Create in-game pause menu."""
        menu = Menu("GAME PAUSED", "What would you like to do?")
        menu.auto_clear = False  # Don't clear screen during gameplay
        
        menu.add_item("Resume Game", resume_action,
                     "Continue your adventure", "r", True, "▶️")
        menu.add_separator()
        menu.add_item("Save Game", save_action,
                     "Save your current progress", "s", True, "💾")
        menu.add_item("Load Game", load_action,
                     "Load a saved game", "l", True, "📁")
        menu.add_item("Options", options_action,
                     "Change game settings", "o", True, "⚙️")
        menu.add_separator()
        menu.add_item("Quit to Menu", quit_action,
                     "Return to main menu (progress will be lost)", "q", True, "🏠")
        
        return menu
    
    def create_settings_menu(self, settings_data: Dict[str, Any]) -> Menu:
        """Create settings/options menu."""
        menu = Menu("GAME OPTIONS", "Customize your experience")
        
        # Text speed setting
        speed_options = ["Slow", "Normal", "Fast", "Instant"]
        current_speed = settings_data.get("text_speed", "Normal")
        menu.add_item(f"Text Speed: {current_speed}", 
                     lambda: self.cycle_setting("text_speed", speed_options),
                     "Change how quickly text appears", icon="📝")
        
        # UI Scale setting
        scale_options = ["Small", "Normal", "Large"]
        current_scale = settings_data.get("ui_scale", "Normal")
        menu.add_item(f"UI Scale: {current_scale}",
                     lambda: self.cycle_setting("ui_scale", scale_options),
                     "Adjust the size of text and UI elements", icon="🔍")
        
        # High contrast mode
        contrast = "On" if settings_data.get("high_contrast", False) else "Off"
        menu.add_item(f"High Contrast: {contrast}",
                     lambda: self.toggle_setting("high_contrast"),
                     "Toggle high contrast mode for better readability", icon="🌗")
        
        menu.add_separator()
        menu.add_back_option()
        
        return menu
    
    def cycle_setting(self, setting_name: str, options: List[str]):
        """Cycle through setting options."""
        # This would interface with the actual settings system
        if UI_ENHANCEMENTS_AVAILABLE:
            print_info(f"Setting {setting_name} cycled through options")
        return "continue"
    
    def toggle_setting(self, setting_name: str):
        """Toggle a boolean setting."""
        if UI_ENHANCEMENTS_AVAILABLE:
            print_info(f"Setting {setting_name} toggled")
        return "continue"
    
    def push_menu(self, menu: Menu):
        """Push current menu to stack and set new current menu."""
        if self.current_menu:
            self.menu_stack.append(self.current_menu)
        self.current_menu = menu
    
    def pop_menu(self) -> Optional[Menu]:
        """Pop menu from stack and return to previous menu."""
        if self.menu_stack:
            self.current_menu = self.menu_stack.pop()
            return self.current_menu
        return None
    
    def run_current_menu(self) -> Any:
        """Run the current menu."""
        if self.current_menu:
            return self.current_menu.run()
        return None


def demo_menu():
    """Demo the enhanced menu system."""
    def placeholder_action(name="action"):
        if UI_ENHANCEMENTS_AVAILABLE:
            show_loading_animation(1.0, f"Executing {name}...")
            print_success(f"{name} completed!")
        else:
            print(f"Executing {name}...")
        time.sleep(1)
        return "demo_complete"
    
    menu_system = GameMenu()
    
    # Create main menu
    main_menu = menu_system.create_main_menu(
        lambda: placeholder_action("New Game"),
        lambda: placeholder_action("Load Game"),
        lambda: placeholder_action("Options")
    )
    
    menu_system.push_menu(main_menu)
    result = menu_system.run_current_menu()
    
    if UI_ENHANCEMENTS_AVAILABLE:
        print_info(f"Menu demo completed with result: {result}")
    else:
        print(f"Menu demo completed with result: {result}")


if __name__ == "__main__":
    demo_menu()