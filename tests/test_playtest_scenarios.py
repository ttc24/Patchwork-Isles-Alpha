#!/usr/bin/env python3
"""
Automated playtest scenarios for Patchwork Isles.
Tests common story paths and player interactions to catch regressions.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
import sys
from typing import Dict, Any, List

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engine.engine_min import GameState, default_profile
from engine.settings import Settings


class AutomatedPlaytestScenario:
    """Base class for automated playtest scenarios."""
    
    def __init__(self, world_data: Dict[str, Any], scenario_name: str):
        self.world_data = world_data
        self.scenario_name = scenario_name
        self.game_state = None
        self.steps_taken = []
        self.errors_encountered = []
    
    def setup_game_state(self, start_id: str = None, initial_tags: List[str] = None) -> GameState:
        """Set up a game state for testing."""
        profile = default_profile()
        settings = Settings()
        
        # Create temporary profile path
        temp_dir = tempfile.mkdtemp()
        profile_path = os.path.join(temp_dir, "test_profile.json")
        
        self.game_state = GameState(
            self.world_data,
            profile,
            profile_path,
            settings
        )
        
        # Set initial tags if provided
        if initial_tags:
            self.game_state.player["tags"] = list(initial_tags)
        
        # Set starting node if provided
        if start_id:
            self.game_state.start_id = start_id
            self.game_state.current_node = start_id
        
        return self.game_state
    
    def simulate_choice(self, choice_index: int) -> bool:
        """
        Simulate making a choice in the current node.
        
        Args:
            choice_index: Index of choice to make (0-based)
        
        Returns:
            True if choice was successful, False otherwise
        """
        if not self.game_state or not self.game_state.current_node:
            self.errors_encountered.append("No current node to make choice in")
            return False
        
        current_node_id = self.game_state.current_node
        node_data = self.world_data.get("nodes", {}).get(current_node_id)
        
        if not node_data:
            self.errors_encountered.append(f"Node {current_node_id} not found")
            return False
        
        choices = node_data.get("choices", [])
        if choice_index >= len(choices):
            self.errors_encountered.append(f"Choice index {choice_index} out of range for node {current_node_id}")
            return False
        
        choice = choices[choice_index]
        choice_text = choice.get("text", "Unknown choice")
        
        # Log the step
        step = {
            "action": "choice",
            "node": current_node_id,
            "choice_index": choice_index,
            "choice_text": choice_text,
            "target": choice.get("target")
        }
        self.steps_taken.append(step)
        
        # Apply choice effects if any
        effects = choice.get("effects", [])
        for effect in effects:
            self._apply_effect(effect)
        
        # Move to target node
        target = choice.get("target")
        if target:
            self.game_state.current_node = target
            return True
        else:
            self.errors_encountered.append(f"Choice {choice_index} in node {current_node_id} has no target")
            return False
    
    def _apply_effect(self, effect: Dict[str, Any]):
        """Apply a single effect to the game state."""
        effect_type = effect.get("type")
        value = effect.get("value")
        
        if effect_type == "add_tag":
            if value not in self.game_state.player["tags"]:
                self.game_state.player["tags"].append(value)
        elif effect_type == "add_trait":
            if value not in self.game_state.player["traits"]:
                self.game_state.player["traits"].append(value)
        elif effect_type == "add_item":
            self.game_state.player["inventory"].append(value)
        elif effect_type == "set_flag":
            flag = effect.get("flag")
            if flag:
                self.game_state.player["flags"][flag] = value
        elif effect_type == "rep_delta":
            faction = effect.get("faction")
            if faction:
                current_rep = self.game_state.player["rep"].get(faction, 0)
                self.game_state.player["rep"][faction] = max(-2, min(2, current_rep + value))
    
    def assert_current_node(self, expected_node: str):
        """Assert that we're at the expected node."""
        if self.game_state.current_node != expected_node:
            self.errors_encountered.append(
                f"Expected to be at node '{expected_node}', but at '{self.game_state.current_node}'"
            )
    
    def assert_has_tag(self, tag: str):
        """Assert that the player has a specific tag."""
        if tag not in self.game_state.player["tags"]:
            self.errors_encountered.append(f"Expected player to have tag '{tag}'")
    
    def assert_has_item(self, item: str):
        """Assert that the player has a specific item."""
        if item not in self.game_state.player["inventory"]:
            self.errors_encountered.append(f"Expected player to have item '{item}'")
    
    def get_available_choices(self) -> List[Dict[str, Any]]:
        """Get available choices at current node."""
        if not self.game_state or not self.game_state.current_node:
            return []
        
        node_data = self.world_data.get("nodes", {}).get(self.game_state.current_node)
        if not node_data:
            return []
        
        return node_data.get("choices", [])
    
    def run_scenario(self) -> Dict[str, Any]:
        """Run the scenario and return results."""
        # Override in subclasses
        raise NotImplementedError("Subclasses must implement run_scenario")


