# WARP.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

Patchwork Isles is a **tag/trait-driven narrative engine** for interactive fiction. It creates **deterministic political intrigue** stories across a living archipelago where player choices unlock new paths based on accumulated tags, traits, and faction relationships.

The engine is built in **pure Python 3.8+** with no runtime dependencies, using a modular JSON-based world format for authoring branching narratives.

## Development Commands

### Essential Commands
```powershell
# Run the game/engine
python engine/engine_min.py world/world.json

# Validate world content (critical before commits)
python tools/validate.py

# Install development tools
python -m pip install -r requirements-dev.txt

# Setup virtual environment (recommended)
python -m venv .venv
# PowerShell activation:
.\.venv\Scripts\Activate.ps1
# CMD activation:
.\.venv\Scripts\activate.bat
```

### Code Quality & Testing
```powershell
# Format code
black engine/ tools/ --line-length 100

# Lint code
ruff check engine/ tools/

# Type checking
mypy engine/ tools/

# Find unreachable story nodes
python tools/list_unreachable.py world/world.json

# Merge modular story content (if using modules)
python tools/merge_modules.py --world world/world.json --modules world/modules
```

### Running Single Tests
Since this is primarily a narrative engine without a traditional test suite, validation focuses on content integrity:

```powershell
# Validate specific world file
python tools/validate.py path/to/specific/world.json

# Check story connectivity
python tools/list_unreachable.py path/to/world.json

# Run engine with different world files for testing
python engine/engine_min.py path/to/test-world.json
```

## Architecture Overview

### Core Engine Structure

**`engine/engine_min.py`** - The heart of the system. Contains:
- **GameState class**: Manages player state (tags, traits, inventory, faction rep, flags)
- **Condition system**: Evaluates story gates (`has_tag`, `rep_at_least`, `flag_eq`, etc.)
- **Effect system**: Applies story consequences (`add_tag`, `rep_delta`, `teleport`, etc.)
- **Save/Load system**: Handles game persistence and autosave
- **Main game loop**: Node traversal, choice evaluation, and story progression

**Supporting modules**:
- `save_manager.py`: Robust save/load with backup and corruption recovery
- `settings.py`: Persistent audio/display settings with validation
- `options_menu.py`: Terminal-based settings interface

### World Content Architecture

**`world/world.json`** - The master story file containing:
- **Nodes**: Individual story beats with text, choices, and conditional logic
- **Starts**: Character origin options with starting tags/traits
- **Endings**: Named conclusion states
- **Factions**: Reputation-tracked organizations (−2 to +2 scale)
- **Advanced Tags**: Special progression markers

**Key design patterns**:
- **Tag canonicalization**: Aliases like "Diplomat"/"Emissary" resolve to single values
- **Conditional choices**: Only show options if player meets requirements
- **Faction reputation**: Bounded integer system preventing runaway values
- **Legacy tags**: Cross-playthrough progression via profile persistence

### Content Validation System

**`tools/validate.py`** - Comprehensive content checker:
- Validates all condition/effect syntax
- Checks node connectivity and reference integrity
- Ensures starts reference valid nodes
- Validates faction names and reputation ranges

**`tools/list_unreachable.py`** - Graph analysis tool:
- Maps all story nodes and choice connections
- Identifies unreachable content from available starts
- Critical for ensuring authored content is actually playable

### Modular Content System

**`tools/merge_modules.py`** - Supports splitting large worlds:
- Combines `world/modules/*.json` files into master world
- Handles node conflicts and duplicate detection
- Enables collaborative authoring of large story worlds

### Player State Management

The engine maintains rich player state:
- **Tags**: Unlocked through story choices (e.g., "Sneaky", "Emissary")
- **Traits**: Named abilities gained through play (e.g., "People-Reader")
- **Inventory**: Items collected and consumed
- **Reputation**: Faction standing on -2 to +2 scale
- **Flags**: Story state variables
- **Profile**: Cross-playthrough data (unlocked starts, legacy tags)

### Save System Design

Multi-layered persistence:
- **Autosave**: Seamless progress preservation
- **Quick save/load**: Rapid experimentation
- **Named slots**: Multiple playthrough management
- **Backup system**: Corruption recovery with user confirmation
- **Profile separation**: Character vs. meta-progression

## Content Authoring Patterns

### Conditional Logic Examples
```json
// Tag requirement (single or multiple)
{"type": "has_tag", "value": "Sneaky"}
{"type": "has_tag", "value": ["Weaver", "Diplomat"]}

// Reputation gates
{"type": "rep_at_least", "faction": "Root Assembly", "value": 1}

// Advanced tag checks (any from world's advanced_tags list)
{"type": "has_advanced_tag", "value": ["Root-Speaker", "Cartographer"]}
```

### Effect Patterns
```json
// Tag/trait rewards
{"type": "add_tag", "value": "Judge"}
{"type": "add_trait", "value": "People-Reader"}

// Faction changes
{"type": "rep_delta", "faction": "Wind Choirs", "value": 1}

// Story progression
{"type": "end_game", "value": "Hidden Docks Escape"}
{"type": "unlock_start", "value": "moon_eel_suburb"}
```

### Tool Configuration

- **Black**: 100-character line length, Python 3.8+ target
- **Ruff**: Focuses on errors, import sorting, and basic quality checks
- **MyPy**: Type checking with pretty output and error codes
- **Line width scaling**: UI scales from 50-120 characters based on settings

## Development Workflow

1. **Edit content** in `world/world.json` or `world/modules/*.json`
2. **Validate immediately** with `python tools/validate.py`
3. **Test connectivity** with `python tools/list_unreachable.py`
4. **Format code** if touching engine files
5. **Run manual playtests** with `python engine/engine_min.py`

The validation step is critical - the engine expects well-formed content and validation catches authoring errors before they break gameplay.

## Key Dependencies & Runtime Notes

- **Runtime**: Pure Python 3.8+ with no third-party dependencies for gameplay
- **Development**: Black, Ruff, MyPy, and Pillow for content authoring
- **Platform**: Cross-platform (Windows PowerShell commands shown above)
- **Save system**: Automatic backup and corruption recovery built-in
- **Profile system**: Cross-playthrough progression stored in `profile.json`
