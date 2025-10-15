#!/usr/bin/env python3
"""Package Patchwork Isles as a Windows executable using PyInstaller."""

import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
DIST_DIR = REPO_ROOT / "dist"
BUILD_DIR = REPO_ROOT / "build"


def clean_directories():
    """Remove old build/dist directories."""
    for directory in [DIST_DIR, BUILD_DIR]:
        if directory.exists():
            print(f"Cleaning {directory}...")
            shutil.rmtree(directory)


def install_pyinstaller():
    """Install PyInstaller if not available."""
    try:
        import PyInstaller
        print("PyInstaller already installed.")
        return True
    except ImportError:
        print("Installing PyInstaller...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            return True
        except subprocess.CalledProcessError:
            print("Failed to install PyInstaller.")
            return False


def create_executable():
    """Create the Windows executable."""
    main_script = REPO_ROOT / "engine" / "engine_min.py"
    world_file = REPO_ROOT / "world" / "world.json"
    
    if not main_script.exists():
        print(f"Main script not found: {main_script}")
        return False
    
    if not world_file.exists():
        print(f"World file not found: {world_file}")
        return False
    
    # PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",  # Single executable file
        "--windowed",  # No console window (remove this if you want console)
        "--name", "Patchwork-Isles",
        "--icon", str(REPO_ROOT / "assets" / "icon.ico") if (REPO_ROOT / "assets" / "icon.ico").exists() else None,
        "--add-data", f"{world_file};world",  # Include world.json
        "--add-data", f"{REPO_ROOT / 'docs'};docs",  # Include docs
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR),
        str(main_script)
    ]
    
    # Remove None values
    cmd = [arg for arg in cmd if arg is not None]
    
    print("Running PyInstaller...")
    print(" ".join(cmd))
    
    try:
        subprocess.check_call(cmd, cwd=REPO_ROOT)
        return True
    except subprocess.CalledProcessError as e:
        print(f"PyInstaller failed with exit code {e.returncode}")
        return False


def create_distribution():
    """Create a complete distribution package."""
    exe_file = DIST_DIR / "Patchwork-Isles.exe"
    if not exe_file.exists():
        print("Executable not found!")
        return False
    
    # Create distribution directory
    dist_name = "Patchwork-Isles-Windows"
    dist_path = DIST_DIR / dist_name
    dist_path.mkdir(exist_ok=True)
    
    # Copy executable
    shutil.copy2(exe_file, dist_path / "Patchwork-Isles.exe")
    
    # Copy essential files
    for file_name in ["README.md", "LICENSE", "CHANGELOG.md"]:
        src = REPO_ROOT / file_name
        if src.exists():
            shutil.copy2(src, dist_path / file_name)
    
    # Create launcher script for easy running
    launcher = dist_path / "play.bat"
    with launcher.open("w") as f:
        f.write("@echo off\n")
        f.write("echo Starting Patchwork Isles...\n")
        f.write("Patchwork-Isles.exe\n")
        f.write("pause\n")
    
    # Create zip file
    zip_name = f"{dist_name}.zip"
    shutil.make_archive(str(DIST_DIR / dist_name), 'zip', str(dist_path))
    
    print(f"Distribution created: {zip_name}")
    print(f"Size: {(DIST_DIR / zip_name).stat().st_size / (1024*1024):.1f} MB")
    
    return True


def main():
    """Main packaging process."""
    print("=== Patchwork Isles Windows Packaging ===")
    
    # Check we're in the right directory
    if not (REPO_ROOT / "engine" / "engine_min.py").exists():
        print("Error: Run this script from the repository root directory")
        return False
    
    # Step 1: Install PyInstaller
    if not install_pyinstaller():
        return False
    
    # Step 2: Clean old builds
    clean_directories()
    
    # Step 3: Create executable
    if not create_executable():
        print("Failed to create executable")
        return False
    
    # Step 4: Create distribution
    if not create_distribution():
        print("Failed to create distribution")
        return False
    
    print("=== Packaging Complete ===")
    print(f"Find your Windows executable in: {DIST_DIR}")
    
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)