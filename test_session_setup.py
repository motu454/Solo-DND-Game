# test_session_setup.py
"""
Test script to verify session management setup
Run this to check if everything is working correctly
"""

import asyncio
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, "src")


def test_imports():
    """Test that all modules can be imported"""
    print("🧪 Testing imports...")

    try:
        from src.config.settings import Settings, get_settings
        print("✅ Settings module imported")

        from src.campaign.models import Character, GameSession, DiceRoll
        print("✅ Models module imported")

        from src.game.dice import DiceRoller, DiceUtils
        print("✅ Dice module imported")

        from src.campaign.session_manager import SessionManager
        print("✅ Session manager imported")

        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False


def test_configuration():
    """Test configuration setup"""
    print("\n🔧 Testing configuration...")

    try:
        from src.config.settings import get_settings
        settings = get_settings()

        print(f"✅ Settings loaded successfully")
        print(f"   Campaign path: {settings.campaign_files_path}")
        print(f"   Sessions path: {settings.sessions_directory}")
        print(f"   Debug mode: {settings.debug}")

        # Check if API key is set
        if settings.anthropic_api_key:
            print(f"✅ API key is configured")
        else:
            print(f"⚠️  API key not configured (set MOCK_AI_RESPONSES=True for testing)")

        return True
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False


def test_dice_system():
    """Test dice rolling system"""
    print("\n🎲 Testing dice system...")

    try:
        from src.game.dice import DiceRoller, DiceUtils

        roller = DiceRoller()

        # Test basic roll
        result = roller.roll_dice("1d20+5")
        print(f"✅ Basic roll (1d20+5): {result.total}")

        # Test advantage
        adv_result = roller.roll_dice("1d20", advantage=True)
        print(f"✅ Advantage roll: {adv_result.total}")

        # Test skill check
        success, roll = roller.roll_skill_check(difficulty_class=15, modifier=3)
        print(f"✅ Skill check (DC 15, +3): {roll.total} ({'Success' if success else 'Failure'})")

        # Test utilities
        avg = DiceUtils.calculate_average("2d6+3")
        min_val, max_val = DiceUtils.calculate_range("2d6+3")
        print(f"✅ Dice utilities: 2d6+3 avg={avg}, range={min_val}-{max_val}")

        return True
    except Exception as e:
        print(f"❌ Dice system error: {e}")
        return False


def test_character_creation():
    """Test character creation"""
    print("\n👤 Testing character creation...")

    try:
        from src.campaign.models import Character

        # Create test character
        character = Character(
            name="Test Hero",
            level=3,
            hit_points=25,
            max_hit_points=30,
            strength=14,
            dexterity=16,
            constitution=13,
            intelligence=12,
            wisdom=15,
            charisma=10
        )

        # Test methods
        str_mod = character.get_modifier(character.strength)
        print(f"✅ Character created: {character.name}")
        print(f"   Strength modifier: {str_mod}")
        print(f"   HP: {character.hit_points}/{character.max_hit_points}")
        print(f"   Alive: {character.is_alive()}")

        # Test damage
        character.take_damage(5)
        print(f"   After 5 damage: {character.hit_points}/{character.max_hit_points}")

        return True
    except Exception as e:
        print(f"❌ Character creation error: {e}")
        return False


async def test_session_manager():
    """Test session manager (basic functionality)"""
    print("\n📝 Testing session manager...")

    try:
        from src.campaign.session_manager import SessionManager

        # Create session manager
        session_manager = SessionManager()
        print("✅ Session manager created")

        # Test session listing
        sessions = session_manager.list_sessions()
        print(f"✅ Found {len(sessions)} existing sessions")

        # Test file manager
        try:
            files = session_manager.file_manager.load_campaign_files()
            print(f"✅ Loaded {len(files)} campaign files")

            for filename in list(files.keys())[:3]:  # Show first 3 files
                print(f"   📄 {filename}")

        except Exception as e:
            print(f"⚠️  Campaign files not loaded: {e}")
            print("   (This is expected if campaign_files directory doesn't exist)")

        return True
    except Exception as e:
        print(f"❌ Session manager error: {e}")
        return False


def setup_directories():
    """Create necessary directories"""
    print("\n📁 Setting up directories...")

    directories = [
        "campaign_files",
        "sessions",
        "src/config",
        "tests"
    ]

    for dir_name in directories:
        Path(dir_name).mkdir(parents=True, exist_ok=True)
        print(f"✅ Directory created/verified: {dir_name}")


