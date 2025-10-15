#!/usr/bin/env python3
"""Apply loop fixes to world.json"""

import json
import shutil
from datetime import datetime

def backup_world():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"world/world_backup_loop_fixes_{timestamp}.json"
    shutil.copy("world/world.json", backup_path)
    print(f"Created backup: {backup_path}")
    return backup_path

def apply_loop_fixes():
    # Create backup first
    backup_path = backup_world()
    
    # Load existing world
    with open("world/world.json", "r", encoding="utf-8") as f:
        world = json.load(f)
    
    # Load loop fixes
    with open("loop_fixes.json", "r", encoding="utf-8") as f:
        fixes = json.load(f)
    
    # Add new nodes
    original_count = len(world["nodes"])
    world["nodes"].update(fixes["new_nodes"])
    print(f"Added {len(fixes['new_nodes'])} new nodes to break loops")
    
    # Apply fixes to existing nodes
    fixes_applied = 0
    for node_id, fix_info in fixes["loop_fixes"].items():
        if node_id in world["nodes"]:
            # Add new choices to break loops
            for new_choice in fix_info["new_choices"]:
                world["nodes"][node_id]["choices"].append(new_choice)
            fixes_applied += 1
            print(f"Applied fix to {node_id}: {fix_info['issue']}")
        else:
            print(f"Warning: Node {node_id} not found in world.json")
    
    # Save updated world
    with open("world/world.json", "w", encoding="utf-8") as f:
        json.dump(world, f, indent=2, ensure_ascii=False)
    
    print(f"\n✅ Successfully applied {fixes_applied} loop fixes")
    print(f"📦 Backup saved as: {backup_path}")
    print(f"🎯 Total nodes: {len(world['nodes'])}")
    
    return fixes_applied

if __name__ == "__main__":
    fixes_applied = apply_loop_fixes()
    print(f"\n🎉 Fixed {fixes_applied} problematic loops!")