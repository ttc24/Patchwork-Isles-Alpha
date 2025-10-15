#!/usr/bin/env python3
"""
Modular content management tool for Patchwork Isles.
Splits world.json into manageable modules and provides merging capabilities.
"""

import json
import sys
from pathlib import Path

# Add project root to path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from engine.content_modules import ContentModuleManager, split_world_into_modules


def main():
    """Main function to manage modular content."""
    world_path = PROJECT_ROOT / "world" / "world.json"
    modules_dir = PROJECT_ROOT / "world" / "modules"
    
    print("=== Patchwork Isles Modular Content Manager ===\n")
    
    # Check current state
    if modules_dir.exists() and any(modules_dir.glob("*.json")):
        modules_exist = True
        print(f"📁 Modules directory exists: {modules_dir}")
        module_files = list(modules_dir.glob("*.json"))
        print(f"📄 Found {len(module_files)} module files")
    else:
        modules_exist = False
        print(f"📁 No modules found at: {modules_dir}")
    
    if world_path.exists():
        world_size = world_path.stat().st_size / 1024 / 1024  # MB
        print(f"🌍 World file exists: {world_path} ({world_size:.1f}MB)")
    else:
        print(f"❌ World file not found: {world_path}")
        sys.exit(1)
    
    print("\n🔧 Available operations:")
    
    if not modules_exist:
        print("1. Split world.json into modules")
        print("2. Exit")
        
        try:
            choice = input("\nEnter your choice (1-2) [1]: ").strip() or "1"
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return
        
        if choice == "1":
            split_world_into_modules_interactive(world_path, modules_dir)
        elif choice == "2":
            print("Exiting.")
        else:
            print("Invalid choice.")
    
    else:
        print("1. Re-split world.json into modules (overwrites existing)")
        print("2. Merge modules back into world.json")
        print("3. Validate modules")
        print("4. Show module statistics")
        print("5. Exit")
        
        try:
            choice = input("\nEnter your choice (1-5) [2]: ").strip() or "2"
        except KeyboardInterrupt:
            print("\nOperation cancelled.")
            return
        
        if choice == "1":
            split_world_into_modules_interactive(world_path, modules_dir)
        elif choice == "2":
            merge_modules_interactive(modules_dir, world_path)
        elif choice == "3":
            validate_modules_interactive(modules_dir)
        elif choice == "4":
            show_module_statistics(modules_dir)
        elif choice == "5":
            print("Exiting.")
        else:
            print("Invalid choice.")


def split_world_into_modules_interactive(world_path: Path, modules_dir: Path):
    """Interactive world splitting."""
    print(f"\n🔨 Splitting {world_path} into modules...")
    
    # Load world data to show statistics
    try:
        with open(world_path, 'r', encoding='utf-8') as f:
            world_data = json.load(f)
    except Exception as e:
        print(f"❌ Error loading world data: {e}")
        return
    
    nodes = world_data.get("nodes", {})
    starts = world_data.get("starts", [])
    
    print(f"📊 World statistics:")
    print(f"   - {len(nodes)} nodes")
    print(f"   - {len(starts)} start entries")
    print(f"   - {len(world_data.get('factions', []))} factions")
    
    # Perform split
    try:
        modules = split_world_into_modules(world_path, modules_dir)
        
        print(f"\n✅ Successfully created {len(modules)} modules:")
        
        total_nodes = 0
        total_starts = 0
        
        for module_id, module in modules.items():
            print(f"   📦 {module.name}")
            print(f"      - {len(module.nodes)} nodes, {len(module.starts)} starts")
            print(f"      - Tags: {', '.join(module.tags) if module.tags else 'none'}")
            print(f"      - Factions: {', '.join(module.factions) if module.factions else 'none'}")
            
            total_nodes += len(module.nodes)
            total_starts += len(module.starts)
        
        print(f"\n📈 Module summary:")
        print(f"   - Total nodes: {total_nodes}")
        print(f"   - Total starts: {total_starts}")
        print(f"   - Modules created: {len(modules)}")
        print(f"   - Files saved to: {modules_dir}")
        
        print(f"\n🎯 Next steps:")
        print(f"   1. Review individual module files in {modules_dir}")
        print(f"   2. Edit modules independently for easier content management")
        print(f"   3. Use 'Merge modules' option to rebuild world.json when ready")
        print(f"   4. Validate modules to check for broken references")
        
    except Exception as e:
        print(f"❌ Error during module creation: {e}")


