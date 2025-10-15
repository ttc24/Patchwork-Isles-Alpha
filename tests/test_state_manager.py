#!/usr/bin/env python3
"""
Tests for state management system.
"""

import unittest
import sys
from pathlib import Path

# Add project paths
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "engine"))

from state_manager import StateManager, PlayerState, GameSession

class TestStateManager(unittest.TestCase):
    """Test state management functionality."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.state_manager = StateManager()
        
        # Create test player state
        self.test_player = PlayerState(
            name="Test Player",
            current_node="test_node",
            tags=["Scout", "Sneaky"],
            traits=["Quick"],
            items=["rope"],
            reputation={"Test Faction": 2}
        )
    
    def test_player_state_creation(self):
        """Test PlayerState creation and basic functionality."""
        self.assertEqual(self.test_player.name, "Test Player")
        self.assertEqual(self.test_player.current_node, "test_node")
        self.assertIn("Scout", self.test_player.tags)
    
    def test_player_state_validation(self):
        """Test PlayerState validation."""
        # Valid state should pass
        self.assertTrue(self.test_player.validate())
        
        # Invalid state should fail
        invalid_player = PlayerState(name="", current_node="")
        self.assertFalse(invalid_player.validate())
    
    def test_session_creation(self):
        """Test GameSession creation."""
        session = GameSession(
            player=self.test_player,
            session_id="test_session"
        )
        
        self.assertEqual(session.player, self.test_player)
        self.assertEqual(session.session_id, "test_session")
        self.assertIsNotNone(session.start_time)
    
    def test_state_manager_session_management(self):
        """Test StateManager session operations."""
        session = self.state_manager.create_session(
            player=self.test_player,
            session_id="test_session"
        )
        
        self.assertIsNotNone(session)
        self.assertEqual(session.player, self.test_player)
        
        # Test getting session
        retrieved = self.state_manager.get_session("test_session")
        self.assertEqual(retrieved, session)
    
    def test_state_snapshots(self):
        """Test state snapshot functionality."""
        session = self.state_manager.create_session(
            player=self.test_player,
            session_id="test_session"
        )
        
        # Create snapshot
        snapshot_id = self.state_manager.create_snapshot("test_session", "before_choice")
        self.assertIsNotNone(snapshot_id)
        
        # Modify state
        session.player.tags.append("Diplomat")
        
        # Restore snapshot
        restored = self.state_manager.restore_snapshot("test_session", snapshot_id)
        self.assertTrue(restored)
        
        # State should be restored
        self.assertNotIn("Diplomat", session.player.tags)
    
    def test_event_handling(self):
        """Test event system."""
        events_received = []
        
        def event_handler(event_type, session_id, data):
            events_received.append((event_type, session_id, data))
        
        self.state_manager.add_event_listener("tag_added", event_handler)
        
        # Trigger event
        session = self.state_manager.create_session(
            player=self.test_player,
            session_id="test_session"
        )
        
        self.state_manager.fire_event("tag_added", "test_session", {"tag": "NewTag"})
        
        # Check event was received
        self.assertEqual(len(events_received), 1)
        self.assertEqual(events_received[0][0], "tag_added")
    
    def test_state_persistence(self):
        """Test state serialization and deserialization."""
        session = self.state_manager.create_session(
            player=self.test_player,
            session_id="test_session"
        )
        
        # Serialize state
        serialized = self.state_manager.serialize_session("test_session")
        self.assertIsNotNone(serialized)
        
        # Deserialize state
        deserialized_session = self.state_manager.deserialize_session(serialized)
        self.assertIsNotNone(deserialized_session)
        
        # Check data integrity
        self.assertEqual(deserialized_session.player.name, self.test_player.name)
        self.assertEqual(deserialized_session.player.current_node, self.test_player.current_node)
    
    def test_history_tracking(self):
        """Test session history functionality."""
        session = self.state_manager.create_session(
            player=self.test_player,
            session_id="test_session"
        )
        
        # Add some history
        self.state_manager.add_to_history("test_session", {
            "action": "choice_made",
            "choice_text": "Go north",
            "target": "north_path"
        })
        
        history = self.state_manager.get_session_history("test_session")
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["action"], "choice_made")
    
    def test_state_validation_comprehensive(self):
        """Test comprehensive state validation."""
        session = self.state_manager.create_session(
            player=self.test_player,
            session_id="test_session"
        )
        
        # Valid session should pass validation
        is_valid, errors = self.state_manager.validate_session("test_session")
        self.assertTrue(is_valid, f"Session validation failed: {errors}")


class TestPlayerState(unittest.TestCase):
    """Specific tests for PlayerState class."""
    
    def test_tag_operations(self):
        """Test tag manipulation methods."""
        player = PlayerState(name="Test", current_node="test")
        
        # Test adding tags
        player.add_tag("Scout")
        self.assertIn("Scout", player.tags)
        
        # Test duplicate prevention
        player.add_tag("Scout")
        self.assertEqual(player.tags.count("Scout"), 1)
        
        # Test tag checking
        self.assertTrue(player.has_tag("Scout"))
        self.assertFalse(player.has_tag("Nonexistent"))
    
    def test_reputation_operations(self):
        """Test reputation manipulation methods."""
        player = PlayerState(name="Test", current_node="test")
        
        # Test setting reputation
        player.set_reputation("Test Faction", 3)
        self.assertEqual(player.get_reputation("Test Faction"), 3)
        
        # Test reputation delta
        player.modify_reputation("Test Faction", 2)
        self.assertEqual(player.get_reputation("Test Faction"), 5)
        
        # Test new faction
        player.modify_reputation("New Faction", 1)
        self.assertEqual(player.get_reputation("New Faction"), 1)
    
    def test_inventory_operations(self):
        """Test item/inventory operations."""
        player = PlayerState(name="Test", current_node="test")
        
        # Test adding items
        player.add_item("sword")
        self.assertIn("sword", player.items)
        
        # Test removing items
        player.remove_item("sword")
        self.assertNotIn("sword", player.items)
        
        # Test has_item
        player.add_item("key")
        self.assertTrue(player.has_item("key"))
        self.assertFalse(player.has_item("nonexistent"))


if __name__ == '__main__':
    unittest.main()