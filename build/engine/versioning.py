#!/usr/bin/env python3
"""
Content versioning system for Patchwork Isles.
Manages world data versioning and save file compatibility across content updates.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass, asdict
import hashlib

logger = logging.getLogger("patchwork_isles.versioning")


@dataclass
class ContentVersion:
    """Represents a content version."""
    major: int
    minor: int
    patch: int
    timestamp: str
    content_hash: str
    description: str = ""
    
    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContentVersion':
        return cls(**data)
    
    def is_compatible_with(self, other: 'ContentVersion') -> bool:
        """Check if this version is compatible with another version."""
        # Same major version is generally compatible
        # Different major versions may have breaking changes
        return self.major == other.major
    
    def is_newer_than(self, other: 'ContentVersion') -> bool:
        """Check if this version is newer than another."""
        if self.major != other.major:
            return self.major > other.major
        if self.minor != other.minor:
            return self.minor > other.minor
        return self.patch > other.patch


class ContentVersionManager:
    """Manages content versioning and migration."""
    
    def __init__(self, world_data: Dict[str, Any], project_root: Optional[Path] = None):
        self.world_data = world_data
        self.project_root = project_root or Path(__file__).parent.parent
        self.versions_file = self.project_root / "versions.json"
        self.version_history = self._load_version_history()
    
    def _load_version_history(self) -> List[ContentVersion]:
        """Load version history from disk."""
        if not self.versions_file.exists():
            return []
        
        try:
            with open(self.versions_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            return [ContentVersion.from_dict(v) for v in data.get("versions", [])]
        except Exception as e:
            logger.warning(f"Could not load version history: {e}")
            return []
    
    def _save_version_history(self) -> None:
        """Save version history to disk."""
        try:
            data = {
                "versions": [v.to_dict() for v in self.version_history],
                "last_updated": datetime.now().isoformat()
            }
            
            with open(self.versions_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
                f.write('\n')
            
            logger.info(f"Version history saved to {self.versions_file}")
        except Exception as e:
            logger.error(f"Could not save version history: {e}")
    
    def _calculate_content_hash(self) -> str:
        """Calculate a hash of the current content."""
        # Create a stable representation of the content for hashing
        content_str = json.dumps(self.world_data, sort_keys=True)
        return hashlib.sha256(content_str.encode('utf-8')).hexdigest()[:16]
    
    def get_current_version(self) -> Optional[ContentVersion]:
        """Get the current content version from world data."""
        version_data = self.world_data.get("_version")
        if not version_data:
            return None
        
        return ContentVersion.from_dict(version_data)
    
    def set_current_version(self, version: ContentVersion) -> None:
        """Set the current version in world data."""
        self.world_data["_version"] = version.to_dict()
        logger.info(f"Set content version to {version}")
    
    def create_new_version(
        self, 
        version_type: str = "patch", 
        description: str = ""
    ) -> ContentVersion:
        """
        Create a new version based on the current content.
        
        Args:
            version_type: Type of version bump ("major", "minor", "patch")
            description: Description of changes in this version
        
        Returns:
            New ContentVersion object
        """
        current = self.get_current_version()
        
        if current is None:
            # First version
            new_version = ContentVersion(
                major=1,
                minor=0,
                patch=0,
                timestamp=datetime.now().isoformat(),
                content_hash=self._calculate_content_hash(),
                description=description or "Initial version"
            )
        else:
            # Increment based on type
            if version_type == "major":
                new_version = ContentVersion(
                    major=current.major + 1,
                    minor=0,
                    patch=0,
                    timestamp=datetime.now().isoformat(),
                    content_hash=self._calculate_content_hash(),
                    description=description
                )
            elif version_type == "minor":
                new_version = ContentVersion(
                    major=current.major,
                    minor=current.minor + 1,
                    patch=0,
                    timestamp=datetime.now().isoformat(),
                    content_hash=self._calculate_content_hash(),
                    description=description
                )
            else:  # patch
                new_version = ContentVersion(
                    major=current.major,
                    minor=current.minor,
                    patch=current.patch + 1,
                    timestamp=datetime.now().isoformat(),
                    content_hash=self._calculate_content_hash(),
                    description=description
                )
        
        # Add to history
        self.version_history.append(new_version)
        self.set_current_version(new_version)
        self._save_version_history()
        
        logger.info(f"Created new version {new_version}: {description}")
        return new_version
    
    def check_save_compatibility(self, save_data: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Check if a save file is compatible with the current content version.
        
        Args:
            save_data: Save file data to check
        
        Returns:
            Tuple of (is_compatible, reason)
        """
        current_version = self.get_current_version()
        if not current_version:
            return True, "No version information available"
        
        save_version_data = save_data.get("content_version")
        if not save_version_data:
            return False, "Save file has no version information"
        
        try:
            save_version = ContentVersion.from_dict(save_version_data)
        except Exception as e:
            return False, f"Invalid version data in save file: {e}"
        
        if not current_version.is_compatible_with(save_version):
            return False, f"Save version {save_version} incompatible with content version {current_version}"
        
        if save_version.is_newer_than(current_version):
            return False, f"Save file is from newer version {save_version}, current is {current_version}"
        
        return True, "Compatible"
    
    def migrate_save_data(self, save_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Migrate save data to be compatible with the current version.
        
        Args:
            save_data: Save data to migrate
        
        Returns:
            Migrated save data
        """
        current_version = self.get_current_version()
        if not current_version:
            return save_data
        
        save_version_data = save_data.get("content_version")
        if not save_version_data:
            # Old save without version info - apply basic migration
            migrated_data = dict(save_data)
            migrated_data["content_version"] = current_version.to_dict()
            logger.info("Migrated legacy save file to current version")
            return migrated_data
        
        save_version = ContentVersion.from_dict(save_version_data)
        
        if save_version == current_version:
            return save_data  # No migration needed
        
        # Apply version-specific migrations
        migrated_data = dict(save_data)
        
        # Migration logic would go here
        # For now, just update the version
        migrated_data["content_version"] = current_version.to_dict()
        
        logger.info(f"Migrated save data from version {save_version} to {current_version}")
        return migrated_data
    
    def add_version_to_save(self, save_data: Dict[str, Any]) -> Dict[str, Any]:
        """Add current version information to save data."""
        current_version = self.get_current_version()
        if current_version:
            save_data["content_version"] = current_version.to_dict()
        return save_data
    
    def get_version_info(self) -> Dict[str, Any]:
        """Get detailed version information."""
        current = self.get_current_version()
        
        return {
            "current_version": current.to_dict() if current else None,
            "version_count": len(self.version_history),
            "first_version": self.version_history[0].to_dict() if self.version_history else None,
            "content_hash": self._calculate_content_hash(),
            "versions_file": str(self.versions_file)
        }
    
    def detect_content_changes(self) -> bool:
        """Detect if content has changed since last version."""
        current_version = self.get_current_version()
        if not current_version:
            return True  # No version means changes exist
        
        current_hash = self._calculate_content_hash()
        return current_hash != current_version.content_hash
    
    def auto_version_if_changed(self, description: str = "") -> Optional[ContentVersion]:
        """Automatically create a new version if content has changed."""
        if self.detect_content_changes():
            return self.create_new_version("patch", description or "Automatic versioning - content changes detected")
        return None


def version_world_content(world_path: Path, version_type: str = "patch", description: str = "") -> ContentVersion:
    """
    Convenience function to version world content.
    
    Args:
        world_path: Path to world.json file
        version_type: Type of version bump ("major", "minor", "patch")
        description: Description of changes
    
    Returns:
        New ContentVersion
    """
    with open(world_path, 'r', encoding='utf-8') as f:
        world_data = json.load(f)
    
    manager = ContentVersionManager(world_data)
    new_version = manager.create_new_version(version_type, description)
    
    # Save updated world data with version
    with open(world_path, 'w', encoding='utf-8') as f:
        json.dump(world_data, f, indent=2, ensure_ascii=False)
        f.write('\n')
    
    return new_version


def check_save_compatibility(save_data: Dict[str, Any], world_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Convenience function to check save compatibility.
    
    Args:
        save_data: Save file data
        world_data: Current world data
    
    Returns:
        Tuple of (is_compatible, reason)
    """
    manager = ContentVersionManager(world_data)
    return manager.check_save_compatibility(save_data)