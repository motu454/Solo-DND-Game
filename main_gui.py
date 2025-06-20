# main_gui.py - Corrected PyQt6 Desktop App Launcher
"""
Fey Bargain Game - Desktop GUI Launcher
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent
src_path = project_root / "src"
sys.path.insert(0, str(src_path))

print("🎭 Starting The Fey Bargain Game...")
print("🎮 Initializing desktop interface...")

try:
    # Import the main function from ui.main_window
    from ui.main_window import main

    if __name__ == "__main__":
        print("✅ Launching application...")
        main()

except ImportError as e:
    print(f"❌ Import Error: {e}")
    print("\n🔧 Troubleshooting:")
    print("1. Make sure PyQt6 is installed: pip install PyQt6")
    print("2. Check that src/ui/main_window.py exists")
    print("3. Verify all __init__.py files are in place")
    print("4. Make sure all required modules are in src/")
    sys.exit(1)

except Exception as e:
    print(f"❌ Error starting application: {e}")
    print("\n🔧 Common solutions:")
    print("- Check your campaign_files directory exists")
    print("- Verify your .env file has ANTHROPIC_API_KEY")
    print("- Make sure all Python dependencies are installed")
    sys.exit(1)