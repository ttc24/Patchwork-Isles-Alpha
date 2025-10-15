#!/usr/bin/env python3
"""
Modular content system for Patchwork Isles.
Splits world.json into manageable modules and provides content merging capabilities.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass
import re

logger = logging.getLogger("patchwork_isles.content_modules")


@dataclass
class ContentModule:
    """Represents a content module."""
    id: str
    name: str
    description: str
    nodes: Dict[str, Any]
    starts: List[Dict[str, Any]]
    dependencies: List[str] = None
    tags: List[str] = None
    factions: List[str] = None
    
    def __post_init__(self):
        if self.dependencies is None:
            self.dependencies = []
        if self.tags is None:
            self.tags = []
        if self.factions is None:
            self.factions = []
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "_module_info": {
                "id": self.id,
                "name": self.name,
                "description": self.description,
                "dependencies": self.dependencies,
                "tags": self.tags,
                "factions": self.factions,
                "node_count": len(self.nodes),
                "start_count": len(self.starts)
            },
            "nodes": self.nodes,
            "starts": self.starts
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentModule':
        """Create from dictionary."""
        module_info = data.get("_module_info", {})
        return cls(
            id=module_info.get("id", "unknown"),
            name=module_info.get("name", "Unknown Module"),
            description=module_info.get("description", ""),
            nodes=data.get("nodes", {}),
            starts=data.get("starts", []),
            dependencies=module_info.get("dependencies", []),
            tags=module_info.get("tags", []),
            factions=module_info.get("factions", [])
        )


class ContentModuleManager:
    """Manages content modules and world assembly."""
    
    def __init__(self, modules_dir: Optional[Path] = None):
        if modules_dir is None:
            self.modules_dir = Path(__file__).parent.parent / "world" / "modules"
        else:
            self.modules_dir = modules_dir
        
        self.modules_dir.mkdir(parents=True, exist_ok=True)
        self.loaded_modules: Dict[str, ContentModule] = {}
    
    def split_world_into_modules(self, world_data: Dict[str, Any]) -> Dict[str, ContentModule]:
        """
        Split world.json into logical modules.
        
        Args:
            world_data: The world data to split
        
        Returns:
            Dictionary of module_id -> ContentModule
        """
        modules = {}
        
        # Extract nodes by area/theme
        nodes = world_data.get("nodes", {})
        starts = world_data.get("starts", [])
        
        # Group nodes by common prefixes/themes
        node_groups = self._group_nodes_by_theme(nodes)
        start_groups = self._group_starts_by_theme(starts)
        
        # Create modules for each group
        for theme, theme_nodes in node_groups.items():
            theme_starts = start_groups.get(theme, [])
            
            # Extract relevant tags and factions from nodes
            theme_tags = self._extract_tags_from_nodes(theme_nodes)
            theme_factions = self._extract_factions_from_nodes(theme_nodes)
            
            module = ContentModule(
                id=theme,
                name=self._generate_module_name(theme),
                description=f"Content module for {theme} area",
                nodes=theme_nodes,
                starts=theme_starts,
                tags=theme_tags,
                factions=theme_factions
            )
            
            modules[theme] = module
        
        # Create core module for shared content
        core_nodes = {}
        core_starts = []
        
        # Add any nodes that don't fit into theme groups
        all_themed_nodes = set()
        for theme_nodes in node_groups.values():
            all_themed_nodes.update(theme_nodes.keys())
        
        for node_id, node_data in nodes.items():
            if node_id not in all_themed_nodes:
                core_nodes[node_id] = node_data
        
        # Add any starts that don't fit into theme groups
        all_themed_starts = set()
        for theme_starts in start_groups.values():
            for start in theme_starts:
                all_themed_starts.add(start.get("id", ""))
        
        for start in starts:
            if start.get("id", "") not in all_themed_starts:
                core_starts.append(start)
        
        if core_nodes or core_starts:
            core_module = ContentModule(
                id="core",
                name="Core Content",
                description="Core game content and shared nodes",
                nodes=core_nodes,
                starts=core_starts
            )
            modules["core"] = core_module
        
        return modules
    
    def _group_nodes_by_theme(self, nodes: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Group nodes by common themes/prefixes."""
        groups = {}
        
        for node_id, node_data in nodes.items():
            # Determine theme from node ID
            theme = self._determine_node_theme(node_id)
            
            if theme not in groups:
                groups[theme] = {}
            
            groups[theme][node_id] = node_data
        
        return groups
    
    def _group_starts_by_theme(self, starts: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Group starts by their target node themes."""
        groups = {}
        
        for start in starts:
            target_node = start.get("node", "")
            theme = self._determine_node_theme(target_node)
            
            if theme not in groups:
                groups[theme] = []
            
            groups[theme].append(start)
        
        return groups
    
    def _determine_node_theme(self, node_id: str) -> str:
        """Determine the theme of a node based on its ID."""
        # Common prefixes that indicate themes
        theme_patterns = [
            ("tutorial", r"^tutorial_"),
            ("sky_docks", r"^sky_docks?_"),
            ("root", r"^root_"),
            ("prism", r"^prism_"),
            ("singing_depths", r"^singing_depths_"),
            ("crystalline_reaches", r"^crystalline_reaches_"),
            ("moon_eel", r"^moon_eel_"),
            ("storm_rail", r"^storm_rail_"),
            ("shade_walker", r"^shade_walker_"),
            ("cloud_burrow", r"^cloud_burrow_"),
            ("amber_barge", r"^amber_barge_"),
            ("market", r"^.*market.*_"),
            ("orchard", r"^orchard_"),
            ("floating_academy", r"^floating_academy_"),
            ("temporal_garden", r"^temporal_garden"),
            ("shadow_marsh", r"^shadow_marsh"),
            ("void_reaches", r"^void_reaches_"),
            ("tidal_sanctum", r"^tidal_sanctum_"),
            ("ending", r"^ending_"),
            ("hub", r"^.*hub.*_")
        ]
        
        for theme, pattern in theme_patterns:
            if re.match(pattern, node_id, re.IGNORECASE):
                return theme
        
        # Fallback: use first part of node ID
        parts = node_id.split("_")
        if len(parts) > 1:
            return parts[0]
        
        return "misc"
    
    def _generate_module_name(self, theme: str) -> str:
        """Generate a human-readable name for a theme."""
        name_mapping = {
            "tutorial": "Tutorial Island",
            "sky_docks": "Sky Docks Hub",
            "root": "Root Assembly Areas", 
            "prism": "Prism Cartel Areas",
            "singing_depths": "Singing Depths",
            "crystalline_reaches": "Crystalline Reaches",
            "moon_eel": "Moon-Eel Suburbs",
            "storm_rail": "Storm Rail Network",
            "shade_walker": "Shade-Walker Outposts",
            "cloud_burrow": "Cloud-Burrow Lofts",
            "amber_barge": "Amber Barge Routes",
            "market": "Market Areas",
            "orchard": "Memory Orchards",
            "floating_academy": "Floating Academy",
            "temporal_garden": "Temporal Gardens",
            "shadow_marsh": "Shadow Marshes",
            "void_reaches": "Void Reaches",
            "tidal_sanctum": "Tidal Sanctum",
            "ending": "Story Endings",
            "hub": "Hub Locations",
            "misc": "Miscellaneous Content",
            "core": "Core Content"
        }
        
        return name_mapping.get(theme, theme.replace("_", " ").title())
    
    def _extract_tags_from_nodes(self, nodes: Dict[str, Any]) -> List[str]:
        """Extract tags referenced in node conditions/effects."""
        tags = set()
        
        for node_data in nodes.values():
            # Check choices for tag conditions and effects
            choices = node_data.get("choices", [])
            for choice in choices:
                # Check conditions
                condition = choice.get("condition")
                if condition:
                    self._extract_tags_from_condition(condition, tags)
                
                # Check effects
                effects = choice.get("effects", [])
                for effect in effects:
                    if effect.get("type") == "add_tag":
                        tag_value = effect.get("value")
                        if isinstance(tag_value, str):
                            tags.add(tag_value)
        
        return sorted(list(tags))
    
    def _extract_tags_from_condition(self, condition: Any, tags: set):
        """Extract tags from a condition recursively."""
        if isinstance(condition, dict):
            if condition.get("type") == "has_tag":
                tag_value = condition.get("value")
                if isinstance(tag_value, str):
                    tags.add(tag_value)
                elif isinstance(tag_value, list):
                    tags.update(tag_value)
        elif isinstance(condition, list):
            for cond in condition:
                self._extract_tags_from_condition(cond, tags)
    
    def _extract_factions_from_nodes(self, nodes: Dict[str, Any]) -> List[str]:
        """Extract factions referenced in node conditions/effects."""
        factions = set()
        
        for node_data in nodes.values():
            choices = node_data.get("choices", [])
            for choice in choices:
                # Check conditions
                condition = choice.get("condition")
                if condition:
                    self._extract_factions_from_condition(condition, factions)
                
                # Check effects
                effects = choice.get("effects", [])
                for effect in effects:
                    if effect.get("type") == "rep_delta":
                        faction = effect.get("faction")
                        if faction:
                            factions.add(faction)
        
        return sorted(list(factions))
    
    def _extract_factions_from_condition(self, condition: Any, factions: set):
        """Extract factions from a condition recursively."""
        if isinstance(condition, dict):
            if condition.get("type") == "rep_at_least":
                faction = condition.get("faction")
                if faction:
                    factions.add(faction)
        elif isinstance(condition, list):
            for cond in condition:
                self._extract_factions_from_condition(cond, factions)
    
    def save_modules(self, modules: Dict[str, ContentModule], backup_original: bool = True):
        """Save modules to separate files."""
        # Create backup of original world.json if requested
        if backup_original:
            world_path = self.modules_dir.parent / "world.json"
            if world_path.exists():
                backup_path = world_path.with_suffix(".json.pre-modular")
                if not backup_path.exists():
                    with open(world_path, 'r', encoding='utf-8') as src:
                        with open(backup_path, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
                    logger.info(f"Created backup: {backup_path}")
        
        # Save each module to its own file
        for module_id, module in modules.items():
            module_file = self.modules_dir / f"{module_id}.json"
            
            with open(module_file, 'w', encoding='utf-8') as f:
                json.dump(module.to_dict(), f, indent=2, ensure_ascii=False)
                f.write('\n')
            
            logger.info(f"Saved module: {module_file} ({len(module.nodes)} nodes, {len(module.starts)} starts)")
        
        # Create module index
        self._create_module_index(modules)
    
    def _create_module_index(self, modules: Dict[str, ContentModule]):
        """Create an index file listing all modules."""
        index = {
            "_metadata": {
                "description": "Content module index for Patchwork Isles",
                "total_modules": len(modules),
                "created": "auto-generated"
            },
            "modules": []
        }
        
        for module_id, module in modules.items():
            index["modules"].append({
                "id": module.id,
                "name": module.name,
                "description": module.description,
                "file": f"{module_id}.json",
                "dependencies": module.dependencies,
                "node_count": len(module.nodes),
                "start_count": len(module.starts),
                "tags": module.tags,
                "factions": module.factions
            })
        
        index_file = self.modules_dir / "modules.json"
        with open(index_file, 'w', encoding='utf-8') as f:
            json.dump(index, f, indent=2, ensure_ascii=False)
            f.write('\n')
        
        logger.info(f"Created module index: {index_file}")
    
    def load_modules(self) -> Dict[str, ContentModule]:
        """Load all modules from the modules directory."""
        modules = {}
        
        if not self.modules_dir.exists():
            logger.warning(f"Modules directory not found: {self.modules_dir}")
            return modules
        
        for module_file in self.modules_dir.glob("*.json"):
            if module_file.name == "modules.json":
                continue  # Skip index file
            
            try:
                with open(module_file, 'r', encoding='utf-8') as f:
                    module_data = json.load(f)
                
                module = ContentModule.from_dict(module_data)
                modules[module.id] = module
                logger.info(f"Loaded module: {module.name} ({len(module.nodes)} nodes)")
                
            except Exception as e:
                logger.error(f"Error loading module {module_file}: {e}")
        
        self.loaded_modules = modules
        return modules
    
    def merge_modules(self, modules: Dict[str, ContentModule] = None) -> Dict[str, Any]:
        """
        Merge modules back into a single world data structure.
        
        Args:
            modules: Optional modules dict, uses loaded_modules if None
        
        Returns:
            Merged world data
        """
        if modules is None:
            modules = self.loaded_modules
        
        if not modules:
            raise ValueError("No modules available to merge")
        
        # Initialize merged world structure
        merged_world = {
            "title": "Patchwork Isles — Modular Content",
            "factions": [],
            "advanced_tags": [],
            "starts": [],
            "nodes": {},
            "_module_info": {
                "merged_from": list(modules.keys()),
                "total_modules": len(modules),
                "merge_timestamp": "auto"
            }
        }
        
        # Collect all unique factions and tags
        all_factions = set()
        all_tags = set()
        
        # Merge content from each module
        for module_id, module in modules.items():
            logger.info(f"Merging module: {module.name}")
            
            # Merge nodes
            for node_id, node_data in module.nodes.items():
                if node_id in merged_world["nodes"]:
                    logger.warning(f"Node ID conflict: {node_id} (from module {module_id})")
                merged_world["nodes"][node_id] = node_data
            
            # Merge starts
            merged_world["starts"].extend(module.starts)
            
            # Collect factions and tags
            all_factions.update(module.factions)
            all_tags.update(module.tags)
        
        # Set collected factions and tags
        merged_world["factions"] = sorted(list(all_factions))
        merged_world["advanced_tags"] = sorted(list(all_tags))
        
        logger.info(f"Merged {len(modules)} modules: "
                   f"{len(merged_world['nodes'])} nodes, "
                   f"{len(merged_world['starts'])} starts")
        
        return merged_world
    
    def save_merged_world(self, output_path: Optional[Path] = None) -> Path:
        """Save merged world data to file."""
        if output_path is None:
            output_path = self.modules_dir.parent / "world.json"
        
        merged_world = self.merge_modules()
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(merged_world, f, indent=2, ensure_ascii=False)
            f.write('\n')
        
        logger.info(f"Saved merged world: {output_path}")
        return output_path
    
    def validate_modules(self, modules: Dict[str, ContentModule] = None) -> Dict[str, Any]:
        """Validate modules for consistency and missing references."""
        if modules is None:
            modules = self.loaded_modules
        
        validation_report = {
            "modules_checked": len(modules),
            "errors": [],
            "warnings": [],
            "statistics": {}
        }
        
        # Collect all node IDs across modules
        all_node_ids = set()
        for module in modules.values():
            all_node_ids.update(module.nodes.keys())
        
        # Check each module
        for module_id, module in modules.items():
            module_errors = []
            module_warnings = []
            
            # Check for missing node references
            for node_id, node_data in module.nodes.items():
                choices = node_data.get("choices", [])
                for i, choice in enumerate(choices):
                    target = choice.get("target")
                    if target and target not in all_node_ids:
                        module_errors.append(f"Module {module_id}, node {node_id}, choice {i}: "
                                           f"references missing node '{target}'")
            
            # Check start references
            for start in module.starts:
                target_node = start.get("node")
                if target_node and target_node not in all_node_ids:
                    module_errors.append(f"Module {module_id}, start '{start.get('id')}': "
                                       f"references missing node '{target_node}'")
            
            if module_errors:
                validation_report["errors"].extend(module_errors)
            if module_warnings:
                validation_report["warnings"].extend(module_warnings)
        
        validation_report["statistics"] = {
            "total_nodes": len(all_node_ids),
            "modules_with_errors": len([m for m in modules if any(e.startswith(f"Module {m}") 
                                                                for e in validation_report["errors"])]),
            "is_valid": len(validation_report["errors"]) == 0
        }
        
        return validation_report


def split_world_into_modules(world_path: Path, modules_dir: Optional[Path] = None) -> Dict[str, ContentModule]:
    """
    Convenience function to split world.json into modules.
    
    Args:
        world_path: Path to world.json
        modules_dir: Optional directory for modules
    
    Returns:
        Dictionary of created modules
    """
    # Load world data
    with open(world_path, 'r', encoding='utf-8') as f:
        world_data = json.load(f)
    
    # Create manager and split
    manager = ContentModuleManager(modules_dir)
    modules = manager.split_world_into_modules(world_data)
    
    # Save modules
    manager.save_modules(modules)
    
    return modules