#!/usr/bin/env python3

import json
from datetime import datetime

def redesign_game():
    """Completely restructure the game for better progression and engagement"""
    
    # Load current world data
    with open('world/world.json', 'r', encoding='utf-8') as f:
        world_data = json.load(f)
    
    print(f"Current game has {len(world_data['nodes'])} nodes")
    
    # Create new simplified Startways Nexus
    new_startways = {
        "title": "Startways Nexus - Central Command",
        "description": "The colossal seed-compass has been reconfigured as a mission center. Four major crisis paths pulse with urgent light, each requiring your immediate attention. The route steward presents you with critical briefings as trade routes collapse and diplomats vanish.",
        "tags": [],
        "choices": [
            {
                "text": "🏛️ [POLITICAL CRISIS] Investigate the missing Root Assembly delegates",
                "target": "political_crisis_start",
                "details": "Current objective: Three key delegates have vanished during crucial guest-law negotiations. Their disappearance threatens to destabilize the entire archipelago's legal framework."
            },
            {
                "text": "💰 [TRADE DISRUPTION] Address the escalating cartel price wars", 
                "target": "economic_crisis_start",
                "details": "Current objective: The Prism Cartel's market manipulation is bankrupting smaller traders. Communities are being cut off from essential supplies."
            },
            {
                "text": "🎵 [DEPTHS DISTURBANCE] Investigate the harmonic disruptions",
                "target": "exploration_crisis_start", 
                "details": "Current objective: Strange resonances from the Singing Depths are interfering with navigation systems. Several transport routes have failed catastrophically."
            },
            {
                "text": "🚡 [NETWORK COLLAPSE] Repair the failing transport grid",
                "target": "infrastructure_crisis_start",
                "details": "Current objective: The storm-rail network is experiencing systematic failures. Remote communities are becoming isolated and desperate."
            }
        ]
    }
    
    # Create new crisis starting points with clear objectives
    crisis_nodes = {
        "political_crisis_start": {
            "title": "Emergency Assembly Session",
            "description": "The Root Assembly chamber buzzes with panic. Acting Speaker Thorn addresses a half-empty room: 'Delegates Willow, Sage, and Ember disappeared three days ago during closed negotiations about trade route rights. Without them, we cannot ratify the Seasonal Compact. The legal framework holding our communities together hangs by a thread.'",
            "tags": ["Political"],
            "choices": [
                {
                    "text": "💡 'I'll investigate their last known locations.'",
                    "target": "investigate_disappearances",
                    "effects": [{"type": "set_flag", "flag": "investigating_delegates", "value": True}]
                },
                {
                    "text": "🤝 'What were they negotiating that was so sensitive?'",
                    "target": "learn_secret_negotiations"
                },
                {
                    "text": "⚖️ 'Can the Compact be ratified without them?'", 
                    "target": "explore_legal_alternatives"
                },
                {
                    "text": "🔄 'I need more information before committing.'",
                    "target": "startways_nexus"
                }
            ]
        },
        
        "economic_crisis_start": {
            "title": "Merchant's Desperate Plea",
            "description": "In the Prism Galleria's outer markets, trader Kess grabs your sleeve: 'The Cartel's price-fixing has destroyed us! They're selling crystals below cost to bankrupt independents, then they'll control everything. Five trading families have lost everything this week. If this continues, only the Cartel will remain—and they'll own us all.'",
            "tags": ["Economic"],
            "choices": [
                {
                    "text": "📊 'Show me the evidence of price manipulation.'",
                    "target": "examine_trade_records",
                    "effects": [{"type": "set_flag", "flag": "investigating_cartel", "value": True}]
                },
                {
                    "text": "🤝 'I'll speak with the Cartel leadership directly.'",
                    "target": "confront_cartel_leaders"
                },
                {
                    "text": "💡 'What if independent traders formed a cooperative?'",
                    "target": "explore_trader_alliance"
                },
                {
                    "text": "🔄 'Let me assess the situation from other angles first.'",
                    "target": "startways_nexus"
                }
            ]
        },
        
        "exploration_crisis_start": {
            "title": "Navigator's Emergency Report", 
            "description": "Storm-rail pilot Chen bursts into the nexus, charts in hand: 'The harmonics from the Singing Depths have gone completely chaotic! Three transport runs failed yesterday when our navigation crystals shattered. If this continues, we'll lose the eastern trade routes entirely. Something down there is very wrong—or very angry.'",
            "tags": ["Exploration"],
            "choices": [
                {
                    "text": "🎵 'I'll descend into the Depths to investigate the source.'",
                    "target": "descend_to_depths",
                    "effects": [{"type": "set_flag", "flag": "investigating_harmonics", "value": True}]
                },
                {
                    "text": "📡 'Can we isolate the affected navigation systems?'",
                    "target": "technical_analysis"
                },
                {
                    "text": "🗣️ 'Has anyone tried communicating with whatever's causing this?'",
                    "target": "attempt_communication"
                },
                {
                    "text": "🔄 'I should gather more intelligence before acting.'",
                    "target": "startways_nexus"
                }
            ]
        },
        
        "infrastructure_crisis_start": {
            "title": "Network Operations Center",
            "description": "Chief Engineer Maya stands before a control board lit with warning signals: 'Fifteen percent of the storm-rail network is down, and it's spreading. The failures aren't random—someone or something is systematically targeting key junction points. If we lose the main trunk lines, half the archipelago will be cut off within days.'",
            "tags": ["Infrastructure"],
            "choices": [
                {
                    "text": "🔧 'Show me the failure pattern—I'll investigate the sabotage.'",
                    "target": "track_sabotage",
                    "effects": [{"type": "set_flag", "flag": "investigating_sabotage", "value": True}]
                },
                {
                    "text": "⚡ 'Can we reroute through backup systems?'",
                    "target": "emergency_rerouting"
                },
                {
                    "text": "🛡️ 'We need to secure the remaining functional lines.'",
                    "target": "defensive_measures"
                },
                {
                    "text": "🔄 'Let me review all crisis reports before choosing a path.'",
                    "target": "startways_nexus"
                }
            ]
        }
    }
    
    # Remove all generic placeholder nodes I created earlier
    nodes_to_remove = [
        'void_reaches_beacon_station', 'shadow_marshes_mist_pier', 'tidal_sanctum_novice_pools',
        'temporal_gardens_chronos_gate', 'floating_academy_archives', 'crystalline_reaches_observatory',
        'crystalline_reaches_waiting_grove', 'root_orrery_deep_teaching', 'root_orrery_apocalypse_vision',
        'singing_depths_communication_spire', 'root_orrery_mastery_training', 'singing_depths_medical_sanctuary',
        'root_assembly_mediation_attempt', 'singing_depths_research_lab', 'singing_depths_archive_vault',
        'singing_depths_renewal_chamber', 'singing_depths_meditation_grove', 'singing_depths_alternative_solutions',
        'ending_depths_bridge_keeper', 'singing_depths_embassy_founding'
    ]
    
    # Remove placeholder nodes
    for node_id in nodes_to_remove:
        if node_id in world_data['nodes']:
            del world_data['nodes'][node_id]
            print(f"Removed placeholder node: {node_id}")
    
    # Update the startways nexus
    world_data['nodes']['startways_nexus'] = new_startways
    
    # Add new crisis nodes
    for node_id, node_data in crisis_nodes.items():
        world_data['nodes'][node_id] = node_data
    
    print(f"Added {len(crisis_nodes)} new crisis starting nodes")
    print(f"Game now has {len(world_data['nodes'])} nodes")
    
    # Save the redesigned world
    with open('world/world.json', 'w', encoding='utf-8') as f:
        json.dump(world_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Game redesign phase 1 complete!")
    print("- Simplified central hub to 4 clear crisis paths")  
    print("- Added objective-driven starting scenarios")
    print("- Removed confusing placeholder content")
    print("- Each path now has clear goals and progression hooks")

def create_investigation_nodes():
    """Add the second layer of nodes for each crisis path"""
    
    with open('world/world.json', 'r', encoding='utf-8') as f:
        world_data = json.load(f)
    
    # Investigation nodes for each path
    investigation_nodes = {
        # Political Crisis Investigation Path
        "investigate_disappearances": {
            "title": "The Delegates' Last Stand",
            "description": "Delegate Willow's office shows signs of a hurried departure—papers scattered, a half-finished letter about 'concerning Cartel proposals,' and a window left open. Her aide whispers: 'She was frightened about something in the negotiations. Said the Cartel was offering deals that were too good to be true.'",
            "tags": ["Political", "Investigation"],
            "choices": [
                {
                    "text": "🔍 'What exactly were these Cartel proposals?'",
                    "target": "uncover_cartel_conspiracy"
                },
                {
                    "text": "📋 'Let me examine those scattered papers.'",
                    "target": "analyze_delegate_notes"
                },
                {
                    "text": "👥 'I need to speak with the other delegates' aides.'",
                    "target": "interview_witnesses"
                },
                {
                    "text": "🏛️ 'Return to the Assembly with this information.'",
                    "target": "report_initial_findings"
                }
            ]
        },
        
        # Economic Crisis Investigation Path  
        "examine_trade_records": {
            "title": "The Paper Trail",
            "description": "Kess produces ledgers showing devastating price patterns: Prism goods selling for 60% below cost, then mysteriously rising 300% once competitors disappeared. But there's more—transport 'accidents' affecting only independent traders, and Cartel buyers who knew exactly when to purchase struggling businesses.",
            "tags": ["Economic", "Investigation"],
            "choices": [
                {
                    "text": "💰 'This looks like systematic market manipulation—I have enough evidence.'",
                    "target": "confront_cartel_with_proof"
                },
                {
                    "text": "🚢 'Tell me more about these convenient transport accidents.'",
                    "target": "investigate_cartel_sabotage"
                },
                {
                    "text": "🤝 'We need to organize the affected traders for collective action.'",
                    "target": "build_merchant_coalition"
                },
                {
                    "text": "⚖️ 'This evidence needs to reach the Root Assembly immediately.'",
                    "target": "political_crisis_start"
                }
            ]
        },
        
        # Exploration Crisis Investigation Path
        "descend_to_depths": {
            "title": "The Harmonic Disturbance",
            "description": "Deep beneath the surface, the usual crystalline harmony has become a discordant scream. The moss networks pulse erratically, and in the distance, you hear something unprecedented: voices. Not the deep, slow thoughts of the ancient guardians, but urgent, rapid communication in patterns you've never heard before.",
            "tags": ["Exploration", "Deep-Listener"],
            "choices": [
                {
                    "text": "🎵 'Try to understand these new harmonic patterns.'",
                    "target": "decode_urgent_harmonics"
                },
                {
                    "text": "👁️ 'Follow the voices to their source.'",
                    "target": "locate_harmonic_source"
                },
                {
                    "text": "🤝 'Attempt to communicate with whatever is causing this.'",
                    "target": "first_contact_depths"
                },
                {
                    "text": "⬆️ 'This is beyond my abilities—return with backup.'",
                    "target": "exploration_crisis_start"
                }
            ]
        },
        
        # Infrastructure Crisis Investigation Path
        "track_sabotage": {
            "title": "The Sabotage Pattern",
            "description": "Maya's data reveals a chilling truth: the failures aren't random attacks, but surgical strikes. Someone with intimate knowledge of the network is targeting exactly the right points to maximize disruption while avoiding detection. Worse, the sabotage is accelerating—and the next target appears to be the main Startways junction.",
            "tags": ["Infrastructure", "Investigation"],
            "choices": [
                {
                    "text": "🕵️ 'Who has this level of technical knowledge?'",
                    "target": "identify_inside_threat"
                },
                {
                    "text": "🛡️ 'We need to protect the Startways junction immediately.'",
                    "target": "defend_critical_infrastructure"
                },
                {
                    "text": "🎯 'Set a trap at the next predicted target.'",
                    "target": "sabotage_counterstrike"
                },
                {
                    "text": "📡 'Can we trace the sabotage signals to their origin?'",
                    "target": "technical_investigation"
                }
            ]
        }
    }
    
    # Add investigation nodes
    for node_id, node_data in investigation_nodes.items():
        world_data['nodes'][node_id] = node_data
    
    print(f"Added {len(investigation_nodes)} investigation nodes")
    
    # Save updated world
    with open('world/world.json', 'w', encoding='utf-8') as f:
        json.dump(world_data, f, indent=2, ensure_ascii=False)
    
    print("✅ Investigation layer complete!")

if __name__ == "__main__":
    redesign_game()
    create_investigation_nodes()