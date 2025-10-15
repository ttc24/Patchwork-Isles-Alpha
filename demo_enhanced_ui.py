#!/usr/bin/env python3
"""
Demo script showing enhanced UI capabilities in Patchwork Isles.
"""

import sys
import time
from pathlib import Path

# Add engine to path
sys.path.insert(0, str(Path(__file__).parent / "engine"))

from ui_enhancements import (
    print_banner, print_character_stats, typewriter_text, 
    show_loading_animation, print_success, print_info,
    create_fancy_box, clear_screen
)
from enhanced_menu import GameMenu, Menu

def demo_game_intro():
    """Demo the game introduction with enhanced UI."""
    clear_screen()
    
    print_banner("PATCHWORK ISLES", "Enhanced UI Demonstration")
    
    print_info("Welcome to the enhanced Patchwork Isles experience!")
    time.sleep(1)
    
    # Demo typewriter effect
    intro_text = """
    The floating archipelago stretches endlessly before you, each island a 
    fragment of possibility. Ancient magic holds these landmasses aloft, 
    while trade winds carry whispers of opportunity between the scattered realms.
    """
    
    print("\\n🌊 Setting the scene...")
    typewriter_text(intro_text.strip(), delay=0.01)
    
    # Demo character stats
    sample_character = {
        "name": "Aria Stormwright",
        "hp": 8,
        "tags": ["Scout", "Diplomat", "Wind-Touched"],
        "traits": ["Fleet-Footed", "Silver Tongue"],
        "inventory": ["Storm Glass", "Sealed Letter", "Travel Rations"]
    }
    
    print_character_stats(sample_character)
    
    input("\\nPress Enter to continue to menu demo...")

def demo_enhanced_menus():
    """Demo the enhanced menu system."""
    def start_new_game():
        show_loading_animation(2.0, "Creating new adventure...")
        print_success("New game started!")
        return "new_game"
    
    def load_game():
        show_loading_animation(1.5, "Loading saved game...")
        print_success("Game loaded!")
        return "load_game"
    
    def show_options():
        create_fancy_box(
            "Game Options:\\n" +
            "• Text Speed: Adjustable from slow to instant\\n" +
            "• UI Scale: Small, Normal, or Large\\n" +
            "• High Contrast: For better readability\\n" +
            "• Rich Terminal: Enhanced colors and formatting",
            "Configuration Options"
        )
        input("\\nPress Enter to return to menu...")
        return "continue"
    
    menu_system = GameMenu()
    main_menu = menu_system.create_main_menu(
        start_new_game,
        load_game, 
        show_options
    )
    
    menu_system.push_menu(main_menu)
    result = menu_system.run_current_menu()
    
    return result

def demo_story_scene():
    """Demo an enhanced story scene."""
    clear_screen()
    
    # Scene header
    print_banner("THE WINDPORT DOCKS", "Chapter 1: Arrival")
    
    # Scene description with typewriter effect
    scene_text = """
    The merchant vessel *Copper Wing* settles into its berth with a groan 
    of stressed timber and canvas. Around you, dock workers rush to secure 
    the mooring lines as the floating city of Windport bobs gently in the 
    ethereal currents.
    """
    
    typewriter_text(scene_text.strip(), delay=0.02)
    
    # Show choices menu
    choices_menu = Menu("What do you do?", "Your first decision in the Patchwork Isles")
    choices_menu.auto_clear = False
    
    choices_menu.add_item(
        "Approach the Harbor Master",
        lambda: "harbor_master",
        "Seek official passage and information about the city",
        "h", True, "🏛️"
    )
    
    choices_menu.add_item(
        "Head to the Merchant Quarter", 
        lambda: "merchant_quarter",
        "Browse the markets and gather rumors from traders",
        "m", True, "🏪"
    )
    
    choices_menu.add_item(
        "Find a tavern",
        lambda: "tavern",
        "Rest and listen for local gossip over a hot meal",
        "t", True, "🍺"
    )
    
    result = choices_menu.run()
    
    if result == "harbor_master":
        print_success("You stride confidently toward the Harbor Master's office...")
    elif result == "merchant_quarter":
        print_success("You follow the crowd toward the bustling merchant stalls...")
    elif result == "tavern":
        print_success("You seek out the warm glow of a nearby tavern...")
    
    return result

def main():
    """Run the enhanced UI demo."""
    try:
        print_info("Starting Patchwork Isles Enhanced UI Demo...")
        time.sleep(1)
        
        # Demo 1: Game intro
        demo_game_intro()
        
        # Demo 2: Enhanced menus
        print_info("\\nDemonstrating enhanced menu system...")
        menu_result = demo_enhanced_menus()
        
        if menu_result in ["new_game", "load_game"]:
            # Demo 3: Story scene
            time.sleep(1)
            choice_result = demo_story_scene()
            
            create_fancy_box(
                f"Demo completed!\\n\\n" +
                f"Menu result: {menu_result}\\n" +
                f"Story choice: {choice_result}\\n\\n" +
                f"The enhanced UI system provides:\\n" +
                f"• Rich terminal formatting with colors and styles\\n" +
                f"• Smooth typewriter text effects\\n" +
                f"• Interactive menus with hotkeys\\n" +
                f"• Progress indicators and animations\\n" +
                f"• Consistent visual theming",
                "🎆 Demo Summary"
            )
        
        print_success("\\nDemo completed successfully!")
        
    except KeyboardInterrupt:
        print_info("\\nDemo interrupted by user.")
    except Exception as e:
        print(f"❌ Error during demo: {e}")

if __name__ == "__main__":
    main()