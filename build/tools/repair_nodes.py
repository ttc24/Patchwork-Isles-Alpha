#!/usr/bin/env python3
"""
Automatic repair tool for broken node references in world.json.
Identifies and fixes missing node references by creating stub nodes or redirecting to safe alternatives.
"""

import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Set, List, Tuple

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

try:
    from engine.schema_validator import WorldValidator
    SCHEMA_VALIDATION_AVAILABLE = True
except ImportError:
    SCHEMA_VALIDATION_AVAILABLE = False


class NodeRepairTool:
    """Tool for automatically repairing broken node references."""
    
    def __init__(self, world_data: Dict[str, Any]):
        self.world_data = world_data
        self.nodes = world_data.get("nodes", {})
        self.broken_refs = []
        self.repairs_made = []
    
    def analyze_broken_references(self) -> List[Dict[str, Any]]:
        """Analyze the world data to find broken node references."""
        broken_refs = []
        node_ids = set(self.nodes.keys())
        
        # Check start entries
        starts = self.world_data.get("starts", [])
        for i, start in enumerate(starts):
            if not isinstance(start, dict):
                continue
            
            target_node = start.get("node")
            if target_node and target_node not in node_ids:
                broken_refs.append({
                    "type": "start_reference",
                    "index": i,
                    "start_id": start.get("id", "unknown"),
                    "missing_node": target_node,
                    "context": f"Start '{start.get('id', 'unknown')}'"
                })
        
        # Check choice destinations
        for node_id, node_data in self.nodes.items():
            if not isinstance(node_data, dict):
                continue
            
            choices = node_data.get("choices", [])
            for i, choice in enumerate(choices):
                if not isinstance(choice, dict):
                    continue
                
                target = choice.get("target")
                if target and target not in node_ids:
                    broken_refs.append({
                        "type": "choice_reference",
                        "node_id": node_id,
                        "choice_index": i,
                        "missing_node": target,
                        "choice_text": choice.get("text", "Unknown"),
                        "context": f"Node '{node_id}' choice {i}"
                    })
        
        self.broken_refs = broken_refs
        return broken_refs
    
    def suggest_repair_strategies(self) -> Dict[str, List[str]]:
        """Suggest repair strategies for each broken reference."""
        strategies = {}
        
        for ref in self.broken_refs:
            missing_node = ref["missing_node"]
            if missing_node not in strategies:
                strategies[missing_node] = []
            
            # Strategy 1: Create stub node
            strategies[missing_node].append("create_stub")
            
            # Strategy 2: Find similar existing node
            similar_node = self._find_similar_node(missing_node)
            if similar_node:
                strategies[missing_node].append(f"redirect_to_{similar_node}")
            
            # Strategy 3: Redirect to safe node
            safe_node = self._find_safe_node()
            if safe_node:
                strategies[missing_node].append(f"redirect_to_safe_{safe_node}")
        
        return strategies
    
    def auto_repair(self, create_stubs: bool = True, backup: bool = True) -> int:
        """
        Automatically repair all broken references.
        
        Args:
            create_stubs: Whether to create stub nodes for missing references
            backup: Whether to create a backup before making changes
        
        Returns:
            Number of repairs made
        """
        if backup:
            self._create_backup()
        
        repairs_count = 0
        
        # Analyze broken references
        broken_refs = self.analyze_broken_references()
        
        if not broken_refs:
            print("No broken references found!")
            return 0
        
        print(f"Found {len(broken_refs)} broken references")
        
        # Group by missing node
        missing_nodes = {}
        for ref in broken_refs:
            missing_node = ref["missing_node"]
            if missing_node not in missing_nodes:
                missing_nodes[missing_node] = []
            missing_nodes[missing_node].append(ref)
        
        # Repair each missing node
        for missing_node, refs in missing_nodes.items():
            print(f"Repairing missing node: {missing_node} ({len(refs)} references)")
            
            if create_stubs:
                # Create stub node
                stub_node = self._create_stub_node(missing_node, refs)
                self.nodes[missing_node] = stub_node
                repairs_count += 1
                self.repairs_made.append(f"Created stub node '{missing_node}'")
                print(f"  ✓ Created stub node")
            else:
                # Redirect to safe alternative
                safe_target = self._find_safe_node()
                if safe_target:
                    repairs_count += self._redirect_references(refs, safe_target)
                    self.repairs_made.append(f"Redirected {len(refs)} refs from '{missing_node}' to '{safe_target}'")
                    print(f"  ✓ Redirected to {safe_target}")
        
        print(f"Made {repairs_count} repairs")
        return repairs_count
    
    def _create_stub_node(self, node_id: str, references: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Create a stub node for the missing reference."""
        # Analyze the references to determine what kind of node this should be
        ref_contexts = [ref.get("context", "") for ref in references]
        
        # Try to infer node type and content
        title = self._generate_node_title(node_id)
        text = self._generate_node_text(node_id, references)
        choices = self._generate_stub_choices(node_id)
        
        stub_node = {
            "id": node_id,
            "title": title,
            "text": text,
            "choices": choices,
            "_auto_generated": True,
            "_generation_reason": f"Missing node referenced by: {', '.join(ref_contexts)}"
        }
        
        return stub_node
    
    def _generate_node_title(self, node_id: str) -> str:
        """Generate an appropriate title for a stub node."""
        # Convert snake_case to Title Case
        words = node_id.replace("_", " ").split()
        title_words = []
        
        for word in words:
            if word.lower() in ["and", "or", "the", "a", "an", "of", "in", "on", "at", "to", "for"]:
                title_words.append(word.lower())
            else:
                title_words.append(word.capitalize())
        
        title = " ".join(title_words)
        
        # Handle some common patterns
        if "tutorial" in node_id.lower():
            return f"Tutorial: {title.replace('Tutorial', '').strip()}"
        elif "ending" in node_id.lower():
            return f"Ending: {title.replace('Ending', '').strip()}"
        elif any(word in node_id.lower() for word in ["hub", "docks", "market", "court"]):
            return f"{title} Hub"
        else:
            return title
    
    def _generate_node_text(self, node_id: str, references: List[Dict[str, Any]]) -> str:
        """Generate appropriate text for a stub node."""
        base_text = f"[This is an auto-generated placeholder for the missing '{node_id}' location.]"
        
        if "tutorial" in node_id.lower():
            return f"{base_text} This appears to be part of the tutorial sequence. The content for this area is still being developed."
        elif "ending" in node_id.lower():
            return f"{base_text} This is an ending node. The conclusion to this story path is still being written."
        elif any(word in node_id.lower() for word in ["hub", "docks", "market"]):
            return f"{base_text} This is a hub location where multiple story paths converge. The area is currently under construction."
        else:
            return f"{base_text} This location exists in the story but its content hasn't been written yet."
    
    def _generate_stub_choices(self, node_id: str) -> List[Dict[str, Any]]:
        """Generate appropriate choices for a stub node."""
        safe_node = self._find_safe_node()
        
        choices = [
            {
                "text": "Continue the story (return to a safe location)",
                "target": safe_node
            }
        ]
        
        # Add context-specific choices
        if "tutorial" in node_id.lower():
            choices.insert(0, {
                "text": "Return to tutorial start",
                "target": self._find_tutorial_start()
            })
        elif "ending" in node_id.lower():
            choices = [
                {
                    "text": "Reflect on your journey",
                    "effects": [
                        {
                            "type": "set_flag",
                            "flag": f"reached_{node_id}",
                            "value": True
                        }
                    ],
                    "target": safe_node
                }
            ]
        
        return choices
    
    def _find_similar_node(self, missing_node: str) -> str:
        """Find an existing node with a similar name/purpose."""
        missing_lower = missing_node.lower()
        best_match = None
        best_score = 0
        
        for existing_node in self.nodes:
            existing_lower = existing_node.lower()
            
            # Calculate similarity score
            score = 0
            
            # Exact word matches
            missing_words = set(missing_lower.split("_"))
            existing_words = set(existing_lower.split("_"))
            common_words = missing_words.intersection(existing_words)
            score += len(common_words) * 2
            
            # Substring matches
            if missing_lower in existing_lower or existing_lower in missing_lower:
                score += 1
            
            if score > best_score and score >= 2:  # Minimum threshold
                best_score = score
                best_match = existing_node
        
        return best_match
    
    def _find_safe_node(self) -> str:
        """Find a safe node to redirect to."""
        # Look for tutorial nodes first
        for node_id in self.nodes:
            if "tutorial_arrival" in node_id.lower():
                return node_id
        
        # Look for other tutorial nodes
        for node_id in self.nodes:
            if "tutorial" in node_id.lower():
                return node_id
        
        # Look for start nodes from starts list
        starts = self.world_data.get("starts", [])
        if starts:
            for start in starts:
                if isinstance(start, dict) and "node" in start:
                    target_node = start["node"]
                    if target_node in self.nodes:
                        return target_node
        
        # Last resort: return first available node
        if self.nodes:
            return next(iter(self.nodes))
        
        return "emergency_fallback"
    
    def _find_tutorial_start(self) -> str:
        """Find the tutorial start node."""
        tutorial_patterns = ["tutorial_arrival", "tutorial_start", "tutorial_beach", "first_five"]
        
        for pattern in tutorial_patterns:
            for node_id in self.nodes:
                if pattern in node_id.lower():
                    return node_id
        
        return self._find_safe_node()
    
    def _redirect_references(self, references: List[Dict[str, Any]], target_node: str) -> int:
        """Redirect all references to a target node."""
        redirects = 0
        
        for ref in references:
            if ref["type"] == "start_reference":
                # Update start entry
                starts = self.world_data.get("starts", [])
                if ref["index"] < len(starts):
                    starts[ref["index"]]["node"] = target_node
                    redirects += 1
            
            elif ref["type"] == "choice_reference":
                # Update choice target
                node_data = self.nodes.get(ref["node_id"])
                if node_data and "choices" in node_data:
                    choices = node_data["choices"]
                    if ref["choice_index"] < len(choices):
                        choices[ref["choice_index"]]["target"] = target_node
                        # Mark choice as redirected
                        choice_text = choices[ref["choice_index"]].get("text", "")
                        if not choice_text.startswith("[REDIRECTED]"):
                            choices[ref["choice_index"]]["text"] = f"[REDIRECTED] {choice_text}"
                        redirects += 1
        
        return redirects
    
    def _create_backup(self):
        """Create a backup of the world file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        world_path = PROJECT_ROOT / "world" / "world.json"
        backup_path = PROJECT_ROOT / "world" / f"world_backup_repair_{timestamp}.json"
        
        try:
            if world_path.exists():
                with open(world_path, 'r', encoding='utf-8') as src:
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                print(f"Created backup: {backup_path}")
        except Exception as e:
            print(f"Warning: Could not create backup: {e}")
    
    def save_repaired_world(self, output_path: Path = None):
        """Save the repaired world data."""
        if output_path is None:
            output_path = PROJECT_ROOT / "world" / "world.json"
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.world_data, f, indent=2, ensure_ascii=False)
            f.write('\n')
        
        print(f"Saved repaired world to: {output_path}")
    
    def generate_repair_report(self) -> str:
        """Generate a report of repairs made."""
        report = ["Node Repair Report", "=" * 50, ""]
        
        if not self.repairs_made:
            report.append("No repairs were made.")
        else:
            report.append(f"Total repairs made: {len(self.repairs_made)}")
            report.append("")
            report.append("Repairs:")
            for repair in self.repairs_made:
                report.append(f"  - {repair}")
        
        report.append("")
        report.append("Broken references found:")
        for ref in self.broken_refs:
            report.append(f"  - {ref['context']}: missing '{ref['missing_node']}'")
        
        return "\n".join(report)


