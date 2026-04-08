#!/usr/bin/env python3
"""Load data-product metadata from an Excel workbook and create Atlas entities."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from scb_atlas.atlas import (
    create_atlas_client,
    create_typedef,
    create_data_products_from_workbook,
    #parse_workbook_to_data_products,
    parse_master_schema_workbook_to_data_products,
    validate_metadata_workbook,
)
from scb_atlas.atlas.atlas_type_def import all_types

def print_header(title):
    """Print formatted header."""
    print("\n" + "="*80)
    print(f"▶ {title}")
    print("="*80 + "\n")

def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Ingest data-product workbook into Atlas.")
    parser.add_argument(
        "workbook",
        type=Path,
        help="Path to metadata workbook (must contain Data Product sheet and per-product sheets).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only validate and parse workbook without creating Atlas entities.",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail on missing per-product worksheet, missing required headers, or invalid typed values.",
    )
    return parser.parse_args()



def main() -> int:
   
    args = parse_args()

    if not validate_metadata_workbook(args.workbook, strict=args.strict):
        print("Workbook validation failed.")
        return 1

    models = parse_master_schema_workbook_to_data_products(args.workbook, strict=args.strict)
    print(f"Validated workbook. Parsed {len(models)} data product(s).")

    if args.dry_run:
        for model in models:
            schema_count = len(model.output_port_schema or [])
            print(f"- {model.basic_metadata.data_product_name} (schema fields: {schema_count})")
        return 0

    atlas_client = create_atlas_client()

    print("Registering SCB type definitions...")
    try:
        create_typedef(all_types, atlas_client)
        print("Type definitions ready.")
    except Exception as e:
        print(f"Note: Type registration returned: {e}")

    created = create_data_products_from_workbook(args.workbook, atlas_client, strict=args.strict)
    print(f"Created {len(created)} data product entity(ies):")
    for name in created:
        print(f"- {name}")

    return 0

if __name__ == "__main__":
    # Backward-compatible wrapper: keep old entry point working via unified CLI.
    print(
        "[DEPRECATED] `ingest_workbook_to_atlas.py` is deprecated. "
        "Use `scb_dp_cli.py ingest ...` (or `scb ingest ...`)."
    )
    # Ensure project root is in sys.path for imports
    project_root = Path(__file__).parent
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))

    from scb_dp_cli import main as scb_main

    raise SystemExit(scb_main(["ingest", *sys.argv[1:]]))

