#!/usr/bin/env python3
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
    print(f"Patchwork Isles v1.0.0 - Setup")
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
        print(f"❌ Error installing dependencies: {e}")
        return False

def verify_installation():
    """Verify that the game can start."""
    print("\n🧪 Verifying installation...")
    
    try:
        # Try importing the main engine
        sys.path.insert(0, str(Path(__file__).parent / "engine"))
        import engine_min
        print("✅ Game engine loads successfully!")
        return True
    except ImportError as e:
        print(f"❌ Failed to import game engine: {e}")
        return False
    except Exception as e:
        print(f"❌ Verification error: {e}")
        return False

def main():
    """Main setup function."""
    print_header()
    
    if not install_dependencies():
        print("\n❌ Setup failed. Please check the error messages above.")
        input("Press Enter to exit...")
        sys.exit(1)
    
    if not verify_installation():
        print("\n⚠️  Installation verification failed.")
        print("The game may still work, but there might be issues.")
    
    print("\n🎉 Setup completed!")
    print("\nTo start the game:")
    print("  • On Windows: Double-click PatchworkIsles.bat")
    print("  • On Mac/Linux: Run 'python patchwork_isles.py'")
    print()
    input("Press Enter to exit...")

if __name__ == "__main__":
    main()
