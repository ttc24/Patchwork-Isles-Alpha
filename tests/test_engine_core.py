#!/usr/bin/env python3
"""
Tests for core engine functionality.
"""

import unittest
import sys
import json
import tempfile
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "engine"))

from engine_min import GameState, default_profile

class TestGameState(unittest.TestCase):
    """Test GameState functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a minimal test world
        self.test_world = {
            "title": "Test World",
            "factions": ["Test Faction"],
            "advanced_tags": ["Test-Advanced"],
            "starts": [
                {
                    "id": "test_start",
                    "title": "Test Start", 
                    "node": "test_node",
                    "tags": ["Scout"],
                    "blurb": "A test start."
                }
            ],
            "nodes": {
                "test_node": {
                    "id": "test_node",
                    "text": "This is a test node.",
                    "choices": [
                        {
                            "text": "Test choice",
                            "target": "test_node_2"
                        }
                    ]
                },
                "test_node_2": {
                    "id": "test_node_2", 
                    "text": "Second test node.",
                    "choices": []
                }
            }
        }
    
    def test_game_state_creation(self):
        """Test GameState can be created properly."""
        profile = default_profile()
        state = GameState(self.test_world, profile, "test_profile.json")
        self.assertIsNotNone(state)
        self.assertEqual(state.world["title"], "Test World")
    
    def test_player_creation(self):
        """Test player creation from start."""
        profile = default_profile()
        state = GameState(self.test_world, profile, "test_profile.json")
        
        # Test that player dict is initialized
        self.assertIsNotNone(state.player)
        self.assertIn("tags", state.player)
        self.assertIn("traits", state.player)
        self.assertIn("inventory", state.player)
    
    def test_navigation(self):
        """Test node navigation."""
        profile = default_profile()
        state = GameState(self.test_world, profile, "test_profile.json")
        
        # Test setting current node
        state.current_node = "test_node"
        self.assertEqual(state.current_node, "test_node")
        
        # Test navigation to another node
        state.current_node = "test_node_2"
        self.assertEqual(state.current_node, "test_node_2")
    
    def test_tag_operations(self):
        """Test adding and checking tags."""
        profile = default_profile()
        state = GameState(self.test_world, profile, "test_profile.json")
        
        # Add a tag
        state.player["tags"].append("Sneaky")
        self.assertIn("Sneaky", state.player["tags"])
        
        # Add starting tags
        state.player["tags"].append("Scout")
        self.assertIn("Scout", state.player["tags"])


if __name__ == '__main__':
    unittest.main()