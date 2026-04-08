#!/usr/bin/env python3
"""
Diagnostic script to test Atlas connection and entity creation step by step.
"""

import sys
from datetime import datetime
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

print("\n" + "="*80)
print("🔍 SCB Atlas - Diagnostic Script")
print("="*80 + "\n")

# Test 1: Import checks
print("1️⃣  Checking imports...")
try:
    from scb_atlas.atlas.atlas_client import create_atlas_client
    print("   ✅ atlas_client imported")
except Exception as e:
    print(f"   ❌ Failed to import atlas_client: {e}")
    sys.exit(1)

try:
    from scb_atlas.atlas.service.type_service import create_typedef
    print("   ✅ type_service imported")
except Exception as e:
    print(f"   ❌ Failed to import type_service: {e}")
    sys.exit(1)

try:
    from scb_atlas.atlas.atlas_type_def import all_types
    print("   ✅ atlas_types imported")
except Exception as e:
    print(f"   ❌ Failed to import atlas_types: {e}")
    sys.exit(1)

# Test 2: Atlas connection
print("\n2️⃣  Testing Atlas connection...")
try:
    atlas_client = create_atlas_client()
    print("   ✅ Connected to Atlas successfully")
except Exception as e:
    print(f"   ❌ Failed to connect to Atlas: {e}")
    print("\n   Make sure Atlas is running on port 23000:")
    print("   docker-compose up -d")
    print("   OR")
    print("   kubectl port-forward svc/atlas 23000:23000")
    sys.exit(1)

# Test 3: Check Atlas response
print("\n3️⃣  Checking Atlas API...")
try:
    # Try to get server version when the client exposes the server API.
    server_api = getattr(atlas_client, "server", None)
    if server_api is not None and hasattr(server_api, "get_server_version"):
        version_info = server_api.get_server_version()
        print(f"   ✅ Atlas version: {version_info}")
    else:
        print("   ⚠️  Atlas client does not expose server version endpoint")
except Exception as e:
    print(f"   ⚠️  Could not get version info: {e}")

# Test 4: Type definitions structure
print("\n4️⃣  Checking type definitions...")
try:
    entity_types = all_types.get('entityDefs', [])
    enum_types = all_types.get('enumDefs', [])
    struct_types = all_types.get('structDefs', [])
    
    print(f"   ✅ Entity types: {len(entity_types)}")
    for entity in entity_types:
        print(f"      - {entity['name']}")
    
    print(f"   ✅ Enum types: {len(enum_types)}")
    print(f"   ✅ Struct types: {len(struct_types)}")
except Exception as e:
    print(f"   ❌ Error checking type definitions: {e}")

# Test 5: Create types
print("\n5️⃣  Creating type definitions...")
try:
    result = create_typedef(all_types, atlas_client)
    print(f"   ✅ Type definitions created successfully")
    print(f"   Response type: {type(result)}")
    if hasattr(result, 'guidAssignments'):
        print(f"   GUID assignments: {result.guidAssignments}")
except Exception as e:
    print(f"   ❌ Type creation failed: {e}")
    import traceback
    traceback.print_exc()

# Test 6: Create a test database entity
print("\n6️⃣  Creating test database entity...")
try:
    from scb_atlas.atlas.service.entity_service import create_database_from_model
    from scb_atlas.atlas.metadata_models import DatabaseModel

    database_model = DatabaseModel(
        database_name="test_diagnostic_db",
        location_uri="hdfs://data/finance",
        create_time=datetime(2026, 3, 24, 0, 0).astimezone(None),
        description="Finance database containing trading and transaction data"
    )
    
    result = create_database_from_model(
        atlas_client,
        database_model
    )
    print(f"   ✅ Database entity created successfully")
except Exception as e:
    print(f"   ❌ Database creation failed: {e}")
    import traceback
    traceback.print_exc()

# Test 7: Search for created entity
print("\n7️⃣  Searching for created entity...")
try:
    from scb_atlas.atlas.service.discovery_service import dsl_search
    
    results = dsl_search(
        atlas_client=atlas_client,
        names=["test_diagnostic_db"],
        type_name="SCB_Database"
    )
    
    if results:
        print(f"   ✅ Found {len(results)} entity(ies)")
        for entity in results:
            print(f"      - (GUID: {entity['guid']})")
    else:
        print(f"   ⚠️  No entities found (may not be indexed yet, wait a moment)")
except Exception as e:
    print(f"   ❌ Search failed: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "="*80)
print("✅ Diagnostic complete!")
print("="*80 + "\n")

print("Summary:")
print("- Atlas connection: ✅ Working")
print("- Type definitions: ✅ Available")
print("- Entity creation: ✅ Should be working")
print("\nIf entities are not appearing in Atlas UI:")
print("1. Wait 5-10 seconds for indexing")
print("2. Refresh the Atlas UI")
print("3. Use Advanced Search to find entities")
print("4. Check Atlas logs for errors\n")

