"""Multi-profile management for Patchwork Isles."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

DEFAULT_PROFILE_DIR = "profiles"
PROFILE_PATTERN = re.compile(r"^[a-zA-Z0-9_-]+$")


class ProfileManager:
    """Manages multiple character profiles."""
    
    def __init__(self, profiles_dir: Path | str = DEFAULT_PROFILE_DIR):
        self.profiles_dir = Path(profiles_dir)
        self.profiles_dir.mkdir(exist_ok=True)
        
    def list_profiles(self) -> List[Dict[str, str]]:
        """List all available profiles with metadata."""
        profiles = []
        
        for profile_path in self.profiles_dir.glob("*.json"):
            profile_name = profile_path.stem
            try:
                with profile_path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                
                # Extract metadata
                last_character = "Unknown"
                last_played = "Never"
                endings_count = len(data.get("seen_endings", []))
                legacy_tags = len(data.get("legacy_tags", []))
                unlocked_starts = len(data.get("unlocked_starts", []))
                
                # Try to get last character from save files
                saves_dir = Path("saves")
                if saves_dir.exists():
                    # Look for recent autosave or quick save
                    for save_type in ["autosave", "quick"]:
                        save_path = saves_dir / save_type / "save_v1.json"
                        if save_path.exists():
                            try:
                                with save_path.open("r", encoding="utf-8") as sf:
                                    save_data = json.load(sf)
                                metadata = save_data.get("metadata", {})
                                if metadata.get("player_name"):
                                    last_character = metadata["player_name"]
                                if metadata.get("saved_at"):
                                    # Parse ISO timestamp
                                    saved_at = metadata["saved_at"]
                                    try:
                                        dt = datetime.fromisoformat(saved_at.replace("Z", "+00:00"))
                                        last_played = dt.strftime("%Y-%m-%d %H:%M")
                                    except ValueError:
                                        last_played = saved_at[:16]  # Just take date/time part
                                break
                            except (json.JSONDecodeError, KeyError):
                                continue
                
                profiles.append({
                    "name": profile_name,
                    "path": str(profile_path),
                    "last_character": last_character,
                    "last_played": last_played,
                    "endings": str(endings_count),
                    "legacy_tags": str(legacy_tags),
                    "unlocked_starts": str(unlocked_starts),
                })
                
            except (json.JSONDecodeError, OSError):
                # Skip corrupted profiles
                continue
                
        return sorted(profiles, key=lambda p: p["name"])
    
    def create_profile(self, name: str) -> Path:
        """Create a new profile with the given name."""
        if not PROFILE_PATTERN.match(name):
            raise ValueError("Profile names can only contain letters, numbers, hyphens, and underscores")
        
        profile_path = self.profiles_dir / f"{name}.json"
        if profile_path.exists():
            raise ValueError(f"Profile '{name}' already exists")
        
        # Create default profile structure
        default_profile = {
            "unlocked_starts": [],
            "legacy_tags": [],
            "seen_endings": [],
            "flags": {},
        }
        
        with profile_path.open("w", encoding="utf-8") as f:
            json.dump(default_profile, f, indent=2)
            f.write("\n")
        
        return profile_path
    
    def delete_profile(self, name: str) -> bool:
        """Delete a profile. Returns True if deleted, False if not found."""
        profile_path = self.profiles_dir / f"{name}.json"
        if profile_path.exists():
            profile_path.unlink()
            # Also clean up associated saves
            saves_dir = Path("saves")
            if saves_dir.exists():
                for save_type in ["autosave", "quick"]:
                    save_dir = saves_dir / save_type
                    if save_dir.exists():
                        # Could implement save cleanup here if needed
                        pass
            return True
        return False
    
    def get_profile_path(self, name: str) -> Path:
        """Get the path to a profile file."""
        return self.profiles_dir / f"{name}.json"
    
    def load_profile_data(self, name: str) -> dict:
        """Load profile data by name."""
        profile_path = self.get_profile_path(name)
        if not profile_path.exists():
            raise FileNotFoundError(f"Profile '{name}' not found")
        
        with profile_path.open("r", encoding="utf-8") as f:
            return json.load(f)


def select_profile(profile_manager: ProfileManager, open_options=None) -> tuple[str, Path]:
    """Interactive profile selection menu."""
    
    while True:
        print("\n")
        print("═══ PATCHWORK ISLES ═══")
        print("Choose your character")
        print()
        
        profiles = profile_manager.list_profiles()
        
        if not profiles:
            print("🎆 Welcome! Let's create your first character profile.")
            print()
            name = input("📝 Profile name: ").strip()
            if not name:
                print("⚠️  Profile name cannot be empty.")
                continue
            
            try:
                path = profile_manager.create_profile(name)
                print(f"✨ Created profile: {name}")
                return name, path
            except ValueError as e:
                print(f"⚠️  {e}")
                continue
        
        # Show profiles in a clean, card-like format
        for i, profile in enumerate(profiles, 1):
            # Profile card
            name = profile['name']
            last_char = profile['last_character']
            last_played = profile['last_played']
            endings = profile['endings']
            starts = profile['unlocked_starts']
            
            print(f"  {i}. 💻 {name}")
            if last_char != "Unknown":
                print(f"     🎭 Last: {last_char}")
            if last_played != "Never":
                print(f"     📅 Played: {last_played}")
            if int(endings) > 0 or int(starts) > 0:
                print(f"     🎆 Progress: {endings} endings, {starts} origins")
            print()
        
        # Clean action menu
        print("━" * 40)
        actions = [f"[{i}] Select profile" for i in range(1, len(profiles) + 1)]
        actions.extend(["[N] New profile", "[D] Delete profile"])
        if open_options:
            actions.append("[O] Options")
        actions.append("[Q] Quit")
        
        print("  " + " • ".join(actions[:3]))  # First row
        if len(actions) > 3:
            print("  " + " • ".join(actions[3:]))  # Second row
        print()
        
        choice = input("Select profile > ").strip().lower()
        
        if choice == "q":
            print("Goodbye!")
            sys.exit(0)
        
        if choice == "n":
            name = input("Enter new profile name: ").strip()
            if not name:
                print("Profile name cannot be empty.")
                continue
            
            try:
                path = profile_manager.create_profile(name)
                print(f"Created profile: {name}")
                return name, path
            except ValueError as e:
                print(f"Error: {e}")
                continue
        
        if choice == "d":
            if len(profiles) <= 1:
                print("Cannot delete the only profile. Create another one first.")
                continue
                
            name = input("Enter profile name to delete: ").strip()
            if not name:
                continue
                
            confirmation = input(f"Really delete profile '{name}'? (yes/no): ").strip().lower()
            if confirmation in ("yes", "y"):
                if profile_manager.delete_profile(name):
                    print(f"Deleted profile: {name}")
                else:
                    print(f"Profile '{name}' not found.")
            continue
        
        if choice == "o" and open_options:
            open_options()
            continue
        
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(profiles):
                selected = profiles[idx]
                return selected["name"], Path(selected["path"])
            else:
                print("Invalid profile number.")
                continue
        
        print("Invalid selection. Please try again.")


def load_profile_with_manager(profile_name: str) -> dict:
    """Load profile data using the profile manager."""
    manager = ProfileManager()
    return manager.load_profile_data(profile_name)