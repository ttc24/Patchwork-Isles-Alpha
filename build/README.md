# Patchwork Isles

**A tag/trait-driven interactive fiction game where your choices shape an entire archipelago**

[![CI Status](https://github.com/your-org/Patchwork-Isles/workflows/CI/badge.svg)](https://github.com/your-org/Patchwork-Isles/actions)
[![Release](https://img.shields.io/github/v/release/your-org/Patchwork-Isles)](https://github.com/your-org/Patchwork-Isles/releases)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **🎮 [Download for Windows](https://github.com/your-org/Patchwork-Isles/releases/latest)** | **📚 [Player Guide](docs/PLAYER_GUIDE.md)** | **🐛 [Report Issues](https://github.com/your-org/Patchwork-Isles/issues)**

![Screenshot of gameplay showing character profile selection with multiple storylines and achievements](https://via.placeholder.com/800x500/2E4057/FFFFFF?text=Patchwork+Isles+%7C+Multi-Profile+Character+System+%7C+Coming+Soon)

## What Makes Patchwork Isles Special?

🏝️ **Living World**: Your reputation with five major factions affects every conversation and opportunity  
🎭 **Multi-Profile System**: Create multiple characters, each with unique story paths and unlockable origins  
🧩 **No Wrong Choices**: Every decision leads to interesting consequences, never dead ends  
🎯 **Tag-Driven Gameplay**: Build your character through gameplay, not character sheets  
♿ **Accessibility First**: Full keyboard navigation, text scaling, high contrast mode, and more  
🔄 **Legacy Progression**: Achievements carry between playthroughs, unlocking new storylines

## Quick Start

### 👥 For Players
**Just want to play?** → **[See the Player Guide](docs/PLAYER_GUIDE.md)** for installation and gameplay instructions.

### 🛠️ For Developers
1. **Install Python 3.8 or newer.** The engine is pure Python with no third-party dependencies required for runtime.
2. **Clone the repo and enter the folder.**
   ```bash
   git clone https://github.com/your-org/Patchwork-Isles.git
   cd Patchwork-Isles
   ```
3. **(Optional) Create and activate a virtual environment.**
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
4. **Install development tools (ruff, black, mypy, Pillow for placeholder art).**
   ```bash
   python -m pip install -r requirements-dev.txt
   ```
   > If you only want to play, you can skip installing dev tools.
5. **Run the engine.**
   ```bash
   python engine/engine_min.py world/world.json
   ```
6. **Validate content before committing changes.**
   ```bash
   python tools/validate.py
   ```

## Folder Map
| Path | What lives here |
| --- | --- |
| `engine/` | The minimal interactive fiction engine (`engine_min.py`). |
| `world/` | Narrative content including `world.json` and modular story beats. |
| `docs/` | Lore bible, prompts, planning notes, and other supporting reference material. |
| `tools/` | Authoring utilities (`validate.py`, `list_unreachable.py`, `merge_modules.py`, etc.). |
| `playtests/` | Session transcripts and QA notes. |
| `profile.json` | Local save data storing unlocked starts and seen endings. |

## 🎆 What's New in v1.0

- ✅ **Multi-Profile Character System**: Create and manage multiple characters with progress tracking
- ✅ **Enhanced Accessibility**: Text speed, high contrast, large text, and pause-after-text options
- ✅ **Improved Session History**: Paginated story review with search and navigation
- ✅ **Automated CI/CD**: Continuous integration with content validation, linting, and automated releases
- ✅ **Executable Packaging**: One-click Windows executable with PyInstaller
- ✅ **Structured Feedback System**: Issue templates for bugs and playtest feedback
- ✅ **Performance Optimizations**: Memory management for long sessions and large save files
- ✅ **Enhanced Error Handling**: User-friendly error messages and graceful recovery

### 🔮 Coming Next
- 🔍 **Expanded Content**: Additional storylines and faction interactions
- 🎼 **Audio System**: Music and sound effects with accessibility considerations  
- 🌍 **Localization**: Multi-language support framework
- 🔧 **Mod Support**: Enhanced tools for community content creation

## Authoring Quick Reference
- **Gate a choice by Tag:**
  ```json
  "condition": {"type": "has_tag", "value": "Sneaky"}
  ```
- **Require multiple Tags (ALL-of):**
  ```json
  "condition": {"type": "has_tag", "value": ["Weaver", "Diplomat"]}
  ```
- **Reward a Tag or Trait:**
  ```json
  {"type": "add_tag", "value": "Judge"}
  {"type": "add_trait", "value": "People-Reader"}
  ```
- **Use Reputation gates/rewards:**
  ```json
  "condition": {"type": "rep_at_least", "faction": "Root Court", "value": 1}
  {"type": "rep_delta", "faction": "Wind Choirs", "value": 1}
  ```
- **End the story:**
  ```json
  {"type": "end_game", "value": "Hidden Docks Escape"}
  ```
- **Unlock a new start:**
  1. Author the start entry in `world/world.json` with `locked: true`, a `locked_title`, and the destination `node`.
  2. Deliver the unlock via an `on_enter` reward node with `{ "type": "unlock_start", "value": "your_start_id" }`.
  3. Playtest the loop, run `python tools/validate.py`, and update any lists that track available origins.

> Always author at least one "tagless" path (e.g., trade an item or spend faction favor) so players are never hard-locked.

## Filing Bugs & Contributing
- Read the [Code of Conduct](CODE_OF_CONDUCT.md) and [Contributing Guide](CONTRIBUTING.md) before opening pull requests.
- Use the issue templates under `.github/ISSUE_TEMPLATE/` so we can triage bug, feature, and balance requests quickly.
- Track shipped features and fixes in the [Changelog](CHANGELOG.md).

## License
Patchwork Isles is released under the [MIT License](LICENSE).
