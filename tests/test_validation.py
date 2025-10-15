#!/usr/bin/env python3
"""
Tests for validation systems.
"""

import unittest
import sys
import json
import tempfile
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "engine"))

from schema_validator import WorldValidator

class TestSchemaValidation(unittest.TestCase):
    """Test schema validation functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.valid_world = {
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
                    "text": "Test node text.",
                    "choices": [
                        {
                            "text": "Test choice",
                            "target": "test_node"
                        }
                    ]
                }
            }
        }
        
        self.validator = WorldValidator()
    
    def test_valid_world_passes(self):
        """Test that a valid world passes validation."""
        is_valid, errors = self.validator.validate_world_data(self.valid_world)
        self.assertTrue(is_valid, f"Valid world failed validation: {errors}")
    
    def test_missing_required_field(self):
        """Test that missing required fields are caught."""
        invalid_world = self.valid_world.copy()
        del invalid_world["title"]
        
        is_valid, errors = self.validator.validate_world_data(invalid_world)
        self.assertFalse(is_valid)
        self.assertTrue(any("title" in error for error in errors))
    
    def test_invalid_start_structure(self):
        """Test that invalid start structures are caught."""
        invalid_world = self.valid_world.copy()
        invalid_world["starts"] = [
            {
                "id": "bad_start",
                # Missing required fields
            }
        ]
        
        is_valid, errors = self.validator.validate_world_data(invalid_world)
        self.assertFalse(is_valid)
    
    def test_node_reference_validation(self):
        """Test node reference validation."""
        is_valid, errors = self.validator.validate_node_references(self.valid_world)
        self.assertTrue(is_valid, f"Node reference validation failed: {errors}")
        
        # Test with invalid reference
        invalid_world = self.valid_world.copy()
        invalid_world["starts"][0]["node"] = "nonexistent_node"
        
        is_valid, errors = self.validator.validate_node_references(invalid_world)
        self.assertFalse(is_valid)
        self.assertTrue(any("nonexistent_node" in error for error in errors))
    
    def test_faction_reference_validation(self):
        """Test faction reference validation."""
        is_valid, errors = self.validator.validate_faction_references(self.valid_world)
        self.assertTrue(is_valid)
        
        # Test with invalid faction reference
        invalid_world = self.valid_world.copy()
        invalid_world["nodes"]["test_node"]["choices"][0]["condition"] = {
            "type": "rep_at_least",
            "faction": "Nonexistent Faction",
            "value": 1
        }
        
        is_valid, errors = self.validator.validate_faction_references(invalid_world)
        self.assertFalse(is_valid)
        self.assertTrue(any("Nonexistent Faction" in error for error in errors))
    
    def test_full_validation(self):
        """Test comprehensive validation."""
        is_valid, errors = self.validator.full_validation(self.valid_world)
        self.assertTrue(is_valid, f"Full validation failed: {errors}")
    
    def test_world_file_validation(self):
        """Test validation of world file on disk."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json.dump(self.valid_world, f, indent=2)
            temp_file = Path(f.name)
        
        try:
            is_valid, errors = self.validator.validate_world_file(temp_file)
            self.assertTrue(is_valid, f"World file validation failed: {errors}")
        finally:
            temp_file.unlink()
    
    def test_malformed_json_file(self):
        """Test handling of malformed JSON files."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write("{ invalid json }")
            temp_file = Path(f.name)
        
        try:
            is_valid, errors = self.validator.validate_world_file(temp_file)
            self.assertFalse(is_valid)
            self.assertTrue(any("JSON" in error for error in errors))
        finally:
            temp_file.unlink()


if __name__ == '__main__':
    unittest.main()