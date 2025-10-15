#!/usr/bin/env python3
"""
Tests for profile management system.
"""

import unittest
import sys
import tempfile
import json
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "engine"))

from profile_manager import ProfileManager

class TestProfileManager(unittest.TestCase):
    """Test profile management functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create temporary directory for test profiles
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = ProfileManager(self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        if self.temp_dir.exists():
            shutil.rmtree(self.temp_dir)
    
    def test_profile_creation(self):
        """Test creating new player profiles."""
        profile_path = self.manager.create_profile("test_player")
        
        self.assertIsNotNone(profile_path)
        self.assertTrue(profile_path.exists())
        self.assertEqual(profile_path.name, "test_player.json")
    
    def test_profile_listing(self):
        """Test listing profiles."""
        # Create a few profiles
        self.manager.create_profile("player_one")
        self.manager.create_profile("player_two")
        
        profiles = self.manager.list_profiles()
        self.assertEqual(len(profiles), 2)
        
        # Check profile names
        profile_names = [p["name"] for p in profiles]
        self.assertIn("player_one", profile_names)
        self.assertIn("player_two", profile_names)
    
    def test_profile_deletion(self):
        """Test deleting profiles."""
        self.manager.create_profile("test_player")
        
        # Delete profile
        success = self.manager.delete_profile("test_player")
        self.assertTrue(success)
        
        # Should not exist anymore
        profiles = self.manager.list_profiles()
        self.assertEqual(len(profiles), 0)
    
    def test_profile_loading(self):
        """Test loading profile data."""
        self.manager.create_profile("test_player")
        
        # Load profile data
        data = self.manager.load_profile_data("test_player")
        self.assertIsInstance(data, dict)
        self.assertIn("unlocked_starts", data)
        self.assertIn("legacy_tags", data)


if __name__ == '__main__':
    unittest.main()