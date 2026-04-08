#!/usr/bin/env python3
"""Delete and recreate SCB_DataProduct entities from a metadata workbook."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path1

from scb_atlas.atlas import (
    create_atlas_client,
    create_data_products_from_workbook,
    delete_entity,
    parse_workbook_to_data_products,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Recreate SCB_DataProduct entities from a workbook (delete existing by qualifiedName, then create)."
    )
    parser.add_argument(
        "workbook",
        type=Path,
        help="Path to metadata workbook (must contain Data Product worksheet).",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on missing required headers, missing per-product worksheet, or invalid typed values.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview deletions and creations without mutating Atlas.",
    )
    return parser.parse_args()


def _find_existing_data_product_guids(atlas_client, qualified_names: list[str]) -> dict[str, str]:
    """Return map of data-product qualifiedName -> entity guid for existing entities."""
    existing: dict[str, str] = {}
    for qualified_name in qualified_names:
        try:
            response = atlas_client.entity.get_entities_by_attribute(
                "SCB_DataProduct",
                [{"qualifiedName": qualified_name}],
            )
        except Exception:
            continue

        entities = response.get("entities", []) if isinstance(response, dict) else []
        if entities:
            guid = entities[0].get("guid")
            if guid:
                existing[qualified_name] = guid
    return existing


def main() -> int:
    args = parse_args()

    models = parse_workbook_to_data_products(args.workbook, strict=args.strict)
    if not models:
        print("No data products found in workbook.")
        return 1

    qualified_names = [model.qualified_name for model in models]
    names = [model.basic_metadata.data_product_name for model in models]

    atlas_client = create_atlas_client()
    existing = _find_existing_data_product_guids(atlas_client, qualified_names)

    print(f"Workbook parsed. Data products: {len(models)}")
    for name, qualified_name in zip(names, qualified_names, strict=True):
        status = "exists" if qualified_name in existing else "new"
        print(f"- {name} [{qualified_name}] ({status})")

    if args.dry_run:
        print("Dry-run complete. No Atlas changes made.")
        return 0

    if existing:
        delete_guids = list(existing.values())
        delete_entity(atlas_client, delete_guids)
        print(f"Deleted {len(delete_guids)} existing SCB_DataProduct entity(ies).")
    else:
        print("No existing SCB_DataProduct entities to delete.")

    created = create_data_products_from_workbook(args.workbook, atlas_client, strict=args.strict)
    print(f"Created {len(created)} SCB_DataProduct entity(ies):")
    for name in created:
        print(f"- {name}")

    return 0


if __name__ == "__main__":
    # Backward-compatible wrapper: keep old entry point working via unified CLI.
    print(
        "[DEPRECATED] `recreate_data_products_from_workbook.py` is deprecated. "
        "Use `scb_dp_cli.py recreate ...` (or `scb recreate ...`)."
    )
    from scb_dp_cli import main as scb_main

    raise SystemExit(scb_main(["recreate", *sys.argv[1:]]))

