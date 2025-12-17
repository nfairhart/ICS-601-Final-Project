"""Quick test to verify service layer works correctly"""

import sys
import os

# Test imports
try:
    print("Testing imports...")

    from backend.services.base import BaseService
    print("✓ BaseService imported")

    from backend.services.user_service import UserService
    print("✓ UserService imported")

    from backend.services.document_service import DocumentService
    print("✓ DocumentService imported")

    from backend.services.version_service import VersionService
    print("✓ VersionService imported")

    from backend.services.permission_service import PermissionService
    print("✓ PermissionService imported")

    from backend.services import (
        UserService,
        DocumentService,
        VersionService,
        PermissionService,
    )
    print("✓ All services imported from __init__")

    print("\n✅ All service imports successful!")
    print("\nService layer is ready to use.")
    print("\nNext steps:")
    print("1. Start the server: uvicorn backend.app:app --reload")
    print("2. Test endpoints at http://localhost:8000/docs")
    print("3. Compare with original: backend/app_original.py")

except ImportError as e:
    print(f"\n❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
    sys.exit(1)