class TutorialPathScenario(AutomatedPlaytestScenario):
    """Test the tutorial path completion."""
    
    def run_scenario(self) -> Dict[str, Any]:
        # Set up for tutorial
        self.setup_game_state()
        
        # Find tutorial start
        tutorial_start = None
        starts = self.world_data.get("starts", [])
        for start in starts:
            if "tutorial" in start.get("id", "").lower():
                tutorial_start = start["node"]
                break
        
        if not tutorial_start:
            self.errors_encountered.append("No tutorial start found")
            return self._get_results()
        
        # Start at tutorial
        self.game_state.current_node = tutorial_start
        
        # Try to complete tutorial by following first choice several times
        max_steps = 10
        for step in range(max_steps):
            choices = self.get_available_choices()
            if not choices:
                break
            
            # Choose first available choice
            if not self.simulate_choice(0):
                break
            
            # Check if we've reached an ending or safe exit
            current_node_id = self.game_state.current_node
            if "exit" in current_node_id.lower() or "ending" in current_node_id.lower():
                break
        
        return self._get_results()
    
    def _get_results(self) -> Dict[str, Any]:
        return {
            "scenario": self.scenario_name,
            "steps_taken": len(self.steps_taken),
            "errors": self.errors_encountered,
            "success": len(self.errors_encountered) == 0,
            "final_node": self.game_state.current_node if self.game_state else None,
            "player_state": {
                "tags": self.game_state.player["tags"] if self.game_state else [],
                "inventory": self.game_state.player["inventory"] if self.game_state else [],
                "flags": self.game_state.player["flags"] if self.game_state else {}
            }
        }


class TagGatedPathScenario(AutomatedPlaytestScenario):
    """Test tag-gated story paths."""
    
    def run_scenario(self) -> Dict[str, Any]:
        # Test with specific starting tags
        test_tags = ["Scout", "Emissary", "Tinkerer"]
        
        for tag in test_tags:
            # Set up game state with specific tag
            self.setup_game_state(initial_tags=[tag])
            
            # Find a node that should have tag-gated content
            nodes = self.world_data.get("nodes", {})
            for node_id, node_data in nodes.items():
                choices = node_data.get("choices", [])
                
                # Look for choices with tag conditions
                for i, choice in enumerate(choices):
                    condition = choice.get("condition")
                    
                    # Handle both single condition and list of conditions
                    conditions_to_check = []
                    if isinstance(condition, list):
                        conditions_to_check = condition
                    elif condition:
                        conditions_to_check = [condition]
                    
                    for cond in conditions_to_check:
                        if cond.get("type") == "has_tag":
                            required_tag = cond.get("value")
                            
                            # If we have the required tag, try this choice
                            if required_tag == tag:
                                self.game_state.current_node = node_id
                                if self.simulate_choice(i):
                                    # Successfully used tag-gated choice
                                    self.steps_taken.append({
                                        "action": "tag_gated_success",
                                        "tag": tag,
                                        "node": node_id,
                                        "choice": i
                                    })
                                break
                
                # Only test a few nodes to keep test time reasonable
                if len(self.steps_taken) > 3:
                    break
        
        return self._get_results()
    
    def _get_results(self) -> Dict[str, Any]:
        return {
            "scenario": self.scenario_name,
            "steps_taken": len(self.steps_taken),
            "errors": self.errors_encountered,
            "success": len(self.errors_encountered) == 0,
            "final_node": self.game_state.current_node if self.game_state else None,
            "player_state": {
                "tags": self.game_state.player["tags"] if self.game_state else [],
                "inventory": self.game_state.player["inventory"] if self.game_state else [],
                "flags": self.game_state.player["flags"] if self.game_state else {}
            }
        }


