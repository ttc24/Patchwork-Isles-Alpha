#!/usr/bin/env python3

import json

def add_missing_nodes():
    """Add the remaining missing investigation nodes"""
    
    # Load current world data
    with open('world/world.json', 'r', encoding='utf-8') as f:
        world_data = json.load(f)
    
    # Add the missing nodes
    missing_nodes = {
        "uncover_cartel_conspiracy": {
            "title": "The Conspiracy Unveiled",
            "description": "The aide's voice drops to a whisper: 'The Cartel wasn't acting alone. Behind their proposal was a shadow organization trying to destabilize our entire legal system. The delegates found communications showing this group has been orchestrating the transport failures, trade disruptions, and harmonic disturbances. They're trying to collapse the archipelago so they can seize control!'",
            "tags": ["Political", "Investigation", "Conspiracy"],
            "choices": [
                {
                    "text": "😱 'How deep does this conspiracy go?'",
                    "target": "analyze_delegate_notes"
                },
                {
                    "text": "🔍 'I need to see that evidence immediately.'",
                    "target": "analyze_delegate_notes"
                },
                {
                    "text": "⚠️ 'We need to coordinate with the other crisis response teams.'",
                    "target": "startways_nexus"
                },
                {
                    "text": "🚨 'This is bigger than just politics - I need to warn everyone!'",
                    "target": "startways_nexus"
                }
            ]
        },
        
        "analyze_delegate_notes": {
            "title": "The Smoking Gun",
            "description": "The scattered papers reveal a horrifying pattern: coded messages coordinating simultaneous attacks on all major infrastructure. The harmonic disruptions in the Singing Depths, the transport sabotage, the trade manipulation - it's all connected. One name appears repeatedly in the communications: 'The Architect.' And worse - there's a timeline. The final phase of their plan launches in just days.",
            "tags": ["Political", "Investigation", "Urgent"],
            "choices": [
                {
                    "text": "📋 'I need to take this evidence to every crisis team immediately.'",
                    "target": "startways_nexus"
                },
                {
                    "text": "🔍 'Who is this Architect? We need to find them.'",
                    "target": "interview_witnesses"
                },
                {
                    "text": "⏰ 'We're running out of time - what's the final phase?'",
                    "target": "political_crisis_start"
                },
                {
                    "text": "🎯 'We need to stop their other operations before they connect.'",
                    "target": "startways_nexus"
                }
            ]
        },
        
        "interview_witnesses": {
            "title": "The Web of Deception", 
            "description": "The other aides reveal disturbing details: meetings held in secret locations, encrypted communications, and a network of operatives embedded in every major organization. But one aide remembers something crucial: 'Delegate Sage mentioned a name right before disappearing - someone called the Architect was supposed to meet them at the old Resonance Chamber. That was the last anyone saw of them.'",
            "tags": ["Political", "Investigation"],
            "choices": [
                {
                    "text": "🏃 'I need to check that Resonance Chamber immediately!'",
                    "target": "root_orrery_resonance"
                },
                {
                    "text": "📊 'First I need to see all the evidence they gathered.'",
                    "target": "analyze_delegate_notes"
                },
                {
                    "text": "🚨 'This confirms the conspiracy - I need to coordinate the response.'",
                    "target": "startways_nexus"
                },
                {
                    "text": "⚖️ 'Can we use emergency powers to act on this intelligence?'",
                    "target": "explore_legal_alternatives"
                }
            ]
        },

        "report_initial_findings": {
            "title": "Briefing the Assembly",
            "description": "You present your initial findings to the emergency Assembly session. The chamber erupts in concerned murmurs as you describe the evidence of conspiracy and coordinated attacks. Acting Speaker Thorn calls for immediate action: 'If this conspiracy is real, then all our separate crisis responses need to coordinate immediately. We're not dealing with random problems - we're under organized attack!'",
            "tags": ["Political", "Briefing"],
            "choices": [
                {
                    "text": "🎯 'I'll coordinate with all crisis response teams.'",
                    "target": "startways_nexus"
                },
                {
                    "text": "📋 'Let me gather more evidence first.'",
                    "target": "analyze_delegate_notes"
                },
                {
                    "text": "⚖️ 'We need emergency powers to respond effectively.'",
                    "target": "explore_legal_alternatives"
                },
                {
                    "text": "🔍 'I need to continue investigating the conspiracy.'",
                    "target": "uncover_cartel_conspiracy"
                }
            ]
        }
    }
    
    # Add missing nodes
    for node_id, node_data in missing_nodes.items():
        world_data['nodes'][node_id] = node_data
        print(f"Added missing node: {node_id}")
    
    print(f"Added {len(missing_nodes)} missing nodes")
    
    # Save updated world
    with open('world/world.json', 'w', encoding='utf-8') as f:
        json.dump(world_data, f, indent=2, ensure_ascii=False)
    
    print("✅ All missing investigation nodes added!")

if __name__ == "__main__":
    add_missing_nodes()