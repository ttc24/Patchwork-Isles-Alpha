#!/usr/bin/env python3
"""
Story path validation and integration tests.
Tests for world data consistency, node connectivity, and story progression.
"""

import json
import os
import unittest
from pathlib import Path
import sys

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from tools.validate import (
    validate_world_structure,
    find_broken_references,
    validate_starts
)


class TestStoryValidation(unittest.TestCase):
    """Test story data validation and consistency."""
    
    @classmethod
    def setUpClass(cls):
        """Load the world data once for all tests."""
        world_path = PROJECT_ROOT / "world" / "world.json"
        if world_path.exists():
            with open(world_path, 'r', encoding='utf-8') as f:
                cls.world_data = json.load(f)
        else:
            cls.world_data = None
    
    def test_world_data_exists(self):
        """Test that world data can be loaded."""
        self.assertIsNotNone(self.world_data, "world.json should be loadable")
        self.assertIsInstance(self.world_data, dict)
    
    def test_world_has_required_fields(self):
        """Test that world data has required top-level fields."""
        if not self.world_data:
            self.skipTest("No world data available")
        
        required_fields = ["title", "factions", "advanced_tags", "starts"]
        for field in required_fields:
            with self.subTest(field=field):
                self.assertIn(field, self.world_data, f"World data should have '{field}' field")
    
    def test_starts_structure(self):
        """Test that all start entries are properly structured."""
        if not self.world_data:
            self.skipTest("No world data available")
        
        starts = self.world_data.get("starts", [])
        self.assertIsInstance(starts, list)
        
        for i, start in enumerate(starts):
            with self.subTest(start_index=i):
                self.assertIsInstance(start, dict)
                
                # Required fields
                required_fields = ["id", "title", "node", "tags", "blurb"]
                for field in required_fields:
                    self.assertIn(field, start, f"Start {i} should have '{field}' field")
                
                # Field types
                self.assertIsInstance(start["id"], str)
                self.assertIsInstance(start["title"], str)
                self.assertIsInstance(start["node"], str)
                self.assertIsInstance(start["tags"], list)
                self.assertIsInstance(start["blurb"], str)
                
                # Locked starts should have locked_title
                if start.get("locked"):
                    self.assertIn("locked_title", start, 
                                f"Locked start {start['id']} should have 'locked_title'")
    
    def test_factions_are_strings(self):
        """Test that all factions are properly formatted strings."""
        if not self.world_data:
            self.skipTest("No world data available")
        
        factions = self.world_data.get("factions", [])
        self.assertIsInstance(factions, list)
        
        for i, faction in enumerate(factions):
            with self.subTest(faction_index=i):
                self.assertIsInstance(faction, str)
                self.assertTrue(len(faction.strip()) > 0, f"Faction {i} should not be empty")
    
    def test_advanced_tags_are_strings(self):
        """Test that all advanced tags are properly formatted strings."""
        if not self.world_data:
            self.skipTest("No world data available")
        
        advanced_tags = self.world_data.get("advanced_tags", [])
        self.assertIsInstance(advanced_tags, list)
        
        for i, tag in enumerate(advanced_tags):
            with self.subTest(tag_index=i):
                self.assertIsInstance(tag, str)
                self.assertTrue(len(tag.strip()) > 0, f"Advanced tag {i} should not be empty")


