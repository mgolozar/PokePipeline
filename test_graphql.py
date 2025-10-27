"""Quick test to verify GraphQL module works."""

import sys
import os

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import and run
try:
    from scripts.graphql_min import app
    print("✓ GraphQL module imported successfully")
    print(f"✓ App object: {app}")
    print("\nTo run the server, execute:")
    print("  python scripts/graphql_min.py")
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

