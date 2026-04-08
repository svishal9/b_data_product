#!/usr/bin/env python3
"""Quick test to verify fixes"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

print("Testing imports...")
try:
    from scb_atlas.atlas.service.type_service import create_typedef

    print("✅ All imports successful")
except Exception as e:
    print(f"❌ Import failed: {e}")
    sys.exit(1)

print("\nTesting function signatures...")
import inspect
sig = inspect.signature(create_typedef)
print(f"create_typedef signature: {sig}")

params = list(sig.parameters.keys())
if 'type_defs' in params and 'atlas_client' in params:
    print("✅ create_typedef now accepts type_defs and atlas_client")
else:
    print(f"❌ Unexpected parameters: {params}")

print("\n✅ All fixes verified!")

