#!/usr/bin/env python3
"""Find circular loops and dead ends in the game world."""

import json
from collections import defaultdict, deque

def analyze_loops(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    nodes = data.get('nodes', {})
    
    # Build adjacency graph of unconditional choices
    graph = defaultdict(list)
    all_choices = defaultdict(list)  # Track all choices including conditional ones
    
    for node_id, node in nodes.items():
        for choice in node.get('choices', []):
            target = choice.get('target')
            if target and target in nodes:
                all_choices[node_id].append((target, choice))
                # Only add to graph if it has no condition (always available)
                if not choice.get('condition'):
                    graph[node_id].append(target)
    
    def find_strongly_connected_components():
        """Find strongly connected components (loops) in the graph."""
        visited = set()
        finish_order = []
        
        def dfs1(node):
            if node in visited:
                return
            visited.add(node)
            for neighbor in graph[node]:
                dfs1(neighbor)
            finish_order.append(node)
        
        # First DFS to get finish times
        for node in list(graph.keys()):
            dfs1(node)
        
        # Build reverse graph
        reverse_graph = defaultdict(list)
        for node in list(graph.keys()):
            for neighbor in graph[node]:
                reverse_graph[neighbor].append(node)
        
        # Second DFS on reverse graph
        visited = set()
        components = []
        
        def dfs2(node, component):
            if node in visited:
                return
            visited.add(node)
            component.append(node)
            for neighbor in reverse_graph[node]:
                dfs2(neighbor, component)
        
        for node in reversed(finish_order):
            if node not in visited:
                component = []
                dfs2(node, component)
                if len(component) > 1:  # Only interested in multi-node components
                    components.append(component)
        
        return components
    
    def find_dead_ends():
        """Find nodes with no unconditional exit paths."""
        dead_ends = []
        for node_id, node in nodes.items():
            # Skip endings
            if node_id in data.get('endings', {}):
                continue
            
            # Check if there are any unconditional choices
            has_unconditional_exit = False
            for choice in node.get('choices', []):
                if choice.get('target') and not choice.get('condition'):
                    has_unconditional_exit = True
                    break
            
            if not has_unconditional_exit and node.get('choices'):
                dead_ends.append((node_id, node))
        
        return dead_ends
    
    def analyze_problematic_paths():
        """Find paths that lead to dead ends or loops with only conditional exits."""
        problematic = []
        
        for node_id, node in nodes.items():
            if node_id in data.get('endings', {}):
                continue
                
            # Check if all choices from this node require conditions
            unconditional_choices = [c for c in node.get('choices', []) if not c.get('condition')]
            conditional_choices = [c for c in node.get('choices', []) if c.get('condition')]
            
            if not unconditional_choices and conditional_choices:
                # This node only has conditional exits - potential trap
                problematic.append({
                    'node_id': node_id,
                    'title': node.get('title', 'No title'),
                    'issue': 'Only conditional exits',
                    'choices': len(conditional_choices)
                })
        
        return problematic
    
    # Run analysis
    loops = find_strongly_connected_components()
    dead_ends = find_dead_ends()
    problematic_paths = analyze_problematic_paths()
    
    print("=== CIRCULAR LOOP ANALYSIS ===")
    print(f"Found {len(loops)} potential circular loops")
    print(f"Found {len(dead_ends)} nodes with only conditional exits")
    print(f"Found {len(problematic_paths)} potentially problematic paths")
    
    if loops:
        print(f"\n=== CIRCULAR LOOPS ===")
        for i, loop in enumerate(loops, 1):
            print(f"\nLoop {i}: {len(loop)} nodes")
            for node_id in loop:
                title = nodes[node_id].get('title', 'No title')
                print(f"  {node_id}: {title}")
                
                # Show what this node connects to within the loop
                targets_in_loop = [t for t in graph[node_id] if t in loop]
                if targets_in_loop:
                    print(f"    → {', '.join(targets_in_loop)}")
    
    if dead_ends:
        print(f"\n=== NODES WITH ONLY CONDITIONAL EXITS ===")
        for node_id, node in dead_ends:
            title = node.get('title', 'No title')
            choices = node.get('choices', [])
            print(f"\n{node_id}: {title}")
            print(f"  {len(choices)} conditional choices:")
            
            for choice in choices:
                condition = choice.get('condition', {})
                target = choice.get('target', 'unknown')
                choice_text = choice.get('text', 'Unnamed choice')[:50]
                
                # Summarize condition
                if condition:
                    cond_type = condition.get('type', 'unknown')
                    if cond_type == 'has_tag':
                        cond_desc = f"Tag: {condition.get('value')}"
                    elif cond_type == 'has_trait':
                        cond_desc = f"Trait: {condition.get('value')}"
                    elif cond_type == 'has_item':
                        cond_desc = f"Item: {condition.get('value')}"
                    elif cond_type == 'rep_at_least':
                        cond_desc = f"Rep: {condition.get('faction')} ≥{condition.get('value')}"
                    else:
                        cond_desc = f"{cond_type}"
                    
                    print(f"    • {choice_text} → {target} (Req: {cond_desc})")
                else:
                    print(f"    • {choice_text} → {target} (No condition)")
    
    if problematic_paths:
        print(f"\n=== PROBLEMATIC PATHS SUMMARY ===")
        for path in problematic_paths:
            print(f"  {path['node_id']}: {path['title']} - {path['issue']} ({path['choices']} choices)")
    
    return {
        'loops': loops,
        'dead_ends': dead_ends,
        'problematic_paths': problematic_paths
    }

if __name__ == "__main__":
    analysis = analyze_loops("world/world.json")