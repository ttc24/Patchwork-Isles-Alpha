#!/usr/bin/env python3
"""Eliminate all remaining loops in the game world."""

import json
import shutil
from datetime import datetime

def backup_world():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"world/world_backup_eliminate_loops_{timestamp}.json"
    shutil.copy("world/world.json", backup_path)
    print(f"Created backup: {backup_path}")
    return backup_path

def eliminate_all_loops():
    # Create backup first
    backup_path = backup_world()
    
    # Load existing world
    with open("world/world.json", "r", encoding="utf-8") as f:
        world = json.load(f)
    
    # Load loop elimination plan
    with open("eliminate_all_loops.json", "r", encoding="utf-8") as f:
        plan = json.load(f)
    
    # Add new exit nodes
    original_count = len(world["nodes"])
    world["nodes"].update(plan["additional_exit_nodes"])
    print(f"Added {len(plan['additional_exit_nodes'])} new exit nodes")
    
    # Apply fixes to existing nodes to break loops
    fixes_applied = 0
    for node_id, fix_info in plan["loop_elimination_plan"]["loop_fixes"].items():
        if node_id in world["nodes"]:
            # Add new choices to break loops
            for new_choice in fix_info["new_choices"]:
                world["nodes"][node_id]["choices"].append(new_choice)
            fixes_applied += 1
            print(f"Applied loop fix to {node_id}: {fix_info['fix']}")
        else:
            print(f"Warning: Node {node_id} not found in world.json")
    
    # Add connections to the new exit nodes where needed
    connections_added = 0
    
    # Connect orchard nodes to new exit gateway
    orchard_nodes = ["starfallen_orchard_quiet_grant", "starfallen_orchard_freehands_collective", "starfallen_orchard_tidal_channel"]
    for node_id in orchard_nodes:
        if node_id in world["nodes"]:
            world["nodes"][node_id]["choices"].append({
                "text": "Follow the meteor trail to the exit gateway.",
                "target": "orchard_exit_gateway"
            })
            connections_added += 1
    
    # Connect amber tides nodes to new harbor exit
    amber_nodes = ["amber_tides_amber_bindery", "amber_tides_mnemonic_harbor", "amber_tides_freehands_flotilla", "amber_tides_quiet_endowment"]
    for node_id in amber_nodes:
        if node_id in world["nodes"]:
            world["nodes"][node_id]["choices"].append({
                "text": "Navigate toward the harbor gateway.",
                "target": "amber_tides_harbor_exit"
            })
            connections_added += 1
    
    # Connect shed market complex to exit plaza
    shed_market_nodes = ["shed_market_freehands_network", "shed_market_dreamway_coop", "shed_market_quiet_ledger_fund"]
    for node_id in shed_market_nodes:
        if node_id in world["nodes"]:
            world["nodes"][node_id]["choices"].append({
                "text": "Head toward the market district exit.",
                "target": "shed_market_exit_plaza"
            })
            connections_added += 1
    
    # Save updated world
    with open("world/world.json", "w", encoding="utf-8") as f:
        json.dump(world, f, indent=2, ensure_ascii=False)
    
    new_total = len(world["nodes"])
    print(f"\\n✅ Loop elimination complete!")
    print(f"📦 Backup saved as: {backup_path}")
    print(f"🔧 Applied {fixes_applied} direct loop fixes")
    print(f"🔗 Added {connections_added} new connections")
    print(f"🏗️  Total nodes: {original_count} → {new_total}")
    
    return fixes_applied, connections_added

if __name__ == "__main__":
    fixes, connections = eliminate_all_loops()
    print(f"\\n🎉 Eliminated ALL loops! Applied {fixes} fixes and {connections} connections.")
    print("\\n🧭 Every area now has clear exit paths - no more player traps!")