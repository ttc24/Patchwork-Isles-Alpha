# Patchwork Isles - Player Guide

Welcome to **Patchwork Isles**, a tag/trait-driven interactive fiction game set in a living archipelago of political intrigue!

## Quick Start

### Easy Installation (Windows)
1. Download `Patchwork-Isles-Windows.zip` from the [Releases page](../../releases)
2. Extract the zip file to a folder
3. Double-click `play.bat` to start the game
4. That's it! No Python installation required.

### Full Installation (All Platforms)
**Requirements:** Python 3.8 or newer

```bash
# Clone the game
git clone https://github.com/your-org/Patchwork-Isles.git
cd Patchwork-Isles

# Set up virtual environment (recommended)
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On Mac/Linux:
source .venv/bin/activate

# Start playing (no additional packages needed!)
python engine/engine_min.py world/world.json
```

## How to Play

### Character Creation
1. **Choose a Profile**: Create a new character profile or continue an existing one
2. **Name Your Character**: Give your character a memorable name
3. **Select Origin**: Choose from available starting backgrounds, each with unique tags
4. **Begin Your Journey**: Start exploring the archipelago!

### Basic Controls
- **Numbers (1, 2, 3, etc.)**: Select choices by their number
- **Enter**: Select the first choice (shortcut)
- **I**: View inventory
- **T**: Check tags and traits
- **H**: Review your story history
- **P**: Pause menu (save, load, options)
- **O**: Access options/settings
- **Q**: Quit to title screen

### Game Concepts

#### Tags & Traits
- **Tags**: Skills and affiliations (Scout, Diplomat, Sneaky, etc.)
  - Unlock special choices throughout the story
  - Gained from starting origins and story decisions
  - Multiple tags can be combined for powerful effects

- **Traits**: Special abilities earned through play
  - **People-Reader**: Reveals hidden social insights
  - **Light-Step**: Bypass certain obstacles with agility
  - **Well-Provisioned**: Access to supply caches and favors
  - **Rememberer's Boon**: Rewrite parts of your history

#### Faction Reputation
Build relationships with five major factions:
- **Aeol Nests**: Sky-dwelling navigators and storm-riders
- **Root Assembly**: Arboreal bureaucrats and legal scholars
- **Prism Cartel**: Light engineers and technological innovators
- **Freehands**: Cooperative smugglers and mutual aid networks
- **Quiet Ledger**: Information brokers and archivists

Reputation ranges from -2 (hostile) to +2 (allied). Higher reputation unlocks new storylines and resources.

#### Progression System
- **Legacy Tags**: Carry achievements between playthroughs
- **Unlockable Origins**: Discover new starting positions through play
- **Multiple Endings**: Each story path has meaningful conclusions
- **Branching Narratives**: Choices affect both immediate scenes and long-term plot development

### Tips for New Players

#### Getting Started
1. **Try the Tutorial**: Start with "First Five Minutes (Tutorial Island)" to learn the mechanics
2. **Experiment**: There are no "wrong" choices, just different stories
3. **Save Often**: Use **S** for quick saves at important decision points
4. **Read Carefully**: Story details matter for understanding consequences

#### Making Choices
- **Tag-Gated Options**: Look for choices marked with your tags (Scout, Diplomat, etc.)
- **Reputation Matters**: Build relationships to access faction-specific storylines
- **Always Have Alternatives**: Every situation has multiple solutions
- **Think Long-Term**: Some choices have consequences chapters later

#### Exploring Content
- **Multiple Playthroughs**: Different origins lead to completely different experiences
- **Unlock New Starts**: Completing certain storylines opens new character backgrounds
- **Collect Endings**: Each conclusion reveals different aspects of the world
- **History Review**: Use **H** to review your journey and understand patterns

## Accessibility Features

### Text and Display
- **Large Text Mode**: Shorter lines and clearer formatting
- **High Contrast Mode**: Enhanced visual separation of UI elements
- **Adjustable Text Speed**: Slow down or speed up text display
- **Pause After Text**: Add breaks between paragraphs for easier reading

### Interface Options
- **UI Scaling**: Adjust interface size from 50% to 200%
- **Multiple Save Slots**: Organize different characters and experiments
- **Session History**: Review your recent choices with pagination
- **Keyboard-Only Play**: No mouse required for any game functions

### Audio Settings (Future)
- Master, music, and sound effect volume controls
- Audio cues for important game state changes

Access all accessibility options by pressing **O** in-game or from the profile selection screen.

## Troubleshooting

### Common Issues

**"World file not found"**
- Make sure you're running the command from the `Patchwork-Isles` directory
- Check that `world/world.json` exists in your installation

**"Module not found" errors**
- Ensure you activated your virtual environment
- Try reinstalling: `pip install -r requirements-dev.txt`

**Save/load problems**
- Check file permissions in your game directory
- Try creating a new profile if saves are corrupted

**Game crashes or freezes**
- Press Ctrl+C to safely exit
- Report bugs with steps to reproduce on the GitHub Issues page

### Performance Tips
- The game automatically manages memory for long sessions
- Use quick saves (**S**) rather than full saves for better performance
- If history gets very long, it's automatically trimmed to maintain responsiveness

### Getting Help
1. **Check the README**: Basic setup and development information
2. **Review Issue Templates**: Structured bug reports and feedback forms
3. **Validation Tools**: Run `python tools/validate.py` to check for content issues
4. **Community**: Share experiences and get help from other players

## Advanced Features

### For Content Creators
- **Modding Support**: JSON-based content format for easy modification
- **Validation Tools**: Built-in content checking and error detection
- **Module System**: Split large stories into manageable chunks
- **Open Source**: Full access to engine code and development tools

### Developer Mode
If you're interested in development:
```bash
# Install development tools
pip install -r requirements-dev.txt

# Validate content
python tools/validate.py world/world.json

# Check connectivity
python tools/list_unreachable.py world/world.json

# Format code
black engine/ tools/ --line-length 100
```

## What's Next?

- **Explore Different Origins**: Each starting background offers a unique perspective
- **Build Faction Alliances**: Deep relationships unlock exclusive storylines
- **Discover Hidden Paths**: Certain combinations of tags/traits reveal secret content
- **Master the Meta-Game**: Use legacy tags and unlocked origins strategically
- **Share Your Stories**: Join the community to discuss favorite moments and strategies

Ready to begin your journey through the Patchwork Isles? The archipelago awaits your choices!

---

**Need Help?** Check our [GitHub Issues](../../issues) for bug reports and feedback, or review the [full README](../../README.md) for development information.