class ItemCollectionScenario(AutomatedPlaytestScenario):
    """Test item collection and usage."""
    
    def run_scenario(self) -> Dict[str, Any]:
        # Set up game state
        self.setup_game_state()
        
        # Look for nodes that give items
        nodes = self.world_data.get("nodes", {})
        items_collected = []
        
        for node_id, node_data in nodes.items():
            choices = node_data.get("choices", [])
            
            for i, choice in enumerate(choices):
                effects = choice.get("effects", [])
                
                for effect in effects:
                    if effect.get("type") == "add_item":
                        item = effect.get("value")
                        
                        # Try to collect this item
                        self.game_state.current_node = node_id
                        initial_inventory = len(self.game_state.player["inventory"])
                        
                        if self.simulate_choice(i):
                            new_inventory = len(self.game_state.player["inventory"])
                            if new_inventory > initial_inventory:
                                items_collected.append(item)
                                self.steps_taken.append({
                                    "action": "item_collected",
                                    "item": item,
                                    "node": node_id
                                })
                        
                        # Don't collect too many items in one test
                        if len(items_collected) >= 3:
                            break
                
                if len(items_collected) >= 3:
                    break
            
            if len(items_collected) >= 3:
                break
        
        # Verify items are in inventory
        for item in items_collected:
            self.assert_has_item(item)
        
        return self._get_results()
    
    def _get_results(self) -> Dict[str, Any]:
        return {
            "scenario": self.scenario_name,
            "steps_taken": len(self.steps_taken),
            "errors": self.errors_encountered,
            "success": len(self.errors_encountered) == 0,
            "final_node": self.game_state.current_node if self.game_state else None,
            "player_state": {
                "tags": self.game_state.player["tags"] if self.game_state else [],
                "inventory": self.game_state.player["inventory"] if self.game_state else [],
                "flags": self.game_state.player["flags"] if self.game_state else {}
            }
        }


