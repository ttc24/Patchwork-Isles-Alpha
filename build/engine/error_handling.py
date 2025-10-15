#!/usr/bin/env python3
"""
Error handling and recovery mechanisms for Patchwork Isles engine.
Provides graceful degradation when encountering missing nodes or other runtime errors.
"""

import logging
from typing import Dict, Any, Optional, List, Tuple
from pathlib import Path

logger = logging.getLogger("patchwork_isles.error_handling")


class GameEngineError(Exception):
    """Base exception for game engine errors."""
    pass


class MissingNodeError(GameEngineError):
    """Raised when a referenced node cannot be found."""
    def __init__(self, node_id: str, source_context: str = "unknown"):
        self.node_id = node_id
        self.source_context = source_context
        super().__init__(f"Missing node '{node_id}' referenced from {source_context}")


class InvalidChoiceError(GameEngineError):
    """Raised when a choice leads to an invalid state."""
    def __init__(self, choice_index: int, node_id: str, reason: str):
        self.choice_index = choice_index
        self.node_id = node_id
        self.reason = reason
        super().__init__(f"Invalid choice {choice_index} in node '{node_id}': {reason}")


class SaveDataCorruptionError(GameEngineError):
    """Raised when save data is corrupted or incompatible."""
    def __init__(self, file_path: Path, reason: str):
        self.file_path = file_path
        self.reason = reason
        super().__init__(f"Save data corruption in {file_path}: {reason}")


