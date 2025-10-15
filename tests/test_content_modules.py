#!/usr/bin/env python3
"""
Tests for content module system.
"""

import unittest
import sys
import tempfile
import json
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "engine"))

from content_modules import ContentModuleManager

class TestContentModules(unittest.TestCase):
    """Test content module functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.test_world = {
            "title": "Test World",
            "factions": ["Test Faction"],
            "advanced_tags": ["Test-Tag"],
            "starts": [
                {
                    "id": "tutorial_start",
                    "title": "Tutorial Start",
                    "node": "tutorial_intro",
                    "tags": ["Scout"],
                    "blurb": "Tutorial beginning."
                }
            ],
            "nodes": {
                "tutorial_intro": {
                    "id": "tutorial_intro",
                    "text": "Welcome to the tutorial.",
                    "choices": [
                        {
                            "text": "Continue",
                            "target": "tutorial_next"
                        }
                    ]
                },
                "tutorial_next": {
                    "id": "tutorial_next",
                    "text": "Tutorial continues.",
                    "choices": []
                },
                "dock_arrival": {
                    "id": "dock_arrival",
                    "text": "You arrive at the docks.",
                    "choices": []
                }
            }
        }
        
        # Create temporary directory for test modules
        self.temp_dir = Path(tempfile.mkdtemp())
        self.modules_dir = self.temp_dir / "modules"
        self.modules_dir.mkdir()
        
        self.manager = ContentModuleManager(self.modules_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_module_creation(self):
        """Test creating content modules."""
        modules = self.manager.create_modules_from_world(self.test_world)
        
        self.assertGreater(len(modules), 0)
        self.assertTrue(any(mod.name == "tutorial" for mod in modules))
    
    def test_module_grouping(self):
        """Test that nodes are grouped correctly."""
        modules = self.manager.create_modules_from_world(self.test_world)
        
        tutorial_mod = next((mod for mod in modules if mod.name == "tutorial"), None)
        self.assertIsNotNone(tutorial_mod)
        self.assertIn("tutorial_intro", tutorial_mod.nodes)
        self.assertIn("tutorial_next", tutorial_mod.nodes)
    
    def test_start_assignment(self):
        """Test that starts are assigned to correct modules."""
        modules = self.manager.create_modules_from_world(self.test_world)
        
        tutorial_mod = next((mod for mod in modules if mod.name == "tutorial"), None)
        self.assertIsNotNone(tutorial_mod)
        self.assertEqual(len(tutorial_mod.starts), 1)
        self.assertEqual(tutorial_mod.starts[0]["id"], "tutorial_start")
    
    def test_module_saving_and_loading(self):
        """Test saving and loading modules."""
        modules = self.manager.create_modules_from_world(self.test_world)
        
        # Save modules
        for module in modules:
            self.manager.save_module(module)
        
        # Check files were created
        module_files = list(self.modules_dir.glob("*.json"))
        self.assertGreater(len(module_files), 0)
        
        # Load modules back
        loaded_modules = self.manager.load_all_modules()
        self.assertEqual(len(loaded_modules), len(modules))
        
        # Check content is preserved
        original_tutorial = next((mod for mod in modules if mod.name == "tutorial"), None)
        loaded_tutorial = next((mod for mod in loaded_modules if mod.name == "tutorial"), None)
        
        if original_tutorial and loaded_tutorial:
            self.assertEqual(
                len(original_tutorial.nodes),
                len(loaded_tutorial.nodes)
            )
    
    def test_module_validation(self):
        """Test module validation."""
        modules = self.manager.create_modules_from_world(self.test_world)
        
        for module in modules:
            is_valid, errors = self.manager.validate_module(module)
            self.assertTrue(is_valid, f"Module {module.name} failed validation: {errors}")
    
    def test_world_reconstruction(self):
        """Test reconstructing world from modules."""
        modules = self.manager.create_modules_from_world(self.test_world)
        
        # Save and reload modules
        for module in modules:
            self.manager.save_module(module)
        loaded_modules = self.manager.load_all_modules()
        
        # Reconstruct world
        reconstructed = self.manager.merge_modules_to_world(loaded_modules)
        
        # Check key content is preserved
        self.assertEqual(reconstructed["title"], self.test_world["title"])
        self.assertEqual(len(reconstructed["starts"]), len(self.test_world["starts"]))
        self.assertEqual(len(reconstructed["nodes"]), len(self.test_world["nodes"]))
    
    def test_module_tags_and_metadata(self):
        """Test module tagging and metadata."""
        modules = self.manager.create_modules_from_world(self.test_world)
        
        for module in modules:
            self.assertIsInstance(module.tags, list)
            self.assertIn("created_date", module.metadata)
            self.assertIn("node_count", module.metadata)


if __name__ == '__main__':
    unittest.main()