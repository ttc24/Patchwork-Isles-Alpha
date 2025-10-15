#!/usr/bin/env python3
"""
Content versioning tool for Patchwork Isles.
Manages world content versions and compatibility tracking.
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engine.versioning import ContentVersionManager, version_world_content


def main():
    """Main function to run the versioning tool."""
    world_path = PROJECT_ROOT / "world" / "world.json"
    
    if not world_path.exists():
        print(f"Error: World file not found at {world_path}")
        sys.exit(1)
    
    # Load world data
    try:
        with open(world_path, 'r', encoding='utf-8') as f:
            world_data = json.load(f)
    except Exception as e:
        print(f"Error loading world data: {e}")
        sys.exit(1)
    
    # Create version manager
    manager = ContentVersionManager(world_data)
    
    # Check current version
    current_version = manager.get_current_version()
    
    print("=== Patchwork Isles Content Versioning Tool ===\n")
    
    if current_version:
        print(f"Current version: {current_version}")
        print(f"Content hash: {manager._calculate_content_hash()}")
        print(f"Version history: {len(manager.version_history)} versions")
        
        # Check if content has changed
        if manager.detect_content_changes():
            print("⚠️  Content has changed since last version")
        else:
            print("✅ Content matches current version")
        
        print("\nOptions:")
        print("1. Create new version (patch)")
        print("2. Create new version (minor)")
        print("3. Create new version (major)")
        print("4. Show version history")
        print("5. Show version info")
        print("6. Auto-version if changed")
        print("7. Exit")
    else:
        print("No version information found in world data.")
        print("This appears to be the first time versioning this content.")
        print("\nOptions:")
        print("1. Initialize versioning (create v1.0.0)")
        print("2. Exit")
    
    try:
        choice = input("\nEnter your choice: ").strip()
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        return
    
    if current_version:
        if choice == "1":
            description = input("Enter description for patch version: ").strip()
            new_version = manager.create_new_version("patch", description)
            _save_world_data(world_data, world_path)
            print(f"✅ Created patch version {new_version}")
        
        elif choice == "2":
            description = input("Enter description for minor version: ").strip()
            new_version = manager.create_new_version("minor", description)
            _save_world_data(world_data, world_path)
            print(f"✅ Created minor version {new_version}")
        
        elif choice == "3":
            description = input("Enter description for major version: ").strip()
            new_version = manager.create_new_version("major", description)
            _save_world_data(world_data, world_path)
            print(f"✅ Created major version {new_version}")
        
        elif choice == "4":
            print("\nVersion History:")
            for i, version in enumerate(manager.version_history):
                print(f"  {i+1}. v{version} - {version.timestamp}")
                if version.description:
                    print(f"     {version.description}")
        
        elif choice == "5":
            info = manager.get_version_info()
            print("\nVersion Information:")
            print(f"  Current version: {info['current_version']}")
            print(f"  Total versions: {info['version_count']}")
            print(f"  Content hash: {info['content_hash']}")
            print(f"  Versions file: {info['versions_file']}")
        
        elif choice == "6":
            if manager.detect_content_changes():
                description = input("Enter description for auto-version: ").strip()
                new_version = manager.auto_version_if_changed(description)
                _save_world_data(world_data, world_path)
                print(f"✅ Auto-created version {new_version}")
            else:
                print("No changes detected - no new version created.")
        
        elif choice == "7":
            print("Exiting.")
        
        else:
            print("Invalid choice.")
    
    else:
        if choice == "1":
            description = input("Enter description for initial version [Initial version after node repairs]: ").strip()
            description = description or "Initial version after node repairs"
            
            new_version = manager.create_new_version("major", description)
            _save_world_data(world_data, world_path)
            print(f"✅ Initialized versioning with v{new_version}")
            
            print("\nNext steps:")
            print("1. Version information is now embedded in world.json")
            print("2. Save files will be checked for compatibility")
            print("3. Use this tool to create new versions when content changes")
        
        elif choice == "2":
            print("Exiting without initializing versioning.")
        
        else:
            print("Invalid choice.")


def _save_world_data(world_data, world_path):
    """Save world data back to file."""
    with open(world_path, 'w', encoding='utf-8') as f:
        json.dump(world_data, f, indent=2, ensure_ascii=False)
        f.write('\n')
    print(f"Saved updated world data to {world_path}")


if __name__ == "__main__":
    main()