class ErrorHandler:
    """Handles errors gracefully with recovery mechanisms."""
    
    def __init__(self, world_data: Dict[str, Any], fallback_node: str = "error_fallback"):
        self.world_data = world_data
        self.fallback_node = fallback_node
        self.error_count = 0
        self.max_errors = 10
        self.reported_missing_nodes = set()
    
    def handle_missing_node(self, node_id: str, source_context: str = "unknown") -> Tuple[str, Dict[str, Any]]:
        """
        Handle missing node error by providing fallback.
        
        Args:
            node_id: The missing node ID
            source_context: Where the missing reference came from
        
        Returns:
            Tuple of (fallback_node_id, fallback_node_data)
        """
        self.error_count += 1
        
        # Only log each missing node once to avoid spam
        if node_id not in self.reported_missing_nodes:
            logger.error(f"Missing node '{node_id}' referenced from {source_context}")
            self.reported_missing_nodes.add(node_id)
        
        # Check if we have too many errors
        if self.error_count > self.max_errors:
            logger.critical("Too many errors encountered, creating emergency fallback")
            return self._create_emergency_fallback()
        
        # Try to find a reasonable fallback
        fallback_id, fallback_data = self._find_fallback_node(node_id, source_context)
        
        if fallback_data is None:
            logger.warning(f"No fallback found for missing node '{node_id}', creating emergency node")
            return self._create_emergency_node(node_id)
        
        return fallback_id, fallback_data
    
    def handle_invalid_choice(self, choice_index: int, node_id: str, reason: str) -> Optional[Dict[str, Any]]:
        """
        Handle invalid choice by providing fallback or None to skip.
        
        Args:
            choice_index: Index of the invalid choice
            node_id: Node containing the invalid choice
            reason: Why the choice is invalid
        
        Returns:
            Fallback choice data or None to skip
        """
        logger.warning(f"Invalid choice {choice_index} in node '{node_id}': {reason}")
        
        # Create a fallback choice that goes back to a safe location
        fallback_choice = {
            "text": f"[ERROR RECOVERY] Return to safe location (choice {choice_index} was invalid)",
            "target": self._find_safe_node()
        }
        
        return fallback_choice
    
    def handle_save_corruption(self, file_path: Path, reason: str) -> Dict[str, Any]:
        """
        Handle save data corruption by providing clean default state.
        
        Args:
            file_path: Path to corrupted save file
            reason: Description of the corruption
        
        Returns:
            Clean default save state
        """
        logger.error(f"Save data corruption in {file_path}: {reason}")
        
        # Create backup of corrupted file
        try:
            backup_path = file_path.with_suffix(f"{file_path.suffix}.corrupted")
            if file_path.exists():
                file_path.rename(backup_path)
                logger.info(f"Corrupted save backed up to {backup_path}")
        except Exception as e:
            logger.warning(f"Could not backup corrupted save: {e}")
        
        # Return clean default state
        from engine.engine_min import default_profile
        return default_profile()
    
    def _find_fallback_node(self, missing_node: str, source_context: str) -> Tuple[str, Optional[Dict[str, Any]]]:
        """Find an appropriate fallback node."""
        nodes = self.world_data.get("nodes", {})
        
        # Strategy 1: Try predefined fallback node
        if self.fallback_node in nodes:
            return self.fallback_node, nodes[self.fallback_node]
        
        # Strategy 2: Try to find a tutorial or safe node
        safe_node_patterns = ["tutorial", "safe", "start", "landing", "hub"]
        for pattern in safe_node_patterns:
            for node_id, node_data in nodes.items():
                if pattern in node_id.lower():
                    logger.info(f"Using fallback node '{node_id}' for missing '{missing_node}'")
                    return node_id, node_data
        
        # Strategy 3: Use first available node
        if nodes:
            first_node_id = next(iter(nodes))
            logger.info(f"Using first available node '{first_node_id}' as fallback")
            return first_node_id, nodes[first_node_id]
        
        return "emergency_fallback", None
    
    def _find_safe_node(self) -> str:
        """Find a safe node to return to."""
        nodes = self.world_data.get("nodes", {})
        
        # Look for tutorial or safe nodes
        safe_patterns = ["tutorial_arrival", "landing", "start", "safe"]
        for pattern in safe_patterns:
            for node_id in nodes:
                if pattern in node_id.lower():
                    return node_id
        
        # Look for nodes in starts
        starts = self.world_data.get("starts", [])
        if starts:
            first_start = starts[0]
            if isinstance(first_start, dict) and "node" in first_start:
                return first_start["node"]
        
        # Return first available node or fallback
        if nodes:
            return next(iter(nodes))
        
        return self.fallback_node
    
    def _create_emergency_node(self, missing_node: str) -> Tuple[str, Dict[str, Any]]:
        """Create an emergency replacement node."""
        emergency_node = {
            "id": f"emergency_{missing_node}",
            "title": "Error Recovery",
            "text": f"An error occurred trying to reach '{missing_node}'. "
                   f"This is a temporary recovery location.",
            "choices": [
                {
                    "text": "Return to a safe location",
                    "target": self._find_safe_node()
                },
                {
                    "text": "Report this error (opens game logs)",
                    "effects": [
                        {
                            "type": "set_flag",
                            "flag": f"error_reported_{missing_node}",
                            "value": True
                        }
                    ],
                    "target": self._find_safe_node()
                }
            ]
        }
        
        return f"emergency_{missing_node}", emergency_node
    
    def _create_emergency_fallback(self) -> Tuple[str, Dict[str, Any]]:
        """Create final emergency fallback when all else fails."""
        emergency_fallback = {
            "id": "emergency_final_fallback",
            "title": "Critical Error Recovery",
            "text": "The game has encountered multiple critical errors. "
                   "Please save your progress and restart the game. "
                   "Check the game logs for details about what went wrong.",
            "choices": [
                {
                    "text": "Save and exit",
                    "effects": [
                        {
                            "type": "set_flag",
                            "flag": "emergency_save_requested",
                            "value": True
                        }
                    ]
                }
            ]
        }
        
        return "emergency_final_fallback", emergency_fallback
    
    def validate_node_references(self, node_data: Dict[str, Any], node_id: str) -> Dict[str, Any]:
        """
        Validate and fix node references within a node.
        
        Args:
            node_data: The node data to validate
            node_id: ID of the node being validated
        
        Returns:
            Cleaned node data with fixed references
        """
        if not isinstance(node_data, dict):
            return node_data
        
        cleaned_data = dict(node_data)
        nodes = self.world_data.get("nodes", {})
        
        # Check choices
        choices = cleaned_data.get("choices", [])
        if isinstance(choices, list):
            cleaned_choices = []
            for i, choice in enumerate(choices):
                if isinstance(choice, dict):
                    cleaned_choice = dict(choice)
                    target = choice.get("target")
                    
                    # Validate target exists
                    if target and target not in nodes:
                        logger.warning(f"Choice {i} in node '{node_id}' references missing node '{target}'")
                        # Replace with safe fallback
                        cleaned_choice["target"] = self._find_safe_node()
                        cleaned_choice["text"] = f"[FIXED] {choice.get('text', 'Continue')}"
                    
                    cleaned_choices.append(cleaned_choice)
                else:
                    logger.warning(f"Invalid choice {i} in node '{node_id}' - not a dict")
            
            cleaned_data["choices"] = cleaned_choices
        
        return cleaned_data


def with_error_recovery(func):
    """Decorator to add error recovery to functions."""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except MissingNodeError as e:
            logger.error(f"Missing node error in {func.__name__}: {e}")
            # Try to recover with a safe fallback
            if hasattr(args[0], 'error_handler'):
                error_handler = args[0].error_handler
                fallback_id, fallback_data = error_handler.handle_missing_node(
                    e.node_id, f"{func.__name__}"
                )
                return fallback_id, fallback_data
            else:
                raise
        except Exception as e:
            logger.exception(f"Unexpected error in {func.__name__}: {e}")
            raise
    
    return wrapper