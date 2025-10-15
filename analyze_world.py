#!/usr/bin/env python3
"""Analyze world.json for missing nodes and incomplete paths."""

import json
from collections import defaultdict

def analyze_world(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    nodes = data.get('nodes', {})
    
    # Find all referenced targets
    all_targets = set()
    node_choices = defaultdict(list)
    
    for node_id, node in nodes.items():
        for choice in node.get('choices', []):
            target = choice.get('target')
            if target:
                all_targets.add(target)
                node_choices[node_id].append({
                    'text': choice.get('text', 'Unnamed choice'),
                    'target': target
                })
    
    # Find missing nodes
    missing_nodes = [t for t in all_targets if t not in nodes]
    
    # Find nodes with no choices (potential dead ends)
    dead_ends = [node_id for node_id, node in nodes.items() 
                 if not node.get('choices') and node_id not in data.get('endings', {})]
    
    # Find nodes with very short text (potential stubs)
    short_nodes = [(node_id, len(node.get('text', ''))) 
                   for node_id, node in nodes.items() 
                   if len(node.get('text', '')) < 100]
    
    print(f"=== World Analysis ===")
    print(f"Total nodes: {len(nodes)}")
    print(f"Missing nodes: {len(missing_nodes)}")
    print(f"Dead end nodes: {len(dead_ends)}")
    print(f"Short nodes (<100 chars): {len(short_nodes)}")
    
    print(f"\n=== Missing Nodes ===")
    for target in sorted(missing_nodes):
        # Find which nodes reference this missing target
        referencing_nodes = []
        for node_id, choices in node_choices.items():
            for choice in choices:
                if choice['target'] == target:
                    referencing_nodes.append(f"{node_id}: '{choice['text']}'")
        
        print(f"  {target}")
        for ref in referencing_nodes[:3]:  # Limit to first 3 references
            print(f"    ← {ref}")
        if len(referencing_nodes) > 3:
            print(f"    ... and {len(referencing_nodes) - 3} more")
        print()
    
    print(f"\n=== Dead End Nodes ===")
    for node_id in sorted(dead_ends)[:10]:  # Limit output
        title = nodes[node_id].get('title', 'No title')
        text_preview = nodes[node_id].get('text', '')[:60] + "..."
        print(f"  {node_id}: {title}")
        print(f"    {text_preview}")
    
    print(f"\n=== Short Nodes (potential stubs) ===")
    for node_id, length in sorted(short_nodes, key=lambda x: x[1])[:10]:
        title = nodes[node_id].get('title', 'No title')
        print(f"  {node_id}: {title} ({length} chars)")
    
    return {
        'missing_nodes': missing_nodes,
        'dead_ends': dead_ends,
        'short_nodes': short_nodes,
        'node_choices': node_choices
    }

if __name__ == "__main__":
    analysis = analyze_world("world/world.json")