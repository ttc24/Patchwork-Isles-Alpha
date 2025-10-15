#!/usr/bin/env python3

import json

def fix_choice_fields():
    """Fix choice fields that use 'destination' instead of 'target'"""
    
    # Load the world data
    with open('world/world.json', 'r', encoding='utf-8') as f:
        world_data = json.load(f)
    
    fixes = 0
    for node_data in world_data['nodes'].values():
        for choice in node_data.get('choices', []):
            if 'destination' in choice:
                choice['target'] = choice.pop('destination')
                fixes += 1
    
    # Save the updated world data
    with open('world/world.json', 'w', encoding='utf-8') as f:
        json.dump(world_data, f, indent=2, ensure_ascii=False)
    
    print(f"Fixed {fixes} choices to use 'target' instead of 'destination'")

if __name__ == "__main__":
    fix_choice_fields()