#!/usr/bin/env python3

import json
import re
from datetime import datetime

def create_missing_nodes():
    """Create all missing nodes that are referenced by choices but don't exist"""
    
    # Load the world data
    with open('world/world.json', 'r', encoding='utf-8') as f:
        world_data = json.load(f)
    
    # Find all referenced node IDs that don't exist
    existing_nodes = set(world_data['nodes'].keys())
    referenced_nodes = set()
    
    # Check starts
    for start in world_data.get('starts', []):
        if 'node' in start:
            referenced_nodes.add(start['node'])
        elif 'node_id' in start:
            referenced_nodes.add(start['node_id'])
    
    print(f"Debug: Found {len(world_data.get('starts', []))} starts")
    print(f"Debug: Existing nodes: {len(existing_nodes)}")
    print(f"Debug: Referenced nodes: {len(referenced_nodes)}")
    
    # Check choice destinations
    for node_data in world_data['nodes'].values():
        for choice in node_data.get('choices', []):
            if 'target' in choice:
                referenced_nodes.add(choice['target'])
            elif 'destination' in choice:
                referenced_nodes.add(choice['destination'])
    
    missing_nodes = referenced_nodes - existing_nodes
    print(f"Found {len(missing_nodes)} missing nodes:")
    for node in sorted(missing_nodes):
        print(f"  - {node}")
    
    if not missing_nodes:
        print("No missing nodes found!")
        return
    
    # Create backup
    backup_filename = f"world_backup_before_missing_nodes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(backup_filename, 'w', encoding='utf-8') as f:
        json.dump(world_data, f, indent=2, ensure_ascii=False)
    print(f"\nBackup created: {backup_filename}")
    
    # Define templates for different node types
    node_templates = {
        # Singing Depths nodes
        "singing_depths_crisis_revealed": {
            "title": "Crisis Revealed",
            "description": "The moss network shares its urgent vision: surface miners have breached a harmonic seal, threatening to shatter the depths' delicate resonance. The crisis demands immediate action to preserve both worlds.",
            "tags": ["Deep-Listener"],
            "choices": [
                {"text": "Volunteer to negotiate with the surface miners.", "target": "singing_depths_surface_mission"},
                {"text": "Study the broken seal to understand the damage.", "target": "singing_depths_wound_source"},
                {"text": "Rally the depths' guardians for defense.", "target": "singing_depths_guardian_council"},
                {"text": "Return to the Startways Nexus with this intelligence.", "target": "startways_nexus"}
            ]
        },
        "singing_depths_disturbance_source": {
            "title": "Source of Disturbance",
            "description": "Following the network's strongest pulses leads you to a cavern where crystalline formations vibrate with distress. Here, the boundary between the depths and surface world grows thin.",
            "tags": ["Deep-Listener"],
            "choices": [
                {"text": "Investigate the thinning boundary.", "destination": "singing_depths_wound_source"},
                {"text": "Try to stabilize the crystal formations.", "destination": "singing_depths_healing_pools"},
                {"text": "Seek guidance from the moss network.", "destination": "singing_depths_moss_revelation"},
                {"text": "Return to the central Startways Nexus.", "destination": "startways_nexus"}
            ]
        },
        "singing_depths_harmony_attempt": {
            "title": "Harmonizing the Network",
            "description": "Your gentle harmonics begin to calm the frantic moss network. The red warning glow softens to amber, then golden yellow. The network's panic subsides, but its message remains urgent.",
            "tags": ["Deep-Listener", "Healer"],
            "choices": [
                {"text": "Request the network's full message now that it's calmed.", "destination": "singing_depths_ancient_language"},
                {"text": "Ask the network to show you the source of danger.", "destination": "singing_depths_disturbance_source"},
                {"text": "Offer to help coordinate a response.", "destination": "singing_depths_guardian_council"},
                {"text": "Return to safer areas to plan.", "destination": "startways_nexus"}
            ]
        },
        "singing_depths_urgent_message": {
            "title": "Urgent Network Message",
            "description": "The moss network pulses with concentrated urgency, transmitting a flood of information about surface disruption and damaged harmonic seals. The message is crystal clear: immediate action is needed.",
            "tags": ["Deep-Listener"],
            "choices": [
                {"text": "Accept the mission to mediate surface conflicts.", "destination": "singing_depths_surface_mission"},
                {"text": "Investigate the damaged seals personally.", "destination": "singing_depths_wound_source"},
                {"text": "Rally the depths' guardians first.", "destination": "singing_depths_guardian_council"},
                {"text": "Return to report to the Startways Nexus.", "destination": "startways_nexus"}
            ]
        },
        "singing_depths_full_truth": {
            "title": "The Complete Truth",
            "description": "The network reveals the complete scope: surface mining operations have unknowingly destabilized the acoustic foundations that keep both worlds stable. Without intervention, both realms face collapse.",
            "tags": ["Deep-Listener", "Scholar"],
            "choices": [
                {"text": "Take on the diplomatic mission to the surface.", "destination": "singing_depths_surface_mission"},
                {"text": "Study the technical aspects of the breach.", "destination": "singing_depths_wound_source"},
                {"text": "Coordinate with depth guardians for solutions.", "destination": "singing_depths_guardian_council"},
                {"text": "Return to the nexus to gather more help.", "destination": "startways_nexus"}
            ]
        },
        "singing_depths_transformation_choice": {
            "title": "The Transformation Offer",
            "description": "The guardian council reveals their ultimate option: they can transform you into a bridge between worlds, giving you the power to heal both surface and depths—but at the cost of your current form and identity.",
            "tags": ["Deep-Listener"],
            "choices": [
                {"text": "Accept the transformation to save both worlds.", "destination": "ending_depths_bridge_keeper"},
                {"text": "Decline and seek alternative solutions.", "destination": "singing_depths_alternative_solutions"},
                {"text": "Ask for time to consider the implications.", "destination": "singing_depths_meditation_grove"},
                {"text": "Return to the surface with their message.", "destination": "startways_nexus"}
            ]
        },
        "singing_depths_neutral_path": {
            "title": "The Middle Way",
            "description": "You choose neither full transformation nor complete rejection, instead forging a new path that preserves your identity while accepting responsibility as a permanent ambassador between the worlds.",
            "tags": ["Deep-Listener", "Diplomat"],
            "choices": [
                {"text": "Establish the first inter-world embassy.", "destination": "singing_depths_embassy_founding"},
                {"text": "Begin regular diplomatic missions.", "destination": "singing_depths_surface_mission"},
                {"text": "Study how to strengthen the barrier safely.", "destination": "singing_depths_research_lab"},
                {"text": "Return to the Startways Nexus as ambassador.", "destination": "startways_nexus"}
            ]
        }
    }
    
    # Add generic nodes for other missing references
    for node_id in missing_nodes:
        if node_id not in node_templates:
            # Create generic node based on ID pattern
            parts = node_id.split('_')
            if len(parts) >= 2:
                area = parts[0] + '_' + parts[1] if len(parts) > 1 else parts[0]
                node_name = ' '.join(word.capitalize() for word in parts[2:]) if len(parts) > 2 else "Unnamed Location"
            else:
                area = "unknown"
                node_name = "Unnamed Location"
            
            node_templates[node_id] = {
                "title": node_name,
                "description": f"You find yourself in {node_name.lower()}, a location within the {area.replace('_', ' ').title()} region. The path forward remains unclear, but you sense this area holds significance.",
                "tags": [],
                "choices": [
                    {"text": "Explore this area further.", "destination": node_id},
                    {"text": "Return to the main pathways.", "destination": "startways_nexus"}
                ]
            }
    
    # Add all missing nodes
    nodes_added = 0
    for node_id in missing_nodes:
        if node_id in node_templates:
            world_data['nodes'][node_id] = node_templates[node_id]
            nodes_added += 1
            print(f"Added node: {node_id}")
        else:
            print(f"Warning: No template for node {node_id}")
    
    # Save the updated world data
    with open('world/world.json', 'w', encoding='utf-8') as f:
        json.dump(world_data, f, indent=2, ensure_ascii=False)
    
    print(f"\nAdded {nodes_added} missing nodes to world.json")
    print("Ready for validation and testing!")

if __name__ == "__main__":
    create_missing_nodes()