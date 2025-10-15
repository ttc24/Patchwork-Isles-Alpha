#!/usr/bin/env python3
"""
Unit tests for the core game engine functionality.
"""

import json
import os
import tempfile
import unittest
from pathlib import Path
import sys

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engine.engine_min import (
    GameState, 
    canonical_tag, 
    canonicalize_tag_list, 
    compute_line_width,
    default_profile,
    load_profile,
    save_profile
)
from engine.settings import Settings


class TestEngineCore(unittest.TestCase):
    """Test core engine functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_world = {
            "title": "Test World",
            "factions": ["Test Faction"],
            "advanced_tags": ["Test-Tag"],
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
                    "text": "You are in a test location.",
                    "choices": [
                        {
                            "text": "Test choice",
                            "destination": "test_node"
                        }
                    ]
                }
            }
        }
        
        self.temp_dir = tempfile.mkdtemp()
        self.test_profile_path = os.path.join(self.temp_dir, "test_profile.json")
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up temporary files
        if os.path.exists(self.test_profile_path):
            os.remove(self.test_profile_path)
        os.rmdir(self.temp_dir)
    
    def test_canonical_tag(self):
        """Test tag canonicalization."""
        self.assertEqual(canonical_tag("Diplomat"), "Emissary")
        self.assertEqual(canonical_tag("Emissary"), "Emissary")
        self.assertEqual(canonical_tag("Judge"), "Arbiter")
        self.assertEqual(canonical_tag("Arbiter"), "Arbiter")
        self.assertEqual(canonical_tag("Scout"), "Scout")  # No alias
    
    def test_canonicalize_tag_list(self):
        """Test tag list canonicalization and deduplication."""
        tags = ["Diplomat", "Judge", "Scout", "Emissary"]
        result = canonicalize_tag_list(tags)
        # Should deduplicate Diplomat->Emissary and Judge->Arbiter
        self.assertEqual(set(result), {"Emissary", "Arbiter", "Scout"})
        self.assertEqual(len(result), 3)  # No duplicates
    
    def test_compute_line_width(self):
        """Test line width computation with different UI scales."""
        settings = Settings()
        settings.ui_scale = 1.0
        self.assertEqual(compute_line_width(settings), 80)
        
        settings.ui_scale = 1.5
        self.assertEqual(compute_line_width(settings), 120)  # Capped at MAX_LINE_WIDTH
        
        settings.ui_scale = 0.5
        self.assertEqual(compute_line_width(settings), 50)  # Capped at MIN_LINE_WIDTH
    
    def test_default_profile(self):
        """Test default profile creation."""
        profile = default_profile()
        expected_keys = ["unlocked_starts", "legacy_tags", "seen_endings", "flags"]
        for key in expected_keys:
            self.assertIn(key, profile)
            self.assertEqual(profile[key], [] if key != "flags" else {})
    
    def test_save_load_profile(self):
        """Test profile save/load functionality."""
        test_profile = {
            "unlocked_starts": ["test_start"],
            "legacy_tags": ["Scout"],
            "seen_endings": ["test_ending"],
            "flags": {"test_flag": True}
        }
        
        save_profile(test_profile, self.test_profile_path)
        self.assertTrue(os.path.exists(self.test_profile_path))
        
        loaded_profile = load_profile(self.test_profile_path)
        self.assertEqual(loaded_profile, test_profile)
    
    def test_game_state_initialization(self):
        """Test GameState initialization."""
        profile = default_profile()
        settings = Settings()
        
        state = GameState(
            self.test_world, 
            profile, 
            self.test_profile_path, 
            settings
        )
        
        self.assertEqual(state.world, self.test_world)
        self.assertEqual(state.profile, profile)
        self.assertIsNotNone(state.player)
        self.assertIn("tags", state.player)
        self.assertIn("hp", state.player)
        self.assertIn("rep", state.player)
    
    def test_game_state_rep_str(self):
        """Test reputation string formatting."""
        profile = default_profile()
        settings = Settings()
        
        state = GameState(
            self.test_world, 
            profile, 
            self.test_profile_path, 
            settings
        )
        
        # Empty rep should return dash
        self.assertEqual(state.rep_str(), "—")
        
        # With reputation
        state.player["rep"] = {"Test Faction": 1, "Another Faction": -1}
        rep_str = state.rep_str()
        self.assertIn("Test Faction:1", rep_str)
        self.assertIn("Another Faction:-1", rep_str)


class TestGameStateConsistency(unittest.TestCase):
    """Test GameState consistency and validation."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_world = {
            "title": "Test World",
            "factions": ["Test Faction"],
            "advanced_tags": ["Test-Tag"],
            "starts": [],
            "nodes": {}
        }
        self.temp_dir = tempfile.mkdtemp()
        self.test_profile_path = os.path.join(self.temp_dir, "test_profile.json")
    
    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.test_profile_path):
            os.remove(self.test_profile_path)
        os.rmdir(self.temp_dir)
    
    def test_ensure_consistency_basic(self):
        """Test basic consistency enforcement."""
        profile = default_profile()
        settings = Settings()
        
        state = GameState(
            self.test_world, 
            profile, 
            self.test_profile_path, 
            settings
        )
        
        # Should not raise any exceptions
        state.ensure_consistency()
        
        # Basic player structure should be intact
        self.assertIsInstance(state.player["tags"], list)
        self.assertIsInstance(state.player["traits"], list)
        self.assertIsInstance(state.player["inventory"], list)
        self.assertIsInstance(state.player["flags"], dict)
        self.assertIsInstance(state.player["rep"], dict)


if __name__ == "__main__":
    unittest.main()