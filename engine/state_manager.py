#!/usr/bin/env python3
"""
Enhanced state management system for Patchwork Isles.
Provides better separation of concerns and more robust state handling.
"""

import logging
from typing import Dict, Any, Optional, List, Callable
from dataclasses import dataclass, field
from copy import deepcopy

logger = logging.getLogger("patchwork_isles.state_manager")


@dataclass
class PlayerState:
    """Represents the player's current state."""
    name: Optional[str] = None
    hp: int = 10
    tags: List[str] = field(default_factory=list)
    traits: List[str] = field(default_factory=list)
    inventory: List[str] = field(default_factory=list)
    resources: Dict[str, int] = field(default_factory=dict)
    flags: Dict[str, Any] = field(default_factory=dict)
    rep: Dict[str, int] = field(default_factory=dict)  # faction -> reputation (-2 to +2)
    
    def copy(self) -> 'PlayerState':
        """Create a deep copy of the player state."""
        return PlayerState(
            name=self.name,
            hp=self.hp,
            tags=self.tags.copy(),
            traits=self.traits.copy(),
            inventory=self.inventory.copy(),
            resources=self.resources.copy(),
            flags=self.flags.copy(),
            rep=self.rep.copy()
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "hp": self.hp,
            "tags": self.tags,
            "traits": self.traits,
            "inventory": self.inventory,
            "resources": self.resources,
            "flags": self.flags,
            "rep": self.rep
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'PlayerState':
        """Create from dictionary."""
        return cls(
            name=data.get("name"),
            hp=data.get("hp", 10),
            tags=data.get("tags", []),
            traits=data.get("traits", []),
            inventory=data.get("inventory", []),
            resources=data.get("resources", {}),
            flags=data.get("flags", {}),
            rep=data.get("rep", {})
        )


@dataclass 
class GameSession:
    """Represents the current game session state."""
    current_node: Optional[str] = None
    start_id: Optional[str] = None
    world_seed: int = 0
    active_area: str = "Unknown"
    choices_made: Dict[str, List[str]] = field(default_factory=dict)
    session_flags: Dict[str, Any] = field(default_factory=dict)
    
    def copy(self) -> 'GameSession':
        """Create a deep copy of the session state."""
        return GameSession(
            current_node=self.current_node,
            start_id=self.start_id,
            world_seed=self.world_seed,
            active_area=self.active_area,
            choices_made=deepcopy(self.choices_made),
            session_flags=deepcopy(self.session_flags)
        )
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "current_node": self.current_node,
            "start_id": self.start_id,
            "world_seed": self.world_seed,
            "active_area": self.active_area,
            "choices_made": self.choices_made,
            "session_flags": self.session_flags
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameSession':
        """Create from dictionary."""
        return cls(
            current_node=data.get("current_node"),
            start_id=data.get("start_id"),
            world_seed=data.get("world_seed", 0),
            active_area=data.get("active_area", "Unknown"),
            choices_made=data.get("choices_made", {}),
            session_flags=data.get("session_flags", {})
        )


@dataclass
class GameHistory:
    """Manages game history and navigation."""
    entries: List[Dict[str, Any]] = field(default_factory=list)
    max_entries: int = 1000
    
    def add_entry(self, entry_type: str, data: Dict[str, Any]):
        """Add a history entry."""
        entry = {
            "type": entry_type,
            "timestamp": "auto",  # Would be datetime.now().isoformat() in real use
            "data": data
        }
        
        self.entries.append(entry)
        
        # Limit history size
        if len(self.entries) > self.max_entries:
            self.entries = self.entries[-self.max_entries:]
    
    def get_recent_entries(self, count: int = 10) -> List[Dict[str, Any]]:
        """Get recent history entries."""
        return self.entries[-count:] if self.entries else []
    
    def clear(self):
        """Clear all history."""
        self.entries.clear()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "entries": self.entries,
            "max_entries": self.max_entries
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GameHistory':
        """Create from dictionary."""
        history = cls()
        history.entries = data.get("entries", [])
        history.max_entries = data.get("max_entries", 1000)
        return history


class StateChangeEvent:
    """Represents a state change event."""
    
    def __init__(self, event_type: str, old_value: Any, new_value: Any, context: Dict[str, Any] = None):
        self.event_type = event_type
        self.old_value = old_value
        self.new_value = new_value
        self.context = context or {}


class StateManager:
    """Advanced state management with validation, history, and event handling."""
    
    def __init__(self):
        self.player_state = PlayerState()
        self.session_state = GameSession()
        self.history = GameHistory()
        self.state_snapshots = []  # For undo/rollback functionality
        self.max_snapshots = 50
        
        # Event handlers for state changes
        self.event_handlers: Dict[str, List[Callable]] = {}
        
        # State validators
        self.validators: Dict[str, List[Callable]] = {}
    
    def add_event_handler(self, event_type: str, handler: Callable):
        """Add an event handler for state changes."""
        if event_type not in self.event_handlers:
            self.event_handlers[event_type] = []
        self.event_handlers[event_type].append(handler)
    
    def add_validator(self, field_name: str, validator: Callable):
        """Add a validator for a specific field."""
        if field_name not in self.validators:
            self.validators[field_name] = []
        self.validators[field_name].append(validator)
    
    def _fire_event(self, event: StateChangeEvent):
        """Fire state change event to all registered handlers."""
        handlers = self.event_handlers.get(event.event_type, [])
        for handler in handlers:
            try:
                handler(event)
            except Exception as e:
                logger.error(f"Error in state change handler: {e}")
    
    def _validate_change(self, field_name: str, old_value: Any, new_value: Any) -> bool:
        """Validate a state change."""
        validators = self.validators.get(field_name, [])
        for validator in validators:
            try:
                if not validator(old_value, new_value):
                    logger.warning(f"State validation failed for {field_name}")
                    return False
            except Exception as e:
                logger.error(f"Error in state validator: {e}")
                return False
        return True
    
    def create_snapshot(self):
        """Create a snapshot of the current state for rollback."""
        snapshot = {
            "player": self.player_state.copy(),
            "session": self.session_state.copy(),
            "timestamp": "auto"  # Would be datetime.now().isoformat() in real use
        }
        
        self.state_snapshots.append(snapshot)
        
        # Limit snapshot count
        if len(self.state_snapshots) > self.max_snapshots:
            self.state_snapshots = self.state_snapshots[-self.max_snapshots:]
    
    def restore_snapshot(self, index: int = -1) -> bool:
        """Restore state from a snapshot."""
        if not self.state_snapshots:
            logger.warning("No snapshots available for restore")
            return False
        
        if abs(index) > len(self.state_snapshots):
            logger.warning("Invalid snapshot index")
            return False
        
        snapshot = self.state_snapshots[index]
        self.player_state = snapshot["player"].copy()
        self.session_state = snapshot["session"].copy()
        
        logger.info(f"State restored from snapshot {index}")
        return True
    
    def update_player_state(self, **updates):
        """Update player state with validation and events."""
        for field_name, new_value in updates.items():
            if not hasattr(self.player_state, field_name):
                logger.warning(f"Unknown player state field: {field_name}")
                continue
            
            old_value = getattr(self.player_state, field_name)
            
            if self._validate_change(f"player.{field_name}", old_value, new_value):
                setattr(self.player_state, field_name, new_value)
                
                # Fire event
                event = StateChangeEvent(
                    f"player.{field_name}_changed",
                    old_value,
                    new_value,
                    {"field": field_name}
                )
                self._fire_event(event)
                
                # Add to history
                self.history.add_entry("player_state_change", {
                    "field": field_name,
                    "old_value": old_value,
                    "new_value": new_value
                })
    
    def update_session_state(self, **updates):
        """Update session state with validation and events."""
        for field_name, new_value in updates.items():
            if not hasattr(self.session_state, field_name):
                logger.warning(f"Unknown session state field: {field_name}")
                continue
            
            old_value = getattr(self.session_state, field_name)
            
            if self._validate_change(f"session.{field_name}", old_value, new_value):
                setattr(self.session_state, field_name, new_value)
                
                # Fire event
                event = StateChangeEvent(
                    f"session.{field_name}_changed",
                    old_value,
                    new_value,
                    {"field": field_name}
                )
                self._fire_event(event)
    
    def add_tag(self, tag: str):
        """Add a tag to the player."""
        if tag not in self.player_state.tags:
            old_tags = self.player_state.tags.copy()
            self.player_state.tags.append(tag)
            
            event = StateChangeEvent("player.tag_added", old_tags, self.player_state.tags, {"tag": tag})
            self._fire_event(event)
            
            self.history.add_entry("tag_added", {"tag": tag})
    
    def remove_tag(self, tag: str):
        """Remove a tag from the player."""
        if tag in self.player_state.tags:
            old_tags = self.player_state.tags.copy()
            self.player_state.tags.remove(tag)
            
            event = StateChangeEvent("player.tag_removed", old_tags, self.player_state.tags, {"tag": tag})
            self._fire_event(event)
            
            self.history.add_entry("tag_removed", {"tag": tag})
    
    def add_trait(self, trait: str):
        """Add a trait to the player."""
        if trait not in self.player_state.traits:
            old_traits = self.player_state.traits.copy()
            self.player_state.traits.append(trait)
            
            event = StateChangeEvent("player.trait_added", old_traits, self.player_state.traits, {"trait": trait})
            self._fire_event(event)
            
            self.history.add_entry("trait_added", {"trait": trait})
    
    def add_item(self, item: str):
        """Add an item to inventory."""
        self.player_state.inventory.append(item)
        
        event = StateChangeEvent("player.item_added", None, item, {"item": item})
        self._fire_event(event)
        
        self.history.add_entry("item_added", {"item": item})
    
    def remove_item(self, item: str) -> bool:
        """Remove an item from inventory."""
        if item in self.player_state.inventory:
            self.player_state.inventory.remove(item)
            
            event = StateChangeEvent("player.item_removed", item, None, {"item": item})
            self._fire_event(event)
            
            self.history.add_entry("item_removed", {"item": item})
            return True
        return False
    
    def set_flag(self, flag: str, value: Any):
        """Set a flag value."""
        old_value = self.player_state.flags.get(flag)
        self.player_state.flags[flag] = value
        
        event = StateChangeEvent("player.flag_changed", old_value, value, {"flag": flag})
        self._fire_event(event)
        
        self.history.add_entry("flag_set", {"flag": flag, "old_value": old_value, "new_value": value})
    
    def adjust_reputation(self, faction: str, delta: int):
        """Adjust reputation with a faction."""
        old_rep = self.player_state.rep.get(faction, 0)
        new_rep = max(-2, min(2, old_rep + delta))  # Clamp to -2..+2
        
        if new_rep != old_rep:
            self.player_state.rep[faction] = new_rep
            
            event = StateChangeEvent("player.reputation_changed", old_rep, new_rep, 
                                   {"faction": faction, "delta": delta})
            self._fire_event(event)
            
            self.history.add_entry("reputation_changed", {
                "faction": faction,
                "old_rep": old_rep,
                "new_rep": new_rep,
                "delta": delta
            })
    
    def change_node(self, new_node: str, choice_text: Optional[str] = None):
        """Change the current node."""
        old_node = self.session_state.current_node
        self.session_state.current_node = new_node
        
        # Record choice made
        if old_node and choice_text:
            if old_node not in self.session_state.choices_made:
                self.session_state.choices_made[old_node] = []
            self.session_state.choices_made[old_node].append(choice_text)
        
        event = StateChangeEvent("session.node_changed", old_node, new_node, 
                               {"choice_text": choice_text})
        self._fire_event(event)
        
        self.history.add_entry("node_changed", {
            "old_node": old_node,
            "new_node": new_node,
            "choice_text": choice_text
        })
    
    def get_state_summary(self) -> Dict[str, Any]:
        """Get a summary of the current state."""
        return {
            "player": self.player_state.to_dict(),
            "session": self.session_state.to_dict(),
            "history_entries": len(self.history.entries),
            "snapshots": len(self.state_snapshots)
        }
    
    def save_state(self) -> Dict[str, Any]:
        """Serialize state for saving."""
        return {
            "player": self.player_state.to_dict(),
            "session": self.session_state.to_dict(),
            "history": self.history.to_dict(),
            "version": "1.0"
        }
    
    def load_state(self, data: Dict[str, Any]):
        """Load state from saved data."""
        if "player" in data:
            self.player_state = PlayerState.from_dict(data["player"])
        
        if "session" in data:
            self.session_state = GameSession.from_dict(data["session"])
        
        if "history" in data:
            self.history = GameHistory.from_dict(data["history"])
        
        logger.info("State loaded successfully")


# Default validators for common cases
def validate_hp(old_value: int, new_value: int) -> bool:
    """Validate HP changes."""
    return isinstance(new_value, int) and new_value >= 0

def validate_reputation(old_value: int, new_value: int) -> bool:
    """Validate reputation values."""
    return isinstance(new_value, int) and -2 <= new_value <= 2

def validate_tag_list(old_value: List[str], new_value: List[str]) -> bool:
    """Validate tag list changes."""
    return isinstance(new_value, list) and all(isinstance(tag, str) for tag in new_value)


# Create a default state manager instance
def create_default_state_manager() -> StateManager:
    """Create a state manager with default validators."""
    sm = StateManager()
    
    # Add default validators
    sm.add_validator("player.hp", validate_hp)
    sm.add_validator("player.tags", validate_tag_list)
    sm.add_validator("player.traits", validate_tag_list)
    
    return sm