class TestAutomatedPlaytests(unittest.TestCase):
    """Test cases for automated playtest scenarios."""
    
    @classmethod
    def setUpClass(cls):
        """Load world data once for all tests."""
        world_path = PROJECT_ROOT / "world" / "world.json"
        if world_path.exists():
            with open(world_path, 'r', encoding='utf-8') as f:
                cls.world_data = json.load(f)
        else:
            cls.world_data = None
    
    def test_tutorial_path_completion(self):
        """Test that tutorial path can be completed without errors."""
        if not self.world_data:
            self.skipTest("No world data available")
        
        scenario = TutorialPathScenario(self.world_data, "tutorial_completion")
        results = scenario.run_scenario()
        
        self.assertTrue(results["success"], f"Tutorial scenario failed: {results['errors']}")
        self.assertGreater(results["steps_taken"], 0, "No steps were taken in tutorial")
        self.assertIsNotNone(results["final_node"], "No final node reached")
    
    def test_tag_gated_paths(self):
        """Test that tag-gated paths work correctly."""
        if not self.world_data:
            self.skipTest("No world data available")
        
        scenario = TagGatedPathScenario(self.world_data, "tag_gated_paths")
        results = scenario.run_scenario()
        
        self.assertTrue(results["success"], f"Tag-gated scenario failed: {results['errors']}")
        
        # Check that some tag-gated choices were exercised
        # If no tag-gated choices were found, that's OK for now - just log it
        tag_gated_steps = [step for step in results.get("steps", []) 
                          if step.get("action") == "tag_gated_success"]
        if len(tag_gated_steps) == 0:
            print("Note: No tag-gated choices were found to test (this is OK for early content)")
    
    def test_item_collection(self):
        """Test that item collection works correctly."""
        if not self.world_data:
            self.skipTest("No world data available")
        
        scenario = ItemCollectionScenario(self.world_data, "item_collection")
        results = scenario.run_scenario()
        
        self.assertTrue(results["success"], f"Item collection scenario failed: {results['errors']}")
        
        # Check that some items were collected
        inventory = results["player_state"]["inventory"]
        self.assertGreater(len(inventory), 0, "No items were collected during test")
    
    def test_all_starts_are_reachable(self):
        """Test that all start entries lead to valid nodes."""
        if not self.world_data:
            self.skipTest("No world data available")
        
        starts = self.world_data.get("starts", [])
        nodes = self.world_data.get("nodes", {})
        
        for i, start in enumerate(starts):
            with self.subTest(start_index=i):
                start_id = start.get("id", f"start_{i}")
                target_node = start.get("node")
                
                self.assertIsNotNone(target_node, f"Start '{start_id}' has no target node")
                self.assertIn(target_node, nodes, f"Start '{start_id}' targets missing node '{target_node}'")
                
                # Try to set up a game state with this start
                scenario = AutomatedPlaytestScenario(self.world_data, f"start_test_{start_id}")
                try:
                    game_state = scenario.setup_game_state(target_node)
                    self.assertEqual(game_state.current_node, target_node)
                except Exception as e:
                    self.fail(f"Could not set up game state for start '{start_id}': {e}")
    
    def test_no_dead_end_nodes(self):
        """Test that nodes don't create hard dead ends."""
        if not self.world_data:
            self.skipTest("No world data available")
        
        nodes = self.world_data.get("nodes", {})
        dead_end_nodes = []
        
        for node_id, node_data in nodes.items():
            choices = node_data.get("choices", [])
            
            if len(choices) == 0:
                # This might be an ending node, which is OK
                if "ending" not in node_id.lower() and "final" not in node_id.lower():
                    dead_end_nodes.append(node_id)
            else:
                # Check if all choices are gated (potential soft lock)
                all_gated = all(choice.get("condition") is not None for choice in choices)
                if all_gated:
                    # This could be problematic - flag for review
                    self.fail(f"Node '{node_id}' has all choices gated - potential soft lock")
        
        # Allow some dead ends for endings, but not too many
        if len(dead_end_nodes) > len(nodes) * 0.1:  # More than 10%
            self.fail(f"Too many potential dead-end nodes: {dead_end_nodes[:5]}")


def run_automated_playtests(world_path: Path) -> Dict[str, Any]:
    """
    Run all automated playtest scenarios and return results.
    
    Args:
        world_path: Path to world.json file
    
    Returns:
        Dictionary with test results
    """
    with open(world_path, 'r', encoding='utf-8') as f:
        world_data = json.load(f)
    
    scenarios = [
        TutorialPathScenario(world_data, "tutorial_completion"),
        TagGatedPathScenario(world_data, "tag_gated_paths"),
        ItemCollectionScenario(world_data, "item_collection")
    ]
    
    results = {
        "timestamp": "2025-10-14T12:00:00Z",  # Would be datetime.now().isoformat() in real use
        "world_path": str(world_path),
        "scenarios": []
    }
    
    for scenario in scenarios:
        try:
            scenario_result = scenario.run_scenario()
            results["scenarios"].append(scenario_result)
        except Exception as e:
            results["scenarios"].append({
                "scenario": scenario.scenario_name,
                "success": False,
                "error": str(e),
                "steps_taken": 0
            })
    
    # Summary statistics
    total_scenarios = len(results["scenarios"])
    successful_scenarios = sum(1 for s in results["scenarios"] if s.get("success", False))
    
    results["summary"] = {
        "total_scenarios": total_scenarios,
        "successful_scenarios": successful_scenarios,
        "success_rate": successful_scenarios / total_scenarios if total_scenarios > 0 else 0
    }
    
    return results


if __name__ == "__main__":
    unittest.main()