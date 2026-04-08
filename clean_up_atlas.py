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

# Keep bulk delete payloads small enough for Atlas/ingress URI limits.
_DELETE_GUID_BATCH_SIZE = 100


def _iter_chunks(values: list[str], size: int):
    """Yield fixed-size chunks from a list."""
    for idx in range(0, len(values), size):
        yield values[idx:idx + size]


def print_header(title):
    """Print formatted header."""
    print("\n" + "="*80)
    print(f"▶ {title}")
    print("="*80 + "\n")

def _extract_type_names(type_key: str) -> list[str]:
    """Return type names from Atlas typedef payload for a given definition key."""
    return [d.get("name") for d in all_types.get(type_key, []) if d.get("name")]


def _purge_entities_by_type(atlas_client, type_name: str) -> int:
    """Best-effort purge of all entities for a type before deleting that type."""
    purged_total = 0
    while True:
        query = f"from {type_name} limit 1000"
        result = atlas_client.discovery.dsl_search(query)
        entities = getattr(result, "entities", None) or []
        guids = [e.get("guid") for e in entities if e.get("guid")]
        if not guids:
            return purged_total

        # Deduplicate while preserving order.
        unique_guids = list(dict.fromkeys(guids))

        # Atlas bulk delete can fail with 414 when too many GUIDs are sent at once.
        for guid_batch in _iter_chunks(unique_guids, _DELETE_GUID_BATCH_SIZE):
            delete_entity(atlas_client, guid_batch)
            purged_total += len(guid_batch)


def _build_cleanup_plan() -> dict[str, list[str]]:
    """Build ordered type lists used during cleanup."""
    entity_type_names = _extract_type_names("entityDefs")
    relationship_type_names = _extract_type_names("relationshipDefs")
    legacy_entity_type_names = [
        # Explicitly clean up deprecated/legacy column entities used by older deployments.
        "SCB_StandardColumn",
        "SCB_Column",
    ]
    legacy_relationship_type_names = [
        "SCB_Table_Columns",
        "SCB_DataProduct_InputTables",
        "SCB_DataProduct_OutputTable",
        "SCB_DataProduct_Tables",
    ]
    classification_type_names = _extract_type_names("classificationDefs")
    struct_type_names = _extract_type_names("structDefs")
    enum_type_names = _extract_type_names("enumDefs")

    purge_entity_types = list(dict.fromkeys(entity_type_names + legacy_entity_type_names))
    delete_order = (
        list(reversed(relationship_type_names + legacy_relationship_type_names))
        + list(reversed(entity_type_names + legacy_entity_type_names))
        + list(reversed(classification_type_names))
        + list(reversed(struct_type_names))
        + list(reversed(enum_type_names))
    )

    return {
        "purge_entity_types": purge_entity_types,
        "delete_order": delete_order,
    }


def reset_scb_types(atlas_client, dry_run: bool = False) -> None:
    """Delete SCB entities and typedefs so setup can recreate them cleanly."""
    print_header("Reset: Purging Existing SCB Entities and Types")

    plan = _build_cleanup_plan()
    purge_entity_types = plan["purge_entity_types"]
    delete_order = plan["delete_order"]

    if dry_run:
        print("[DRY-RUN] Entity types to purge:")
        for type_name in reversed(purge_entity_types):
            print(f"- {type_name}")

        print("[DRY-RUN] Type definitions to delete (order):")
        for type_name in delete_order:
            print(f"- {type_name}")
        return

    # Purge entity instances first in reverse dependency order.
    for type_name in reversed(purge_entity_types):
        try:
            purged_count = _purge_entities_by_type(atlas_client, type_name)
            print(f"✅ Purged entities for type: {type_name} (count={purged_count})")
        except Exception as e:
            print(f"⚠️  Could not purge entities for {type_name}: {e}")

    # Delete typedefs in dependency-safe order.

    for type_name in delete_order:
        try:
            if atlas_client.typedef.type_with_name_exists(type_name):
                atlas_client.typedef.delete_type_by_name(type_name)
                print(f"✅ Deleted type: {type_name}")
        except Exception as e:
            # Atlas may still have residual references (409). Re-purge entity instances and retry.
            if "has references" in str(e):
                try:
                    purged_count = _purge_entities_by_type(atlas_client, type_name)
                    if purged_count > 0:
                        print(f"↻ Retried purge for {type_name} before delete (count={purged_count})")
                    atlas_client.typedef.delete_type_by_name(type_name)
                    print(f"✅ Deleted type after retry: {type_name}")
                    continue
                except Exception as retry_error:
                    print(f"⚠️  Could not delete type {type_name} after retry: {retry_error}")
                    continue
            print(f"⚠️  Could not delete type {type_name}: {e}")

if __name__ == "__main__":
    client = create_atlas_client("admin", "admin")
    reset_scb_types(client)