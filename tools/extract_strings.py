#!/usr/bin/env python3
"""
String extraction tool for localization.
Extracts all user-visible strings from the game content for translation.
"""

import json
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engine.localization import LocalizationManager


def main():
    """Extract strings from world data for localization."""
    world_path = PROJECT_ROOT / "world" / "world.json"
    
    if not world_path.exists():
        print(f"Error: World file not found at {world_path}")
        sys.exit(1)
    
    print("=== Patchwork Isles String Extraction Tool ===\n")
    
    # Load world data
    try:
        with open(world_path, 'r', encoding='utf-8') as f:
            world_data = json.load(f)
    except Exception as e:
        print(f"Error loading world data: {e}")
        sys.exit(1)
    
    # Initialize localization manager
    localization_dir = PROJECT_ROOT / "localization"
    loc_manager = LocalizationManager("en", localization_dir)
    
    print(f"Localization directory: {localization_dir}")
    print(f"Extracting strings from: {world_path}")
    
    try:
        # Extract strings and create base language file
        lang_file = loc_manager.create_base_language_file(world_data, overwrite=True)
        
        extracted_strings = loc_manager.extract_strings_from_world(world_data)
        
        print(f"\n✅ Successfully created base language file: {lang_file}")
        print(f"📝 Extracted {len(extracted_strings)} strings")
        
        # Show some example strings
        print("\n📋 Example extracted strings:")
        count = 0
        for key, value in extracted_strings.items():
            if count >= 5:
                break
            if not key.startswith("_") and len(value) < 100:
                print(f"  {key}: \"{value}\"")
                count += 1
        
        if len(extracted_strings) > 5:
            print(f"  ... and {len(extracted_strings) - 5} more")
        
        # Ask if user wants to create translation templates
        print("\n🌍 Translation templates:")
        print("Would you like to create translation templates for other languages?")
        print("1. No, just extract English strings")
        print("2. Create Spanish (es) template")
        print("3. Create French (fr) template") 
        print("4. Create German (de) template")
        print("5. Create custom language template")
        
        try:
            choice = input("\nEnter your choice (1-5) [1]: ").strip() or "1"
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return
        
        if choice == "2":
            template_path = loc_manager.create_translation_template("es", "Español")
            print(f"✅ Created Spanish template: {template_path}")
        elif choice == "3":
            template_path = loc_manager.create_translation_template("fr", "Français")
            print(f"✅ Created French template: {template_path}")
        elif choice == "4":
            template_path = loc_manager.create_translation_template("de", "Deutsch")
            print(f"✅ Created German template: {template_path}")
        elif choice == "5":
            try:
                lang_code = input("Enter language code (e.g., 'ja', 'zh'): ").strip()
                lang_name = input("Enter language name (e.g., 'Japanese', 'Chinese'): ").strip()
                
                if lang_code and lang_name:
                    template_path = loc_manager.create_translation_template(lang_code, lang_name)
                    print(f"✅ Created {lang_name} template: {template_path}")
                else:
                    print("❌ Invalid language code or name")
            except KeyboardInterrupt:
                print("\nTemplate creation cancelled.")
        
        print("\n📚 Next steps:")
        print("1. Translators can now work with the language files in the localization/ directory")
        print("2. Use the engine.localization module to integrate localized strings in the game code")
        print("3. Test different languages by calling set_language('language_code')")
        print("4. Validate translations with LocalizationManager.validate_translation()")
        
    except Exception as e:
        print(f"❌ Error during extraction: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()