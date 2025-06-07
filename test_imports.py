try:
    import markdown
    print("✅ markdown imported successfully")
except ImportError as e:
    print(f"❌ markdown import failed: {e}")

try:
    from src.campaign.models import NPC
    print("✅ models imported successfully")
except ImportError as e:
    print(f"❌ models import failed: {e}")

print("🐍 Python path check:")
import sys
print(f"Python executable: {sys.executable}")
print(f"Virtual env active: {hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)}")