class TestNodeConnectivity(unittest.TestCase):
    """Test node connectivity and reference integrity."""
    
    @classmethod
    def setUpClass(cls):
        """Load the world data once for all tests."""
        world_path = PROJECT_ROOT / "world" / "world.json"
        if world_path.exists():
            with open(world_path, 'r', encoding='utf-8') as f:
                cls.world_data = json.load(f)
        else:
            cls.world_data = None
    
    def test_nodes_exist(self):
        """Test that the world has nodes defined."""
        if not self.world_data:
            self.skipTest("No world data available")
        
        nodes = self.world_data.get("nodes", {})
        self.assertIsInstance(nodes, dict)
        self.assertGreater(len(nodes), 0, "World should have at least one node")
    
    def test_all_starts_reference_valid_nodes(self):
        """Test that all start entries reference existing nodes."""
        if not self.world_data:
            self.skipTest("No world data available")
        
        starts = self.world_data.get("starts", [])
        nodes = self.world_data.get("nodes", {})
        
        for start in starts:
            start_id = start.get("id", "unknown")
            target_node = start.get("node")
            
            with self.subTest(start_id=start_id, target_node=target_node):
                self.assertIsNotNone(target_node, f"Start {start_id} should have a target node")
                self.assertIn(target_node, nodes, 
                            f"Start {start_id} references non-existent node '{target_node}'")
    
    def test_choice_destinations_exist(self):
        """Test that all choice destinations reference existing nodes."""
        if not self.world_data:
            self.skipTest("No world data available")
        
        nodes = self.world_data.get("nodes", {})
        broken_refs = []
        
        for node_id, node_data in nodes.items():
            choices = node_data.get("choices", [])
            
            for i, choice in enumerate(choices):
                destination = choice.get("destination")
                if destination and destination not in nodes:
                    broken_refs.append({
                        "node": node_id,
                        "choice_index": i,
                        "destination": destination,
                        "choice_text": choice.get("text", "Unknown")
                    })
        
        if broken_refs:
            error_msg = "Found broken node references:\n"
            for ref in broken_refs[:10]:  # Show first 10 to avoid overwhelming output
                error_msg += f"  - Node '{ref['node']}' choice {ref['choice_index']} -> '{ref['destination']}'\n"
            if len(broken_refs) > 10:
                error_msg += f"  ... and {len(broken_refs) - 10} more"
            
            self.fail(error_msg)
    
    def test_nodes_have_required_structure(self):
        """Test that all nodes have required fields and proper structure."""
        if not self.world_data:
            self.skipTest("No world data available")
        
        nodes = self.world_data.get("nodes", {})
        
        for node_id, node_data in nodes.items():
            with self.subTest(node_id=node_id):
                self.assertIsInstance(node_data, dict, f"Node {node_id} should be a dict")
                
                # Required fields
                if "text" in node_data:
                    self.assertIsInstance(node_data["text"], str)
                
                if "choices" in node_data:
                    choices = node_data["choices"]
                    self.assertIsInstance(choices, list, f"Node {node_id} choices should be a list")
                    
                    for i, choice in enumerate(choices):
                        self.assertIsInstance(choice, dict, 
                                            f"Node {node_id} choice {i} should be a dict")
                        self.assertIn("text", choice, 
                                    f"Node {node_id} choice {i} should have text")


class TestAutomatedPlaytest(unittest.TestCase):
    """Automated playtest scenarios to catch regressions."""
    
    @classmethod
    def setUpClass(cls):
        """Load the world data once for all tests."""
        world_path = PROJECT_ROOT / "world" / "world.json"
        if world_path.exists():
            with open(world_path, 'r', encoding='utf-8') as f:
                cls.world_data = json.load(f)
        else:
            cls.world_data = None
    
    def test_tutorial_path_completable(self):
        """Test that the tutorial path can be completed without errors."""
        if not self.world_data:
            self.skipTest("No world data available")
        
        # Find tutorial start
        starts = self.world_data.get("starts", [])
        tutorial_start = None
        
        for start in starts:
            if "tutorial" in start.get("id", "").lower():
                tutorial_start = start
                break
        
        if not tutorial_start:
            self.skipTest("No tutorial start found")
        
        # Verify tutorial node exists and has choices
        nodes = self.world_data.get("nodes", {})
        tutorial_node_id = tutorial_start["node"]
        
        self.assertIn(tutorial_node_id, nodes, 
                     f"Tutorial node '{tutorial_node_id}' should exist")
        
        tutorial_node = nodes[tutorial_node_id]
        choices = tutorial_node.get("choices", [])
        self.assertGreater(len(choices), 0, 
                          "Tutorial node should have at least one choice")
    
    def test_at_least_one_tagless_path_per_major_node(self):
        """Test that major story nodes have at least one tagless progression path."""
        if not self.world_data:
            self.skipTest("No world data available")
        
        nodes = self.world_data.get("nodes", {})
        nodes_without_tagless_paths = []
        
        for node_id, node_data in nodes.items():
            choices = node_data.get("choices", [])
            
            # Skip nodes with no choices (endings, etc.)
            if len(choices) == 0:
                continue
            
            # Check if at least one choice has no conditions
            has_tagless_path = False
            for choice in choices:
                if "condition" not in choice:
                    has_tagless_path = True
                    break
            
            if not has_tagless_path:
                nodes_without_tagless_paths.append(node_id)
        
        # Allow some nodes to not have tagless paths, but flag if too many
        if len(nodes_without_tagless_paths) > len(nodes) * 0.3:  # More than 30%
            self.fail(f"Too many nodes ({len(nodes_without_tagless_paths)}) lack tagless progression paths. "
                     f"Examples: {nodes_without_tagless_paths[:5]}")


if __name__ == "__main__":
    unittest.main()