# Changelog

All notable changes to Patchwork Isles will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-14 🎆 **MAJOR POLISH UPDATE**

### ✨ Added
- **Enhanced UI System**: Rich terminal formatting with colors, styles, and animations
  - Interactive menus with hotkeys and keyboard navigation
  - Typewriter text effects for immersive storytelling
  - Progress bars and loading animations
  - Fancy text boxes and panels
  - Theme support (default and dark themes)
  
- **Professional Packaging**: Complete build and distribution system
  - Automated build script (`build_package.py`)
  - Windows batch launcher (`PatchworkIsles.bat`)
  - Cross-platform Python launcher
  - Setup script for dependency installation
  - ZIP distribution packages
  - Professional README and documentation
  
- **Comprehensive Testing Framework**
  - Unit tests for core engine functionality
  - Integration tests for content validation
  - Schema validation tests
  - Profile manager tests
  - Test runner with detailed reporting
  
- **Improved Dependencies**
  - Added `jsonschema` for content validation
  - Added `colorama` for cross-platform colors
  - Added `rich` for enhanced terminal UI
  - Added `psutil` for performance monitoring

### 🔧 Improved
- **Content Validation**: Full schema validation with detailed error reporting
- **Error Handling**: More robust error handling and user-friendly messages  
- **Performance**: Optimized loading and validation processes
- **Documentation**: Enhanced README with detailed setup instructions

### 🐛 Fixed
- **Schema Validation**: Updated schema to support all condition and effect types
- **Content References**: All broken node references identified and documented
- **Import Issues**: Resolved module import problems in test framework

### 📁 Infrastructure
- **Modular Content System**: Split world.json into manageable modules (75 modules created)
- **State Management**: Advanced state tracking with history and snapshots
- **Build System**: Automated packaging and distribution
- **Testing**: Comprehensive test coverage framework established

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]
### Added
- Repository scaffolding: README, code of conduct, contributing guide, changelog, license, and issue templates.
- Development tooling configuration for Black, Ruff, and Mypy, plus dev requirements list.
- Planning backlog for the `v0.9 Beta` milestone.
- Persistent options menu with audio, display, and UI scale settings saved to `settings.json`.

## [0.1.0] - 2025-09-26
### Added
- Minimal tag/trait interactive fiction engine with save support.
- Patchwork Isles world data, authoring tools, and playtest transcripts.
