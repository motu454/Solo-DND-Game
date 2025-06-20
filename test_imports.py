# test_imports.py
"""Test all imports to verify setup"""

import sys
from pathlib import Path

# Add src to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))


def test_external_packages():
    """Test external package imports"""
    print("📦 Testing external packages...")

    try:
        import markdown  # Note: lowercase 'markdown', not 'Markdown'
        print("✅ markdown imported successfully")
    except ImportError as e:
        print(f"❌ markdown import failed: {e}")
        return False

    try:
        import anthropic
        print("✅ anthropic imported successfully")
    except ImportError as e:
        print(f"❌ anthropic import failed: {e}")
        return False

    try:
        import pydantic
        print("✅ pydantic imported successfully")
    except ImportError as e:
        print(f"❌ pydantic import failed: {e}")
        return False

    try:
        from dotenv import load_dotenv
        print("✅ python-dotenv imported successfully")
    except ImportError as e:
        print(f"❌ python-dotenv import failed: {e}")
        return False

    return True


def test_project_modules():
    """Test project module imports"""
    print("\n🏗️ Testing project modules...")

    try:
        from campaign.models import Character, NPC, GameSession
        print("✅ campaign.models imported successfully")
    except ImportError as e:
        print(f"❌ campaign.models import failed: {e}")
        return False

    try:
        from config.settings import Settings, get_settings
        print("✅ config.settings imported successfully")
    except ImportError as e:
        print(f"❌ config.settings import failed: {e}")
        return False

    try:
        from game.dice import DiceRoller
        print("✅ game.dice imported successfully")
    except ImportError as e:
        print(f"❌ game.dice import failed: {e}")
        return False

    return True


def test_file_structure():
    """Test that required files exist"""
    print("\n📁 Testing file structure...")

    required_files = [
        "src/campaign/models.py",
        "src/config/settings.py",
        "src/game/dice.py",
        "src/campaign/session_manager.py",
        "src/game/character_creation.py"
    ]

    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
            print(f"❌ Missing: {file_path}")
        else:
            print(f"✅ Found: {file_path}")

    return len(missing_files) == 0


def main():
    """Run all import tests"""
    print("🧪 Testing Fey Bargain Game Imports")
    print("=" * 50)

    # Test external packages
    external_ok = test_external_packages()

    # Test file structure
    files_ok = test_file_structure()

    # Test project modules (only if files exist)
    if files_ok:
        modules_ok = test_project_modules()
    else:
        modules_ok = False
        print("\n⚠️ Skipping module tests due to missing files")

    # Python environment info
    print("\n🐍 Python environment info:")
    print(f"Python executable: {sys.executable}")
    print(f"Python version: {sys.version}")
    print(
        f"Virtual env active: {hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)}")
    print(f"Working directory: {Path.cwd()}")
    print(f"Project root: {project_root}")

    # Summary
    print("\n" + "=" * 50)
    if external_ok and files_ok and modules_ok:
        print("✅ All imports successful! Setup is working correctly.")
        return True
    else:
        print("❌ Some imports failed. Check the errors above.")
        if not external_ok:
            print("   → Install missing packages: pip install markdown anthropic pydantic python-dotenv")
        if not files_ok:
            print("   → Some project files are missing")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)