def create_sample_files():
    """Create sample files for testing"""
    print("\n📄 Creating sample files...")

    # Create sample .env if it doesn't exist
    env_file = Path(".env")
    if not env_file.exists():
        sample_env = """# Sample .env file for Fey Bargain Game
ANTHROPIC_API_KEY=your_api_key_here
DEBUG=True
MOCK_AI_RESPONSES=True
CAMPAIGN_FILES_PATH=./campaign_files
SESSIONS_DIRECTORY=./sessions
"""
        env_file.write_text(sample_env)
        print("✅ Created sample .env file")
    else:
        print("✅ .env file already exists")

    # Create sample campaign file
    campaign_dir = Path("campaign_files")
    campaign_dir.mkdir(exist_ok=True)

    sample_character = campaign_dir / "character-sheet.md"
    if not sample_character.exists():
        character_content = """# Character Sheet

## Basic Information
**Name:** Test Hero
**Level:** 1
**Class:** Fighter
**Background:** Soldier

## Ability Scores
**Strength:** 16 (+3)
**Dexterity:** 14 (+2)
**Constitution:** 15 (+2)
**Intelligence:** 12 (+1)
**Wisdom:** 13 (+1)
**Charisma:** 10 (+0)

## Combat Stats
**Armor Class:** 16 (Chain Mail)
**Hit Points:** 12/12
**Speed:** 30 feet

## Skills
- Athletics +5
- Intimidation +2
- Perception +3

## Equipment
- Longsword
- Shield
- Chain mail
- Explorer's pack
- 50 gold pieces
"""
        sample_character.write_text(character_content)
        print("✅ Created sample character sheet")

    sample_reference = campaign_dir / "quick-reference.md"
    if not sample_reference.exists():
        reference_content = """# Quick Reference

## Current Status
**Location:** Starting Village
**Current Mission:** Investigate strange lights in the forest
**Party Status:** Healthy and ready for adventure

## Key NPCs
- **Mayor Thornwick** - Village leader, concerned about the disturbances
- **Elara the Wise** - Local sage who knows about fey magic

## Important Locations
- **The Whispering Woods** - Where the strange lights have been seen
- **Ancient Standing Stones** - Rumored portal to the Feywild

## Active Quests
1. Investigate the mysterious lights
2. Speak with the village elders
3. Prepare for journey into the woods
"""
        reference_content = reference_content
        sample_reference.write_text(reference_content)
        print("✅ Created sample quick reference")

    # Create __init__.py files
    init_files = [
        "src/__init__.py",
        "src/campaign/__init__.py",
        "src/ai/__init__.py",
        "src/game/__init__.py",
        "src/config/__init__.py",
        "src/cli/__init__.py"
    ]

    for init_file in init_files:
        Path(init_file).parent.mkdir(parents=True, exist_ok=True)
        Path(init_file).touch()

    print("✅ Created __init__.py files")


def check_requirements():
    """Check if required packages are installed"""
    print("\n📦 Checking requirements...")

    required_packages = [
        'anthropic',
        'pydantic',
        'dotenv'
    ]

    missing_packages = []

    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"✅ {package} is installed")
        except ImportError:
            print(f"❌ {package} is missing")
            missing_packages.append(package)

    if missing_packages:
        print(f"\n📥 To install missing packages, run:")
        print(f"pip install {' '.join(missing_packages)}")
        return False

    return True


async def run_full_test():
    """Run comprehensive test suite"""
    print("🚀 Starting Fey Bargain Game Setup Test")
    print("=" * 60)

    # Setup
    setup_directories()
    create_sample_files()

    # Check requirements
    if not check_requirements():
        print("\n❌ Please install missing packages first")
        return False

    # Run tests
    tests = [
        ("Imports", test_imports),
        ("Configuration", test_configuration),
        ("Dice System", test_dice_system),
        ("Character Creation", test_character_creation),
        ("Session Manager", test_session_manager)
    ]

    passed = 0
    total = len(tests)

    for test_name, test_func in tests:
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()

            if result:
                passed += 1
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")

    # Summary
    print("\n" + "=" * 60)
    print(f"🏁 TEST SUMMARY: {passed}/{total} tests passed")

    if passed == total:
        print("✅ All tests passed! Your setup is ready.")
        print("\n🎮 Next steps:")
        print("1. Add your Anthropic API key to .env file")
        print("2. Copy your campaign .md files to campaign_files/")
        print("3. Run: python main.py")
    else:
        print("❌ Some tests failed. Check the errors above.")
        print("\n🔧 Common solutions:")
        print("- Make sure all packages are installed: pip install -r requirements.txt")
        print("- Check your .env file configuration")
        print("- Verify file permissions")

    return passed == total


def main():
    """Main test function"""
    try:
        success = asyncio.run(run_full_test())
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n⏸️  Test interrupted by user")
        return 1
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)