def merge_modules_interactive(modules_dir: Path, world_path: Path):
    """Interactive module merging."""
    print(f"\n🔗 Merging modules from {modules_dir}...")
    
    manager = ContentModuleManager(modules_dir)
    
    try:
        modules = manager.load_modules()
        
        if not modules:
            print("❌ No modules found to merge!")
            return
        
        print(f"📦 Found {len(modules)} modules to merge:")
        for module_id, module in modules.items():
            print(f"   - {module.name}: {len(module.nodes)} nodes, {len(module.starts)} starts")
        
        # Create backup of existing world.json
        if world_path.exists():
            backup_path = world_path.with_suffix(".json.pre-merge-backup")
            if not backup_path.exists():
                with open(world_path, 'r', encoding='utf-8') as src:
                    with open(backup_path, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
                print(f"💾 Created backup: {backup_path}")
        
        # Merge and save
        merged_world_path = manager.save_merged_world(world_path)
        
        # Load merged data for statistics
        with open(merged_world_path, 'r', encoding='utf-8') as f:
            merged_data = json.load(f)
        
        print(f"\n✅ Successfully merged modules:")
        print(f"   - Output file: {merged_world_path}")
        print(f"   - Total nodes: {len(merged_data.get('nodes', {}))}")
        print(f"   - Total starts: {len(merged_data.get('starts', []))}")
        print(f"   - Total factions: {len(merged_data.get('factions', []))}")
        print(f"   - File size: {merged_world_path.stat().st_size / 1024 / 1024:.1f}MB")
        
    except Exception as e:
        print(f"❌ Error during merge: {e}")


def validate_modules_interactive(modules_dir: Path):
    """Interactive module validation."""
    print(f"\n🔍 Validating modules in {modules_dir}...")
    
    manager = ContentModuleManager(modules_dir)
    
    try:
        modules = manager.load_modules()
        
        if not modules:
            print("❌ No modules found to validate!")
            return
        
        print(f"📦 Validating {len(modules)} modules...")
        
        validation_report = manager.validate_modules(modules)
        
        print(f"\n📊 Validation Results:")
        print(f"   - Modules checked: {validation_report['modules_checked']}")
        print(f"   - Total nodes: {validation_report['statistics']['total_nodes']}")
        print(f"   - Modules with errors: {validation_report['statistics']['modules_with_errors']}")
        print(f"   - Overall status: {'✅ VALID' if validation_report['statistics']['is_valid'] else '❌ INVALID'}")
        
        if validation_report["errors"]:
            print(f"\n❌ Errors found ({len(validation_report['errors'])}):")
            for error in validation_report["errors"][:10]:  # Show first 10
                print(f"   - {error}")
            
            if len(validation_report["errors"]) > 10:
                print(f"   ... and {len(validation_report['errors']) - 10} more errors")
        
        if validation_report["warnings"]:
            print(f"\n⚠️  Warnings ({len(validation_report['warnings'])}):")
            for warning in validation_report["warnings"][:5]:  # Show first 5
                print(f"   - {warning}")
        
        if validation_report["statistics"]["is_valid"]:
            print(f"\n✅ All modules are valid! No broken references found.")
        else:
            print(f"\n❌ Validation failed. Fix the errors above before merging.")
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")


def show_module_statistics(modules_dir: Path):
    """Show detailed module statistics."""
    print(f"\n📈 Module Statistics for {modules_dir}")
    
    manager = ContentModuleManager(modules_dir)
    
    try:
        modules = manager.load_modules()
        
        if not modules:
            print("❌ No modules found!")
            return
        
        print(f"\n📦 Module Overview ({len(modules)} modules):")
        print("-" * 80)
        
        total_nodes = 0
        total_starts = 0
        
        for module_id, module in sorted(modules.items()):
            print(f"📁 {module.name} ({module_id})")
            print(f"   Description: {module.description}")
            print(f"   Content: {len(module.nodes)} nodes, {len(module.starts)} starts")
            
            if module.tags:
                print(f"   Tags: {', '.join(module.tags)}")
            
            if module.factions:
                print(f"   Factions: {', '.join(module.factions)}")
            
            if module.dependencies:
                print(f"   Dependencies: {', '.join(module.dependencies)}")
            
            total_nodes += len(module.nodes)
            total_starts += len(module.starts)
            print()
        
        print("-" * 80)
        print(f"📊 Totals:")
        print(f"   Total nodes: {total_nodes}")
        print(f"   Total starts: {total_starts}")
        print(f"   Average nodes per module: {total_nodes / len(modules):.1f}")
        print(f"   Largest module: {max(modules.values(), key=lambda m: len(m.nodes)).name} ({max(len(m.nodes) for m in modules.values())} nodes)")
        print(f"   Smallest module: {min(modules.values(), key=lambda m: len(m.nodes)).name} ({min(len(m.nodes) for m in modules.values())} nodes)")
        
        # Show module files
        print(f"\n📄 Module Files:")
        for module_file in sorted(modules_dir.glob("*.json")):
            size_kb = module_file.stat().st_size / 1024
            print(f"   {module_file.name}: {size_kb:.1f}KB")
        
    except Exception as e:
        print(f"❌ Error generating statistics: {e}")


if __name__ == "__main__":
    main()