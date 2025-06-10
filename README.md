# 🎮 The Fey Bargain Game
*AI-Powered Solo D&D Campaign Manager*

[![Python Version](https://img.shields.io/badge/python-3.12+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Development Status](https://img.shields.io/badge/status-Active%20Development-orange.svg)](https://github.com/motu454/Solo-DND-Game)

Transform solo D&D from manual file management into an intelligent, AI-powered gaming experience that rivals traditional group campaigns in depth and engagement.

## 🌟 What Makes This Special

**The Fey Bargain Game** is the world's first professional-grade AI Dungeon Master application that combines sophisticated campaign management with intelligent storytelling, preserving player agency while handling the complexity that typically requires years of DM experience.

### ✨ Key Features

- 🤖 **AI-Assisted Character Creation** - Interactive character building with Claude AI guidance
- 💾 **Persistent Session Management** - Auto-save every 5 minutes, never lose progress
- 🎲 **Professional Dice System** - Full D&D 5e mechanics with advantage/disadvantage
- 📚 **24-File Campaign System** - Comprehensive campaign tracking and management
- 🎭 **Enhanced CLI Interface** - Professional command system with session management
- ⚔️ **Solo-Optimized Gameplay** - Designed specifically for single-player D&D experiences

## 🚀 Quick Start

### Prerequisites

- Python 3.12+ 
- [Anthropic API Key](https://console.anthropic.com/) (for AI features)
- 8GB+ RAM recommended

### Installation

```bash
# Clone the repository
git clone https://github.com/motu454/Solo-DND-Game.git
cd Solo-DND-Game

# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your ANTHROPIC_API_KEY
```

### First Run

```bash
# Test your setup
python test_session_setup.py

# Start the game
python main.py
```

## 🎭 Character Creation System

### AI-Assisted Creation Flow

1. **Character Concept**: Describe your character idea
   ```
   "A wise old wizard seeking forbidden knowledge"
   ```

2. **AI Analysis**: Get intelligent suggestions
   ```
   🧬 Suggested Races: High Elf, Human, Variant Human
   ⚔️ Suggested Classes: Wizard, Warlock, Sorcerer  
   📚 Suggested Backgrounds: Sage, Hermit, Noble
   ```

3. **Interactive Choices**: Step-by-step character building
   - Race selection with synergy indicators
   - Class selection with AI explanations
   - Background integration
   - Ability score assignment (multiple methods)
   - Personality development with AI suggestions

4. **Game Integration**: Seamless transition to gameplay

### Character Creation Options

- **🤖 AI-Assisted Creation** - Full interactive experience (15 minutes)
- **🎲 Quick Random Character** - Instant random generation (30 seconds)
- **📄 Template Characters** - Pre-built character examples

## 🎮 Gameplay Features

### Session Management

```bash
# Enhanced CLI Commands
save                    # Manual save current session
character / char        # Show character sheet  
roll 1d20+5            # Roll dice with modifier
r 2d6 adv              # Roll with advantage
info                   # Show session information
status                 # Show system status
```

### Session Persistence

- ✅ **Auto-save** every 5 minutes
- ✅ **Session history** with full state preservation
- ✅ **Automatic backups** of campaign files
- ✅ **Resume anywhere** - pick up exactly where you left off
- ✅ **Session statistics** - track your adventures

### Campaign Integration

The game works with a sophisticated **24-file campaign system**:

```
campaign_files/
├── character-sheet.md      # Your character's stats and progression
├── npc-directory.md        # All NPCs with relationship tracking
├── active-missions.md      # Current quests and objectives  
├── location-directory.md   # Visited and known locations
├── faction-tracker.md      # Political relationships and standings
├── campaign-timeline.md    # Major events and story progression
├── quick-reference.md      # Current status and context
└── ... (17 more specialized files)
```

## 🎲 Dice System

### D&D 5e Mechanics

```bash
# Basic rolls
roll 1d20               # Standard d20
roll 2d6+3              # Multiple dice with modifier
roll 1d8-1              # Negative modifiers

# Advantage/Disadvantage  
roll 1d20 adv           # Roll twice, take higher
roll 1d20 dis           # Roll twice, take lower

# Skill checks
# Auto-calculated with character modifiers
```

### Supported Dice Types

- ✅ All standard RPG dice (d4, d6, d8, d10, d12, d20, d100)
- ✅ Multiple dice notation (3d6, 4d6 drop lowest)
- ✅ Modifiers and complex expressions
- ✅ Critical success/failure detection
- ✅ Advantage/disadvantage mechanics

## 🤖 AI Integration

### Claude AI Features

- **Character Concept Analysis** - Turn ideas into mechanical suggestions
- **Choice Feedback** - Understand why combinations work well
- **Personality Generation** - AI-crafted traits, ideals, bonds, flaws
- **Backstory Assistance** - Coherent character histories
- **Scene Generation** - Dynamic storytelling within campaign structure

### Offline Mode

Set `MOCK_AI_RESPONSES=True` in your `.env` file to run without API access:
- Uses pre-written responses for testing
- All core functionality remains available
- Perfect for development and offline play

## 📁 Project Structure

```
Solo-DND-Game/
├── src/
│   ├── ai/                    # AI integration and context management
│   ├── campaign/              # Campaign file management and session state
│   ├── cli/                   # Command-line interfaces
│   ├── config/                # Configuration and settings
│   └── game/                  # Game mechanics (dice, character creation)
├── campaign_files/            # Your 24-file campaign system
├── sessions/                  # Saved game sessions
├── tests/                     # Test files
├── main.py                    # Application entry point
└── requirements.txt           # Python dependencies
```

## ⚙️ Configuration

### Environment Variables

```bash
# Required
ANTHROPIC_API_KEY=your_api_key_here

# Optional - Game Settings
DEBUG=True
ANTHROPIC_MODEL=claude-3-haiku-20240307
CAMPAIGN_FILES_PATH=./campaign_files
SESSIONS_DIRECTORY=./sessions
AUTO_SAVE_INTERVAL=300         # Auto-save every 5 minutes
DEFAULT_DIFFICULTY_CLASS=15    # Default skill check DC

# Optional - AI Settings  
MAX_TOKENS=2000
TEMPERATURE=0.7
MOCK_AI_RESPONSES=False        # Set to True for offline mode
```

### Advanced Configuration

The game uses **pydantic-settings** for robust configuration management. See `src/config/settings.py` for all available options.

## 🧪 Testing

```bash
# Run setup verification
python test_session_setup.py

# Check imports and basic functionality
python test_imports.py

# Manual testing checklist
python main.py
# → Test character creation (option 2)
# → Test session management
# → Test dice rolling system
# → Test save/load functionality
```

## 🛠️ Development

### Setting Up Development Environment

```bash
# Install development dependencies
pip install pytest black isort

# Run code formatting
black src/
isort src/

# Add new features
# 1. Create feature branch
# 2. Implement in appropriate src/ subdirectory  
# 3. Add tests
# 4. Update documentation
```

### Architecture Overview

The application follows a **modular architecture** inspired by infrastructure-as-code principles:

- **Campaign Layer** - File management and state persistence
- **Game Layer** - D&D mechanics and character creation  
- **AI Layer** - Claude integration and context management
- **CLI Layer** - User interface and command processing
- **Config Layer** - Environment and settings management

## 🎯 Roadmap

### Phase 1: Core Foundation ✅
- [x] Session management with persistence
- [x] AI-assisted character creation
- [x] Enhanced CLI interface
- [x] Professional dice system
- [x] Configuration management

### Phase 2: User Interface (In Progress)
- [ ] **Streamlit web interface** for rapid prototyping
- [ ] **PyQt6 desktop application** for native experience
- [ ] Visual dice rolling animations
- [ ] Character sheet editing GUI
- [ ] Session browser and management

### Phase 3: Advanced Features (Planned)
- [ ] **Mission tracking system** with automatic progress detection
- [ ] **NPC relationship visualization** with dynamic relationship graphs
- [ ] **Campaign templates** beyond Fey Bargain
- [ ] **Custom campaign creation tools**
- [ ] **Community sharing** - export/import campaigns

### Phase 4: Platform & Community (Future)
- [ ] **Mobile companion app**
- [ ] **Cloud save synchronization**
- [ ] **Campaign marketplace**
- [ ] **Multiplayer coordination tools**

## 🤝 Contributing

We welcome contributions! Here's how to get started:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Follow the coding standards** (black formatting, type hints)
4. **Add tests** for new functionality
5. **Update documentation** as needed
6. **Submit a pull request**

### Code Style

- **Python 3.12+** with type hints
- **Black** code formatting
- **Docstrings** for all public functions
- **Modular design** - keep components focused and reusable

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Anthropic** for Claude AI that powers the intelligent character creation
- **D&D 5e** for the incredible game system this enhances
- **Solo RPG Community** for inspiration and feedback
- **Open Source Contributors** who make projects like this possible

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/motu454/Solo-DND-Game/issues)
- **Discussions**: [GitHub Discussions](https://github.com/motu454/Solo-DND-Game/discussions)
- **Documentation**: [Project Wiki](https://github.com/motu454/Solo-DND-Game/wiki)

---

**Ready to revolutionize your solo D&D experience?** 🎲⚔️✨

```bash
git clone https://github.com/motu454/Solo-DND-Game.git
cd Solo-DND-Game
python main.py
```

*Transform your solo D&D from manual file management into an intelligent, AI-powered adventure that rivals traditional group campaigns!*
