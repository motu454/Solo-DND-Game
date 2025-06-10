"""
The Fey Bargain Game - Main Entry Point
"""
import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv
from src.cli.game_interface import GameInterface

async def main():
    """Main application entry point"""

    # Load environment variables
    load_dotenv()

    # Check for required setup
    env_check = check_environment()
    if not env_check:
        return

    # Check campaign files
    files_check = check_campaign_files()
    if not files_check:
        return

    # Start the game
    try:
        game = GameInterface()
        await game.start_session()
    except KeyboardInterrupt:
        print("\n👋 Game interrupted. Goodbye!")
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

def check_environment() -> bool:
    """Check if environment is properly configured"""
    print("🔍 Checking environment configuration...")

    # Check API key
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found!")
        print("📝 Please:")
        print("   1. Get your API key from https://console.anthropic.com/")
        print("   2. Create a .env file in your project root")
        print("   3. Add: ANTHROPIC_API_KEY=your_key_here")
        return False

    print("✅ API key found")
    return True

def check_campaign_files() -> bool:
    """Check if campaign files directory exists"""
    campaign_dir = Path("./campaign_files")

    if not campaign_dir.exists():
        print("❌ Campaign files directory not found!")
        print("📝 Please create './campaign_files' directory with your campaign markdown files")
        return False

    # Count markdown files
    md_files = list(campaign_dir.glob("*.md"))
    print(f"📁 Found {len(md_files)} markdown files in campaign directory")

    if len(md_files) == 0:
        print("⚠️  No markdown files found in campaign directory")
        print("📝 Please add your campaign .md files to './campaign_files'")
        return False

    print("✅ Campaign files ready")
    return True

if __name__ == "__main__":
    asyncio.run(main())
