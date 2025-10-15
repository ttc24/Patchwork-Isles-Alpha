#!/usr/bin/env python3
"""
Professional packaging script for Patchwork Isles.
Creates standalone executables and distribution packages.
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path
from datetime import datetime

PROJECT_ROOT = Path(__file__).parent
PROJECT_NAME = "Patchwork-Isles"
VERSION = "1.0.0"
BUILD_DIR = PROJECT_ROOT / "build"
DIST_DIR = PROJECT_ROOT / "dist"

# Files and directories to include in distribution
INCLUDE_FILES = [
    "world/",
    "engine/",
    "tools/",
    "schemas/",
    "requirements.txt",
    "README.md",
    "LICENSE",
    "CHANGELOG.md"
]

EXCLUDE_PATTERNS = [
    "__pycache__/",
    "*.pyc",
    "*.pyo", 
    ".git/",
    ".venv/",
    "build/",
    "dist/",
    "*.log",
    "test_*.py",
    "profile.json",
    "saves/"
]

def print_step(message: str):
    """Print a build step message."""
    print(f"\n🔧 {message}")
    print("─" * (len(message) + 4))

def run_command(command: str, cwd=None) -> bool:
    """Run a command and return success status."""
    try:
        result = subprocess.run(
            command,
            shell=True,
            cwd=cwd or PROJECT_ROOT,
            capture_output=True,
            text=True
        )
        if result.returncode != 0:
            print(f"❌ Command failed: {command}")
            print(f"Error: {result.stderr}")
            return False
        return True
    except Exception as e:
        print(f"❌ Exception running command: {e}")
        return False

def clean_build_dirs():
    """Clean build and dist directories."""
    print_step("Cleaning build directories")
    
    for directory in [BUILD_DIR, DIST_DIR]:
        if directory.exists():
            shutil.rmtree(directory)
            print(f"  Removed {directory}")
        directory.mkdir(exist_ok=True)
        print(f"  Created {directory}")

def check_dependencies():
    """Check if required build tools are available."""
    print_step("Checking build dependencies")
    
    required_tools = {
        "python": "python --version",
        "pip": "pip --version"
    }
    
    missing_tools = []
    
    for tool, command in required_tools.items():
        if not run_command(command):
            missing_tools.append(tool)
        else:
            print(f"  ✅ {tool} is available")
    
    if missing_tools:
        print(f"❌ Missing required tools: {', '.join(missing_tools)}")
        return False
    
    return True

def create_main_launcher():
    """Create main launcher script."""
    print_step("Creating launcher script")
    
    launcher_content = f'''#!/usr/bin/env python3
"""
Patchwork Isles - Main Launcher
Version: {VERSION}
"""

import sys
import os
from pathlib import Path

# Add engine directory to Python path
game_dir = Path(__file__).parent
engine_dir = game_dir / "engine"
sys.path.insert(0, str(engine_dir))

def main():
    """Main entry point for Patchwork Isles."""
    try:
        # Import and run the main game
        from engine_min import main as game_main
        world_file = game_dir / "world" / "world.json"
        
        # Pass world file as argument
        sys.argv = ["patchwork_isles", str(world_file)]
        
        game_main()
        
    except ImportError as e:
        print(f"❌ Error importing game engine: {{e}}")
        print("Please ensure all required files are present.")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\\n👋 Thanks for playing Patchwork Isles!")
        sys.exit(0)
    except Exception as e:
        print(f"❌ Unexpected error: {{e}}")
        sys.exit(1)

if __name__ == "__main__":
    main()
'''
    
    launcher_path = BUILD_DIR / "patchwork_isles.py"
    with open(launcher_path, 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    print(f"  Created launcher: {launcher_path}")
    return launcher_path

def copy_game_files():
    """Copy game files to build directory."""
    print_step("Copying game files")
    
    for item in INCLUDE_FILES:
        src = PROJECT_ROOT / item
        dst = BUILD_DIR / item
        
        if not src.exists():
            print(f"  ⚠️  Skipping missing file: {src}")
            continue
        
        if src.is_dir():
            # Copy directory, excluding certain patterns
            shutil.copytree(
                src, dst,
                ignore=shutil.ignore_patterns(*EXCLUDE_PATTERNS)
            )
            print(f"  📁 Copied directory: {item}")
        else:
            # Copy file
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            print(f"  📄 Copied file: {item}")

def create_batch_launcher():
    """Create Windows batch launcher."""
    print_step("Creating Windows batch launcher")
    
    batch_content = f'''@echo off
title Patchwork Isles v{VERSION}
echo Starting Patchwork Isles...
echo.

cd /d "%~dp0"
python patchwork_isles.py
if errorlevel 1 (
    echo.
    echo ❌ Error running Patchwork Isles
    echo Make sure Python 3.8+ is installed and in your PATH
    pause
)
'''
    
    batch_path = BUILD_DIR / "PatchworkIsles.bat"
    with open(batch_path, 'w', encoding='utf-8') as f:
        f.write(batch_content)
    
    print(f"  Created batch launcher: {batch_path}")

def create_setup_script():
    """Create setup script for dependencies."""
    print_step("Creating setup script")
    
    setup_content = f'''#!/usr/bin/env python3
"""
Setup script for Patchwork Isles
Installs required dependencies and verifies installation.
"""

import subprocess
import sys
import os
from pathlib import Path

def print_header():
    print("=" * 60)
    print(f"Patchwork Isles v{VERSION} - Setup")
    print("=" * 60)
    print()

def install_dependencies():
    """Install required dependencies."""
    print("📦 Installing dependencies...")
    
    try:
        result = subprocess.run([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ], capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Dependencies installed successfully!")
            return True
        else:
            print("❌ Failed to install dependencies:")
            print(result.stderr)
            return False
            
    except Exception as e:
        print(f"❌ Error installing dependencies: {{e}}")
        return False

def verify_installation():
    """Verify that the game can start."""
    print("\\n🧪 Verifying installation...")
    
    try:
        # Try importing the main engine
        sys.path.insert(0, str(Path(__file__).parent / "engine"))
        import engine_min
        print("✅ Game engine loads successfully!")
        return True
    except ImportError as e:
        print(f"❌ Failed to import game engine: {{e}}")
        return False
    except Exception as e:
        print(f"❌ Verification error: {{e}}")
        return False

def main():
    """Main setup function."""
    print_header()
    
    if not install_dependencies():
        print("\\n❌ Setup failed. Please check the error messages above.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    if not verify_installation():
        print("\\n⚠️  Installation verification failed.")
        print("The game may still work, but there might be issues.")
    
    print("\\n🎉 Setup completed!")
    print("\\nTo start the game:")
    print("  • On Windows: Double-click PatchworkIsles.bat")
    print("  • On Mac/Linux: Run 'python patchwork_isles.py'")
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
'''
    
    setup_path = BUILD_DIR / "setup.py"
    with open(setup_path, 'w', encoding='utf-8') as f:
        f.write(setup_content)
    
    print(f"  Created setup script: {setup_path}")

def create_readme():
    """Create distribution README."""
    print_step("Creating distribution README")
    
    readme_content = f'''# Patchwork Isles v{VERSION}

A tag/trait-driven interactive fiction game where your choices shape an entire archipelago.

## Quick Start

### Windows Users
1. Double-click `PatchworkIsles.bat` to start the game
2. If you encounter issues, run `setup.py` first

### Mac/Linux Users  
1. Ensure Python 3.8+ is installed
2. Run `python setup.py` to install dependencies
3. Run `python patchwork_isles.py` to start the game

## Game Features

🏝️ **Living World**: Your reputation with factions affects every interaction
🎭 **Multi-Profile System**: Create multiple characters with unique story paths  
🧩 **No Wrong Choices**: Every decision leads to interesting consequences
🎯 **Tag-Driven Gameplay**: Build your character through choices, not stats
♿ **Accessibility First**: Full keyboard navigation and accessibility options
🔄 **Legacy Progression**: Achievements unlock new storylines across playthroughs

## System Requirements

- Python 3.8 or newer
- 50MB free disk space
- Windows 10+, macOS 10.14+, or Linux with terminal support

## Controls

- **Numbers (1-9)**: Select menu options
- **Letters**: Use hotkeys shown in brackets [like this]
- **ESC or P**: Pause during gameplay
- **I**: View character information
- **H**: View session history

## Troubleshooting

**Game won't start**: Run `setup.py` to install dependencies
**Text display issues**: Try the high contrast mode in Options
**Performance issues**: Close other applications and try again

For more help, visit: https://github.com/your-org/Patchwork-Isles/issues

---
Built on {datetime.now().strftime('%Y-%m-%d')} | Version {VERSION}
'''
    
    readme_path = BUILD_DIR / "README.txt"
    with open(readme_path, 'w', encoding='utf-8') as f:
        f.write(readme_content)
    
    print(f"  Created README: {readme_path}")

def create_zip_distribution():
    """Create ZIP distribution package."""
    print_step("Creating ZIP distribution")
    
    zip_name = f"{PROJECT_NAME}-v{VERSION}-Portable.zip"
    zip_path = DIST_DIR / zip_name
    
    with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
        # Add all files from build directory
        for file_path in BUILD_DIR.rglob('*'):
            if file_path.is_file():
                # Calculate relative path from build dir
                rel_path = file_path.relative_to(BUILD_DIR)
                zipf.write(file_path, rel_path)
                
        print(f"  Added {len(zipf.namelist())} files to ZIP")
    
    print(f"  Created ZIP package: {zip_path}")
    print(f"  Package size: {zip_path.stat().st_size / 1024 / 1024:.1f} MB")
    
    return zip_path

def create_installer_script():
    """Create cross-platform installer script.""" 
    print_step("Creating installer script")
    
    installer_content = f'''#!/usr/bin/env python3
"""
Patchwork Isles Installer
Extracts and sets up the game.
"""

import os
import sys
import shutil
import zipfile
from pathlib import Path

def main():
    print("🎮 Patchwork Isles v{VERSION} Installer")
    print("=" * 40)
    
    # This would contain the embedded game files
    # For now, just create a placeholder
    print("\\nThis installer would extract and set up the game.")
    print("Currently, please use the ZIP distribution instead.")
    
if __name__ == "__main__":
    main()
'''
    
    installer_path = DIST_DIR / f"{PROJECT_NAME}-v{VERSION}-Installer.py"
    with open(installer_path, 'w', encoding='utf-8') as f:
        f.write(installer_content)
    
    print(f"  Created installer: {installer_path}")

def build_summary():
    """Print build summary."""
    print_step("Build Summary")
    
    build_files = list(BUILD_DIR.rglob('*'))
    dist_files = list(DIST_DIR.rglob('*'))
    
    print(f"  📁 Build directory: {BUILD_DIR}")
    print(f"     Files created: {len([f for f in build_files if f.is_file()])}")
    
    print(f"  📦 Distribution directory: {DIST_DIR}")
    print(f"     Packages created: {len([f for f in dist_files if f.is_file()])}")
    
    total_size = sum(f.stat().st_size for f in dist_files if f.is_file())
    print(f"     Total size: {total_size / 1024 / 1024:.1f} MB")
    
    print(f"\\n✅ Build completed successfully!")
    print(f"   Version: {VERSION}")
    print(f"   Built on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def main():
    """Main build function."""
    print(f"🏗️  Building Patchwork Isles v{VERSION}")
    print("=" * 60)
    
    try:
        # Build steps
        if not check_dependencies():
            return False
        
        clean_build_dirs()
        copy_game_files()
        create_main_launcher()
        create_batch_launcher()
        create_setup_script()
        create_readme()
        
        # Distribution packages
        create_zip_distribution()
        create_installer_script()
        
        build_summary()
        return True
        
    except KeyboardInterrupt:
        print("\\n❌ Build interrupted by user")
        return False
    except Exception as e:
        print(f"\\n❌ Build failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)