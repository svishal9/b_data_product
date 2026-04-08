#!/usr/bin/env python3
"""Unified entry point for SCB Atlas operations."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from typing import Any

# Lazy imports to avoid circular dependencies and reduce import surface area
def _get_clean_up_atlas():
    from clean_up_atlas import reset_scb_types
    return reset_scb_types

def _get_create_sample_entities():
    from create_entities_with_pydantic import main as create_sample_entities_main
    return create_sample_entities_main

def _get_legacy_functions():
    from scb_dp import entity_create as legacy_entity_create, entity_delete as legacy_entity_delete
    from scb_dp_search import catalog_search as legacy_catalog_search, process_find as legacy_process_find
    return {
        'entity_create': legacy_entity_create,
        'entity_delete': legacy_entity_delete,
        'catalog_search': legacy_catalog_search,
        'process_find': legacy_process_find,
    }

from scb_atlas.atlas import (
    create_atlas_client,
    create_data_products_from_workbook,
    create_typedef,
    delete_entity,
    delete_typedef,
    parse_master_schema_workbook_to_data_products,
    validate_metadata_workbook,
)
from scb_atlas.atlas.atlas_type_def import all_type_names, all_types


def _find_existing_data_product_guids(atlas_client: Any, qualified_names: list[str]) -> dict[str, str]:
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


def _register_types(atlas_client: Any) -> None:
    print("Registering SCB type definitions...")
    try:
        create_typedef(all_types, atlas_client)
        print("Type definitions ready.")
    except Exception as exc:
        print(f"Note: Type registration returned: {exc}")


def cmd_ingest(args: argparse.Namespace) -> int:
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
    _register_types(atlas_client)
    created = create_data_products_from_workbook(args.workbook, atlas_client, strict=args.strict)

    print(f"Created {len(created)} data product entity(ies):")
    for name in created:
        print(f"- {name}")
    return 0


def cmd_recreate(args: argparse.Namespace) -> int:
    models = parse_master_schema_workbook_to_data_products(args.workbook, strict=args.strict)
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

    _register_types(atlas_client)

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


def cmd_types(args: argparse.Namespace) -> int:
    client = create_atlas_client("admin", "admin")
    if args.type_action == "create":
        create_typedef(all_types, client)
        print("SCB types created.")
        return 0

    if args.type_action == "delete":
        delete_typedef(client, args.name)
        print(f"Deleted type: {args.name}")
        return 0

    for type_name in all_type_names:
        try:
            delete_typedef(client, type_name)
            print(f"Deleted type {type_name}")
        except Exception:
            pass
    return 0


def cmd_cleanup(args: argparse.Namespace) -> int:
    client = create_atlas_client()
    reset_scb_types_fn = _get_clean_up_atlas()
    reset_scb_types_fn(client)
    return 0


def cmd_sample_entities(_args: argparse.Namespace) -> int:
    create_sample_entities_main_fn = _get_create_sample_entities()
    create_sample_entities_main_fn()
    return 0


def cmd_diagnose(_args: argparse.Namespace) -> int:
    return subprocess.run([sys.executable, "tests/manual/diagnose_atlas.py"], check=False).returncode


def cmd_tests(args: argparse.Namespace) -> int:
    suite_to_args = {
        "all": ["tests/", "-v"],
        "unit": ["tests/unit/", "-v"],
        "integration": ["tests/integration/", "-v"],
        "builders": ["tests/unit/test_entity_builders.py", "-v"],
        "types": ["tests/unit/test_atlas_types.py", "-v"],
        "coverage": ["tests/", "--cov=scb_atlas", "--cov-report=html", "-v"],
        "coverage-term": ["tests/", "--cov=scb_atlas", "--cov-report=term-missing", "-v"],
        "fast": ["tests/", "-v", "-m", "not slow"],
        "quick": ["tests/", "-x", "-q"],
        "verbose": ["tests/", "-vv", "-s"],
    }
    cmd = [sys.executable, "-m", "pytest", *suite_to_args[args.suite]]
    return subprocess.run(cmd, check=False).returncode


def cmd_dp(args: argparse.Namespace) -> int:
    legacy = _get_legacy_functions()

    if args.dp_action == "entity-create":
        legacy["entity_create"]()
        return 0
    if args.dp_action == "entity-delete":
        legacy["entity_delete"](args.guid)
        return 0
    if args.dp_action == "catalog-search":
        legacy["catalog_search"]()
        return 0

    legacy["process_find"]()
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Unified SCB Atlas CLI")
    subparsers = parser.add_subparsers(dest="command", required=True)

    ingest_parser = subparsers.add_parser("ingest", help="Ingest data products from workbook")
    ingest_parser.add_argument("workbook", type=Path, help="Path to metadata workbook")
    ingest_parser.add_argument("--dry-run", action="store_true", help="Validate/parse only")
    ingest_parser.add_argument("--strict", action="store_true", help="Enable strict workbook validation")
    ingest_parser.set_defaults(func=cmd_ingest)

    recreate_parser = subparsers.add_parser("recreate", help="Delete existing and recreate workbook data products")
    recreate_parser.add_argument("workbook", type=Path, help="Path to metadata workbook")
    recreate_parser.add_argument("--dry-run", action="store_true", help="Preview only")
    recreate_parser.add_argument("--strict", action="store_true", help="Enable strict workbook validation")
    recreate_parser.set_defaults(func=cmd_recreate)

    types_parser = subparsers.add_parser("types", help="Manage Atlas SCB type definitions")
    types_sub = types_parser.add_subparsers(dest="type_action", required=True)
    types_sub.add_parser("create", help="Create SCB types")
    delete_parser = types_sub.add_parser("delete", help="Delete one type")
    delete_parser.add_argument("name", help="Type name to delete")
    types_sub.add_parser("clean", help="Delete all SCB types")
    types_parser.set_defaults(func=cmd_types)

    cleanup_parser = subparsers.add_parser("cleanup", help="Purge SCB entities and types")
    cleanup_parser.set_defaults(func=cmd_cleanup)

    sample_parser = subparsers.add_parser("sample-entities", help="Create sample entities with Pydantic models")
    sample_parser.set_defaults(func=cmd_sample_entities)

    diagnose_parser = subparsers.add_parser("diagnose", help="Run Atlas diagnostics script")
    diagnose_parser.set_defaults(func=cmd_diagnose)

    tests_parser = subparsers.add_parser("tests", help="Run test suites")
    tests_parser.add_argument(
        "suite",
        choices=["all", "unit", "integration", "builders", "types", "coverage", "coverage-term", "fast", "quick", "verbose"],
        help="Test suite to run",
    )
    tests_parser.set_defaults(func=cmd_tests)

    dp_parser = subparsers.add_parser("dp", help="Legacy data-product helper actions")
    dp_sub = dp_parser.add_subparsers(dest="dp_action", required=True)
    dp_sub.add_parser("entity-create", help="Create legacy example entities")
    dp_delete = dp_sub.add_parser("entity-delete", help="Delete legacy entity by guid")
    dp_delete.add_argument("guid", help="Atlas entity guid")
    dp_sub.add_parser("catalog-search", help="Run legacy catalog search")
    dp_sub.add_parser("process-find", help="Run legacy process search and cleanup")
    dp_parser.set_defaults(func=cmd_dp)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())


