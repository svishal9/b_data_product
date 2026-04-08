#!/usr/bin/env python3
"""
Setup script to create all entity types and sample entities in local Atlas.

This script:
1. Creates all type definitions (Database, Table, Column, Process, DataProduct)
2. Creates sample entities for demonstration
3. Shows how to access them in Atlas UI

Usage:
    python create_atlas_entities.py
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from scb_atlas.atlas.atlas_client import create_atlas_client
from scb_atlas.atlas.atlas_type_def import all_types
from scb_atlas.atlas.service.entity_service import (

    delete_entity,
)

def print_header(title):
    """Print formatted header."""
    print("\n" + "="*80)
    print(f"▶ {title}")
    print("="*80 + "\n")

def _extract_type_names(type_key: str) -> list[str]:
    """Return type names from Atlas typedef payload for a given definition key."""
    return [d.get("name") for d in all_types.get(type_key, []) if d.get("name")]


def _purge_entities_by_type(atlas_client, type_name: str) -> None:
    """Best-effort purge of all entities for a type before deleting that type."""
    query = f"from {type_name} limit 1000"
    result = atlas_client.discovery.dsl_search(query)
    entities = getattr(result, "entities", None) or []
    guids = [e.get("guid") for e in entities if e.get("guid")]
    if not guids:
        return

    # Deduplicate while preserving order.
    unique_guids = list(dict.fromkeys(guids))
    delete_entity(atlas_client, unique_guids)


def reset_scb_types(atlas_client) -> None:
    """Delete SCB entities and typedefs so setup can recreate them cleanly."""
    print_header("Reset: Purging Existing SCB Entities and Types")

    entity_type_names = _extract_type_names("entityDefs") 
    relationship_type_names = _extract_type_names("relationshipDefs")
    legacy_relationship_type_names = [
        "SCB_Column",
        "SCB_DataProduct_InputTables",
        "SCB_DataProduct_OutputTable",
        "SCB_DataProduct_Tables",
    ]
    classification_type_names = _extract_type_names("classificationDefs")
    struct_type_names = _extract_type_names("structDefs")
    enum_type_names = _extract_type_names("enumDefs")

    # Purge entity instances first in reverse dependency order.
    for type_name in reversed(entity_type_names):
        try:
            _purge_entities_by_type(atlas_client, type_name)
            print(f"✅ Purged entities for type: {type_name}")
        except Exception as e:
            print(f"⚠️  Could not purge entities for {type_name}: {e}")

    # Delete typedefs in dependency-safe order.
    delete_order = (
        list(reversed(relationship_type_names + legacy_relationship_type_names))
        +
        list(reversed(entity_type_names))
        + list(reversed(classification_type_names))
        + list(reversed(struct_type_names))
        + list(reversed(enum_type_names))
    )

    for type_name in delete_order:
        try:
            if atlas_client.typedef.type_with_name_exists(type_name):
                atlas_client.typedef.delete_type_by_name(type_name)
                print(f"✅ Deleted type: {type_name}")
        except Exception as e:
            print(f"⚠️  Could not delete type {type_name}: {e}")

if __name__ == "__main__":
    client = create_atlas_client("admin", "admin")
    reset_scb_types(client)