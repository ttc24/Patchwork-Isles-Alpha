#!/usr/bin/env python3
"""
Schema validation for world data structures.
Validates world.json against the defined schema to catch structural issues early.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

try:
    import jsonschema
    JSONSCHEMA_AVAILABLE = True
except ImportError:
    JSONSCHEMA_AVAILABLE = False
    logging.warning("jsonschema not available - schema validation will be skipped")


logger = logging.getLogger(__name__)


class SchemaValidationError(Exception):
    """Raised when schema validation fails."""
    pass


class WorldValidator:
    """Validates world data against the schema."""
    
    def __init__(self, schema_path: Optional[Path] = None):
        """Initialize validator with schema."""
        if schema_path is None:
            # Default to schema in project root
            project_root = Path(__file__).parent.parent
            schema_path = project_root / "schemas" / "world_schema.json"
        
        self.schema_path = schema_path
        self.schema = None
        self._load_schema()
    
    def _load_schema(self) -> None:
        """Load the JSON schema from disk."""
        if not self.schema_path.exists():
            logger.warning(f"Schema file not found: {self.schema_path}")
            return
        
        try:
            with open(self.schema_path, 'r', encoding='utf-8') as f:
                self.schema = json.load(f)
            logger.debug(f"Loaded schema from {self.schema_path}")
        except Exception as e:
            logger.error(f"Failed to load schema: {e}")
            raise SchemaValidationError(f"Could not load schema: {e}")
    
    def validate_world_data(self, world_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate world data against the schema.
        
        Args:
            world_data: The world data to validate
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if not JSONSCHEMA_AVAILABLE:
            logger.warning("jsonschema not available - returning validation success")
            return True, []
        
        if self.schema is None:
            logger.warning("No schema loaded - returning validation success")
            return True, []
        
        errors = []
        
        try:
            jsonschema.validate(world_data, self.schema)
            logger.info("World data passed schema validation")
            return True, []
        except jsonschema.ValidationError as e:
            error_msg = f"Schema validation error at {'.'.join(str(p) for p in e.absolute_path)}: {e.message}"
            errors.append(error_msg)
            logger.error(error_msg)
        except jsonschema.SchemaError as e:
            error_msg = f"Schema definition error: {e.message}"
            errors.append(error_msg)
            logger.error(error_msg)
        except Exception as e:
            error_msg = f"Unexpected validation error: {e}"
            errors.append(error_msg)
            logger.error(error_msg)
        
        return False, errors
    
    def validate_world_file(self, world_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate a world file against the schema.
        
        Args:
            world_path: Path to the world.json file
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        if not world_path.exists():
            return False, [f"World file not found: {world_path}"]
        
        try:
            with open(world_path, 'r', encoding='utf-8') as f:
                world_data = json.load(f)
        except json.JSONDecodeError as e:
            return False, [f"Invalid JSON in world file: {e}"]
        except Exception as e:
            return False, [f"Could not read world file: {e}"]
        
        return self.validate_world_data(world_data)
    
    def validate_node_references(self, world_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate that all node references are valid.
        This is a semantic validation beyond the schema.
        
        Args:
            world_data: The world data to validate
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        nodes = world_data.get("nodes", {})
        node_ids = set(nodes.keys())
        
        # Check start entries
        starts = world_data.get("starts", [])
        for i, start in enumerate(starts):
            if not isinstance(start, dict):
                continue
            
            target_node = start.get("node")
            if target_node and target_node not in node_ids:
                errors.append(f"Start entry {i} ({start.get('id', 'unknown')}) "
                            f"references non-existent node '{target_node}'")
        
        # Check choice destinations
        for node_id, node_data in nodes.items():
            if not isinstance(node_data, dict):
                continue
            
            choices = node_data.get("choices", [])
            for i, choice in enumerate(choices):
                if not isinstance(choice, dict):
                    continue
                
                target = choice.get("target")
                if target and target not in node_ids:
                    errors.append(f"Choice {i} in node '{node_id}' "
                                f"targets non-existent node '{target}'")
        
        return len(errors) == 0, errors
    
    def validate_faction_references(self, world_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate that all faction references are valid.
        
        Args:
            world_data: The world data to validate
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        factions = set(world_data.get("factions", []))
        
        # Check faction references in nodes
        nodes = world_data.get("nodes", {})
        for node_id, node_data in nodes.items():
            if not isinstance(node_data, dict):
                continue
            
            # Check choices
            choices = node_data.get("choices", [])
            for i, choice in enumerate(choices):
                if not isinstance(choice, dict):
                    continue
                
                # Check conditions
                condition = choice.get("condition", {})
                if isinstance(condition, dict) and condition.get("faction"):
                    faction = condition["faction"]
                    if faction not in factions:
                        errors.append(f"Choice {i} in node '{node_id}' "
                                    f"references unknown faction '{faction}'")
                
                # Check effects
                effects = choice.get("effects", [])
                for j, effect in enumerate(effects):
                    if isinstance(effect, dict) and effect.get("faction"):
                        faction = effect["faction"]
                        if faction not in factions:
                            errors.append(f"Effect {j} of choice {i} in node '{node_id}' "
                                        f"references unknown faction '{faction}'")
        
        return len(errors) == 0, errors
    
    def full_validation(self, world_data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Perform comprehensive validation including schema and semantic checks.
        
        Args:
            world_data: The world data to validate
        
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        all_errors = []
        all_valid = True
        
        # Schema validation
        schema_valid, schema_errors = self.validate_world_data(world_data)
        if not schema_valid:
            all_valid = False
            all_errors.extend(schema_errors)
        
        # Node reference validation
        node_valid, node_errors = self.validate_node_references(world_data)
        if not node_valid:
            all_valid = False
            all_errors.extend(node_errors)
        
        # Faction reference validation  
        faction_valid, faction_errors = self.validate_faction_references(world_data)
        if not faction_valid:
            all_valid = False
            all_errors.extend(faction_errors)
        
        return all_valid, all_errors


def validate_world_file(world_path: Path, schema_path: Optional[Path] = None) -> Tuple[bool, List[str]]:
    """
    Convenience function to validate a world file.
    
    Args:
        world_path: Path to world.json
        schema_path: Optional path to schema file
    
    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    validator = WorldValidator(schema_path)
    return validator.validate_world_file(world_path)