def main():
    """Main function to run the node repair tool."""
    world_path = PROJECT_ROOT / "world" / "world.json"
    
    if not world_path.exists():
        print(f"Error: World file not found at {world_path}")
        sys.exit(1)
    
    # Load world data
    try:
        with open(world_path, 'r', encoding='utf-8') as f:
            world_data = json.load(f)
    except Exception as e:
        print(f"Error loading world data: {e}")
        sys.exit(1)
    
    # Create repair tool
    repair_tool = NodeRepairTool(world_data)
    
    # Analyze broken references
    print("Analyzing broken node references...")
    broken_refs = repair_tool.analyze_broken_references()
    
    if not broken_refs:
        print("✅ No broken node references found!")
        return
    
    print(f"🔍 Found {len(broken_refs)} broken references:")
    for ref in broken_refs[:10]:  # Show first 10
        print(f"  - {ref['context']}: missing '{ref['missing_node']}'")
    if len(broken_refs) > 10:
        print(f"  ... and {len(broken_refs) - 10} more")
    
    # Ask user for repair strategy
    print("\nRepair options:")
    print("1. Create stub nodes for missing references (recommended)")
    print("2. Redirect missing references to safe locations")
    print("3. Show detailed analysis and exit")
    
    try:
        choice = input("\nEnter your choice (1-3) [1]: ").strip() or "1"
    except KeyboardInterrupt:
        print("\nOperation cancelled.")
        return
    
    if choice == "3":
        strategies = repair_tool.suggest_repair_strategies()
        print("\nDetailed analysis:")
        for missing_node, strategy_list in strategies.items():
            print(f"  Missing node: {missing_node}")
            print(f"    Suggested strategies: {', '.join(strategy_list)}")
        return
    
    create_stubs = choice == "1"
    
    # Perform repairs
    print(f"\n{'Creating stub nodes' if create_stubs else 'Redirecting references'}...")
    repairs_made = repair_tool.auto_repair(create_stubs=create_stubs)
    
    if repairs_made > 0:
        # Save repaired world
        repair_tool.save_repaired_world()
        
        # Generate report
        report = repair_tool.generate_repair_report()
        report_path = PROJECT_ROOT / "logs" / f"repair_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
        report_path.parent.mkdir(exist_ok=True)
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)
        
        print(f"\n✅ Repairs completed! Report saved to: {report_path}")
        print("\nNext steps:")
        print("1. Run 'python tools/validate.py' to verify repairs")
        print("2. Test the game to ensure everything works correctly")
        print("3. Review auto-generated nodes and improve their content")
    else:
        print("❌ No repairs could be made.")


if __name__ == "__main__":
    main()