#!/usr/bin/env python3
"""Merge missing nodes into world.json"""

import json
import shutil
from datetime import datetime

def backup_world():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"world/world_backup_{timestamp}.json"
    shutil.copy("world/world.json", backup_path)
    print(f"Created backup: {backup_path}")
    return backup_path

def merge_nodes():
    # Create backup first
    backup_path = backup_world()
    
    # Load existing world
    with open("world/world.json", "r", encoding="utf-8") as f:
        world = json.load(f)
    
    # Load missing nodes
    with open("missing_nodes.json", "r", encoding="utf-8") as f:
        missing_nodes = json.load(f)
    
    # Merge nodes
    original_count = len(world["nodes"])
    world["nodes"].update(missing_nodes)
    new_count = len(world["nodes"])
    
    print(f"Original nodes: {original_count}")
    print(f"Adding nodes: {len(missing_nodes)}")
    print(f"New total: {new_count}")
    
    # Save updated world
    with open("world/world.json", "w", encoding="utf-8") as f:
        json.dump(world, f, indent=2, ensure_ascii=False)
    
    print("✅ Successfully merged nodes into world.json")
    print(f"📦 Backup saved as: {backup_path}")
    
    return new_count - original_count

if __name__ == "__main__":
    added_count = merge_nodes()
    print(f"\n🎉 Added {added_count} new nodes to the game world!")