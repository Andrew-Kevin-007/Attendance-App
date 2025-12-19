"""
Quick test script to verify all backend imports work correctly.
Run this from the backend/ directory: python test_imports.py
"""

import sys
import os

# Add backend root to path
backend_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_root)

def test_imports():
    print("Testing backend imports...")
    
    try:
        print("✓ Testing face_utils import...", end=" ")
        import face_utils
        print("SUCCESS")
    except ImportError as e:
        print(f"FAILED: {e}")
        return False
    
    try:
        print("✓ Testing database import...", end=" ")
        import database
        print("SUCCESS")
    except ImportError as e:
        print(f"FAILED: {e}")
        return False
    
    try:
        print("✓ Testing models import...", end=" ")
        import models
        print("SUCCESS")
    except ImportError as e:
        print(f"FAILED: {e}")
        return False
    
    try:
        print("✓ Testing flask_app import...", end=" ")
        import flask_app
        print("SUCCESS")
    except ImportError as e:
        print(f"FAILED: {e}")
        return False
    
    try:
        print("✓ Testing app.main import...", end=" ")
        from app import main
        print("SUCCESS")
    except ImportError as e:
        print(f"FAILED: {e}")
        return False
    
    try:
        print("✓ Testing app.routers.attendance import...", end=" ")
        from app.routers import attendance
        print("SUCCESS")
    except ImportError as e:
        print(f"FAILED: {e}")
        return False
    
    print("\n✅ All imports successful!")
    return True

if __name__ == "__main__":
    success = test_imports()
    sys.exit(0 if success else 1)
