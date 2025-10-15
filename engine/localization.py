#!/usr/bin/env python3
"""
Localization framework for Patchwork Isles.
Provides foundation for multi-language support with string externalization and formatting.
"""

import json
import logging
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import re

logger = logging.getLogger("patchwork_isles.localization")


class LocalizationError(Exception):
    """Raised when localization operations fail."""
    pass


class LocalizationManager:
    """Manages localized strings and formatting."""
    
    def __init__(self, base_language: str = "en", localization_dir: Optional[Path] = None):
        self.base_language = base_language
        self.current_language = base_language
        
        if localization_dir is None:
            # Default to localization directory in project root
            self.localization_dir = Path(__file__).parent.parent / "localization"
        else:
            self.localization_dir = localization_dir
        
        self.localization_dir.mkdir(exist_ok=True)
        
        # String tables: {language_code: {string_id: localized_string}}
        self.string_tables = {}
        self.fallback_strings = {}  # Base language fallbacks
        
        # Load available languages
        self._load_all_languages()
    
    def _load_all_languages(self):
        """Load all available language files."""
        if not self.localization_dir.exists():
            return
        
        for lang_file in self.localization_dir.glob("*.json"):
            lang_code = lang_file.stem
            try:
                self._load_language(lang_code)
                logger.info(f"Loaded localization for language: {lang_code}")
            except Exception as e:
                logger.warning(f"Could not load language {lang_code}: {e}")
    
    def _load_language(self, language_code: str):
        """Load strings for a specific language."""
        lang_file = self.localization_dir / f"{language_code}.json"
        
        if not lang_file.exists():
            logger.warning(f"Language file not found: {lang_file}")
            return
        
        try:
            with open(lang_file, 'r', encoding='utf-8') as f:
                strings = json.load(f)
            
            self.string_tables[language_code] = strings
            
            # If this is the base language, also store as fallbacks
            if language_code == self.base_language:
                self.fallback_strings = strings
                
        except Exception as e:
            logger.error(f"Error loading language {language_code}: {e}")
            raise LocalizationError(f"Could not load language {language_code}: {e}")
    
    def set_language(self, language_code: str) -> bool:
        """
        Set the current language.
        
        Args:
            language_code: Language code (e.g., 'en', 'es', 'fr')
        
        Returns:
            True if language was set successfully, False otherwise
        """
        if language_code not in self.string_tables:
            logger.warning(f"Language {language_code} not available")
            return False
        
        self.current_language = language_code
        logger.info(f"Language set to: {language_code}")
        return True
    
    def get_available_languages(self) -> List[str]:
        """Get list of available language codes."""
        return list(self.string_tables.keys())
    
    def localize(self, string_id: str, **kwargs) -> str:
        """
        Get a localized string by ID with optional formatting.
        
        Args:
            string_id: Unique identifier for the string
            **kwargs: Format arguments for string interpolation
        
        Returns:
            Localized and formatted string, or fallback if not found
        """
        # Try current language first
        strings = self.string_tables.get(self.current_language, {})
        localized_string = strings.get(string_id)
        
        # Fall back to base language if not found
        if localized_string is None:
            localized_string = self.fallback_strings.get(string_id)
        
        # Last resort: return the string ID itself as a debug indicator
        if localized_string is None:
            logger.warning(f"String ID not found: {string_id}")
            return f"[{string_id}]"
        
        # Apply formatting if arguments provided
        if kwargs:
            try:
                return localized_string.format(**kwargs)
            except (KeyError, ValueError) as e:
                logger.warning(f"String formatting error for '{string_id}': {e}")
                return localized_string
        
        return localized_string
    
    def localize_plural(self, string_id: str, count: int, **kwargs) -> str:
        """
        Get a pluralized localized string.
        
        Args:
            string_id: Base string ID (will look for string_id_singular, string_id_plural)
            count: Number to determine singular/plural
            **kwargs: Additional format arguments
        
        Returns:
            Appropriately pluralized string
        """
        if count == 1:
            return self.localize(f"{string_id}_singular", count=count, **kwargs)
        else:
            return self.localize(f"{string_id}_plural", count=count, **kwargs)
    
    def extract_strings_from_world(self, world_data: Dict[str, Any]) -> Dict[str, str]:
        """
        Extract all text strings from world data for localization.
        
        Args:
            world_data: World data dictionary
        
        Returns:
            Dictionary mapping generated IDs to original strings
        """
        extracted = {}
        
        # Extract from nodes
        nodes = world_data.get("nodes", {})
        for node_id, node_data in nodes.items():
            # Node text
            if "text" in node_data:
                key = f"node.{node_id}.text"
                extracted[key] = node_data["text"]
            
            # Node title
            if "title" in node_data:
                key = f"node.{node_id}.title"
                extracted[key] = node_data["title"]
            
            # Choice texts
            choices = node_data.get("choices", [])
            for i, choice in enumerate(choices):
                if "text" in choice:
                    key = f"node.{node_id}.choice.{i}.text"
                    extracted[key] = choice["text"]
        
        # Extract from starts
        starts = world_data.get("starts", [])
        for start in starts:
            start_id = start.get("id", "unknown")
            
            if "title" in start:
                key = f"start.{start_id}.title"
                extracted[key] = start["title"]
            
            if "locked_title" in start:
                key = f"start.{start_id}.locked_title"
                extracted[key] = start["locked_title"]
            
            if "blurb" in start:
                key = f"start.{start_id}.blurb"
                extracted[key] = start["blurb"]
        
        # Extract UI strings (common game interface elements)
        ui_strings = {
            "ui.continue": "Continue",
            "ui.back": "Back", 
            "ui.save": "Save",
            "ui.load": "Load",
            "ui.quit": "Quit",
            "ui.settings": "Settings",
            "ui.help": "Help",
            "ui.inventory": "Inventory",
            "ui.character": "Character",
            "ui.empty_inventory": "Your inventory is empty",
            "ui.tags_label": "Tags",
            "ui.traits_label": "Traits",
            "ui.reputation_label": "Reputation",
            "ui.health_label": "Health",
            "game.save_success": "Game saved successfully",
            "game.save_error": "Could not save game",
            "game.load_success": "Game loaded successfully", 
            "game.load_error": "Could not load game",
            "error.node_not_found": "Story location not found",
            "error.choice_unavailable": "That choice is not available",
        }
        
        extracted.update(ui_strings)
        
        return extracted
    
    def create_base_language_file(self, world_data: Dict[str, Any], overwrite: bool = False) -> Path:
        """
        Create a base language file from world data.
        
        Args:
            world_data: World data to extract strings from
            overwrite: Whether to overwrite existing file
        
        Returns:
            Path to created language file
        """
        lang_file = self.localization_dir / f"{self.base_language}.json"
        
        if lang_file.exists() and not overwrite:
            logger.warning(f"Language file already exists: {lang_file}")
            return lang_file
        
        extracted_strings = self.extract_strings_from_world(world_data)
        
        # Create organized structure
        organized = {
            "_metadata": {
                "language": self.base_language,
                "language_name": "English",
                "created": "auto-generated",
                "version": "1.0"
            }
        }
        organized.update(extracted_strings)
        
        with open(lang_file, 'w', encoding='utf-8') as f:
            json.dump(organized, f, indent=2, ensure_ascii=False)
            f.write('\n')
        
        logger.info(f"Created base language file: {lang_file}")
        logger.info(f"Extracted {len(extracted_strings)} strings")
        
        # Reload the language
        self._load_language(self.base_language)
        
        return lang_file
    
    def create_translation_template(self, target_language: str, language_name: str) -> Path:
        """
        Create a translation template for a new language.
        
        Args:
            target_language: Language code (e.g., 'es', 'fr')
            language_name: Human-readable language name (e.g., 'Spanish', 'French')
        
        Returns:
            Path to created template file
        """
        if not self.fallback_strings:
            raise LocalizationError("No base language loaded to create template from")
        
        template_file = self.localization_dir / f"{target_language}.json"
        
        if template_file.exists():
            logger.warning(f"Template file already exists: {template_file}")
            return template_file
        
        template = {
            "_metadata": {
                "language": target_language,
                "language_name": language_name,
                "created": "translation_template",
                "version": "1.0",
                "completion": 0
            }
        }
        
        # Copy all strings from base language but mark for translation
        for key, value in self.fallback_strings.items():
            if not key.startswith("_"):
                template[key] = f"TODO: {value}"
        
        with open(template_file, 'w', encoding='utf-8') as f:
            json.dump(template, f, indent=2, ensure_ascii=False)
            f.write('\n')
        
        logger.info(f"Created translation template: {template_file}")
        return template_file
    
    def validate_translation(self, language_code: str) -> Dict[str, Any]:
        """
        Validate a translation for completeness and consistency.
        
        Args:
            language_code: Language code to validate
        
        Returns:
            Validation report with missing strings and statistics
        """
        if language_code not in self.string_tables:
            return {"error": f"Language {language_code} not loaded"}
        
        base_strings = set(self.fallback_strings.keys())
        target_strings = set(self.string_tables[language_code].keys())
        
        missing_strings = base_strings - target_strings
        extra_strings = target_strings - base_strings
        
        total_base = len([k for k in base_strings if not k.startswith("_")])
        total_translated = len([k for k in target_strings if not k.startswith("_")])
        completion = total_translated / total_base if total_base > 0 else 0
        
        return {
            "language": language_code,
            "completion_percentage": completion * 100,
            "total_strings": total_base,
            "translated_strings": total_translated,
            "missing_strings": list(missing_strings),
            "extra_strings": list(extra_strings),
            "is_complete": len(missing_strings) == 0
        }


# Global localization manager instance
_localization_manager = None


def get_localization_manager() -> LocalizationManager:
    """Get the global localization manager instance."""
    global _localization_manager
    if _localization_manager is None:
        _localization_manager = LocalizationManager()
    return _localization_manager


def init_localization(base_language: str = "en", localization_dir: Optional[Path] = None) -> LocalizationManager:
    """
    Initialize the global localization system.
    
    Args:
        base_language: Base language code
        localization_dir: Directory for localization files
    
    Returns:
        Localization manager instance
    """
    global _localization_manager
    _localization_manager = LocalizationManager(base_language, localization_dir)
    return _localization_manager


def localize(string_id: str, **kwargs) -> str:
    """Shorthand function for localizing strings."""
    return get_localization_manager().localize(string_id, **kwargs)


def set_language(language_code: str) -> bool:
    """Shorthand function for setting language."""
    return get_localization_manager().set_language(language_code)