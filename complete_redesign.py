#!/usr/bin/env python3

import json
from datetime import datetime

def complete_redesign():
    """Fix remaining navigation issues and complete the crisis-focused redesign"""
    
    # Load current world data
    with open('world/world.json', 'r', encoding='utf-8') as f:
        world_data = json.load(f)
    
    print(f"Completing redesign for {len(world_data['nodes'])} nodes")
    
    # Fix the root orrery resonance node to lead to new content instead of broken paths
    if 'root_orrery_resonance' in world_data['nodes']:
        world_data['nodes']['root_orrery_resonance'] = {
            "title": "The Resonance Emergency",
            "description": "As you touch the bronze conduits, alarms begin sounding throughout the orrery. The Root-Speaker voice becomes urgent: 'The seasonal corrections are failing because the entire network is under attack! Critical systems across the archipelago are being disrupted simultaneously. You must get to the Startways Nexus immediately—this is bigger than just the orrery!'",
            "tags": ["Root-Speaker"],
            "choices": [
                {
                    "text": "🚨 'Get me to the Startways Nexus immediately!'",
                    "target": "startways_nexus"
                },
                {
                    "text": "🔧 'What kind of attacks? Can we fix the orrery first?'",
                    "target": "root_orrery_concourse",
                    "details": "The Root-Speaker explains this is part of coordinated infrastructure failures across multiple systems."
                },
                {
                    "text": "📊 'I need to understand the scope of this crisis.'",
                    "target": "startways_nexus",
                    "details": "Head directly to central command to see all crisis reports."
                }
            ]
        }
        print("Fixed root_orrery_resonance to lead to crisis hub")
    
    # Remove any other broken references to deleted nodes
    nodes_to_check = ['root_orrery_mastery_training', 'root_orrery_apocalypse_vision', 'root_orrery_deep_teaching']
    
    # Fix any choices that reference these broken nodes
    fixes_made = 0
    for node_id, node_data in world_data['nodes'].items():
        if 'choices' in node_data:
            for choice in node_data['choices']:
                if choice.get('target') in nodes_to_check:
                    # Redirect to the crisis hub
                    choice['target'] = 'startways_nexus'  
                    choice['text'] = f"🚨 'Something's wrong - I need to get to the command center!'"
                    fixes_made += 1
                    print(f"Fixed broken choice in {node_id}")
    
    # Also update some existing nodes to acknowledge the crisis and direct players to the hub
    crisis_aware_nodes = {
        'sky_docks': {
            "add_choice": {
                "text": "🚨 [URGENT] Report to Startways Central Command about the crisis",
                "target": "startways_nexus",
                "details": "Emergency sirens are sounding - something major is happening across the archipelago."
            }
        },
        'root_tangle_market': {
            "add_choice": {
                "text": "🚨 [CRISIS RESPONSE] Head to Startways Nexus for emergency briefing", 
                "target": "startways_nexus",
                "details": "Assembly officials are redirecting everyone to central crisis management."
            }
        }
    }
    
    # Add crisis awareness choices to key nodes
    for node_id, update_info in crisis_aware_nodes.items():
        if node_id in world_data['nodes']:
            world_data['nodes'][node_id]['choices'].append(update_info['add_choice'])
            print(f"Added crisis awareness to {node_id}")
    
    # Create a few more investigation nodes that were referenced but missing
    missing_investigation_nodes = {
        "learn_secret_negotiations": {
            "title": "The Secret Deal",
            "description": "Acting Speaker Thorn lowers his voice: 'The delegates were negotiating emergency powers—the right to suspend normal trade laws during crisis. The Prism Cartel offered massive infrastructure investments in exchange for regulatory exemptions. But the delegates discovered something disturbing about who was really behind the proposal.'",
            "tags": ["Political", "Investigation"],
            "choices": [
                {
                    "text": "❓ 'Who was really behind the Cartel's proposal?'",
                    "target": "uncover_cartel_conspiracy"
                },
                {
                    "text": "💡 'That explains their disappearance. I need to investigate further.'",
                    "target": "investigate_disappearances"
                },
                {
                    "text": "⚖️ 'What emergency powers were they actually negotiating?'",
                    "target": "explore_legal_alternatives"
                },
                {
                    "text": "🔄 'I need to see the full crisis picture first.'",
                    "target": "startways_nexus"
                }
            ]
        },
        
        "explore_legal_alternatives": {
            "title": "Emergency Legal Protocols",
            "description": "The Assembly's legal clerk reveals dusty emergency protocols: 'In theory, emergency powers can be granted without the missing delegates—but only if we can prove their disappearance was directly related to the crisis. And the evidence suggests all these problems—trade wars, transport failures, harmonic disruptions—are coordinated attacks on our infrastructure.'",
            "tags": ["Political", "Legal"],
            "choices": [
                {
                    "text": "🔍 'Then we need proof these crises are connected.'",
                    "target": "startways_nexus"
                },
                {
                    "text": "💡 'I'll investigate the delegates to get that proof.'", 
                    "target": "investigate_disappearances"
                },
                {
                    "text": "⚖️ 'What powers exactly would this unlock?'",
                    "target": "political_crisis_start"
                },
                {
                    "text": "🚨 'I need to coordinate with other crisis response teams.'",
                    "target": "startways_nexus"
                }
            ]
        }
    }
    
    # Add missing investigation nodes
    for node_id, node_data in missing_investigation_nodes.items():
        world_data['nodes'][node_id] = node_data
        print(f"Added missing investigation node: {node_id}")
    
    print(f"Made {fixes_made} broken reference fixes")
    print(f"Added {len(missing_investigation_nodes)} missing investigation nodes")
    
    # Save the completed redesign
    with open('world/world.json', 'w', encoding='utf-8') as f:
        json.dump(world_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Redesign completion phase done!")
    print("Game now has:")
    print("- Crisis-focused central hub with 4 clear paths")  
    print("- Fixed broken navigation paths")
    print("- Emergency context that drives players to crisis management")
    print("- Clear objectives and progression hooks")

if __name__ == "__main__":
    complete_redesign()