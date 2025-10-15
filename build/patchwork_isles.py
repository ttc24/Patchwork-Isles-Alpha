#!/usr/bin/env python3
"""
Patchwork Isles - Main Launcher
Version: 1.0.0
"""

import sys
import os
from pathlib import Path

# Add engine directory to Python path
game_dir = Path(__file__).parent
engine_dir = game_dir / "engine"
sys.path.insert(0, str(engine_dir))

def main():
    """Main entry point for Patchwork Isles."""
    try:
        # Import and run the main game
        from engine_min import main as game_main
        world_file = game_dir / "world" / "world.json"
        
        # Pass world file as argument
        sys.argv = ["patchwork_isles", str(world_file)]
        
        game_main()
        
    except ImportError as e:
        print(f"❌ Error importing game engine: {e}")
        print("Please ensure all required files are present.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n👋 Thanks for playing Patchwork Isles!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
