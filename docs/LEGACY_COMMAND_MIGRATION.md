# Legacy Command Migration

This project now uses a single unified CLI entry point:

- `uv run python scb_dp_cli.py ...`
- or installed command: `scb ...`

Use this guide to migrate old script commands to their new `scb` equivalents.

## Quick Rule

- Old: `uv run python <old_script>.py ...`
- New: `uv run python scb_dp_cli.py <subcommand> ...`
- Preferred (after install): `scb <subcommand> ...`

## Command Mapping

| Legacy command | New unified command | Installed command |
|---|---|---|
| `uv run python ingest_workbook_to_atlas.py sample_data/metadata_example.xlsx` | `uv run python scb_dp_cli.py ingest sample_data/metadata_example.xlsx` | `scb ingest sample_data/metadata_example.xlsx` |
| `uv run python ingest_workbook_to_atlas.py sample_data/metadata_example.xlsx --dry-run --strict` | `uv run python scb_dp_cli.py ingest sample_data/metadata_example.xlsx --dry-run --strict` | `scb ingest sample_data/metadata_example.xlsx --dry-run --strict` |
| `uv run python recreate_data_products_from_workbook.py sample_data/metadata_example.xlsx` | `uv run python scb_dp_cli.py recreate sample_data/metadata_example.xlsx` | `scb recreate sample_data/metadata_example.xlsx` |
| `uv run python recreate_data_products_from_workbook.py sample_data/metadata_example.xlsx --dry-run --strict` | `uv run python scb_dp_cli.py recreate sample_data/metadata_example.xlsx --dry-run --strict` | `scb recreate sample_data/metadata_example.xlsx --dry-run --strict` |
| `uv run python clean_up_atlas.py` | `uv run python scb_dp_cli.py cleanup` | `scb cleanup` |
| `uv run python create_entities_with_pydantic.py` | `uv run python scb_dp_cli.py sample-entities` | `scb sample-entities` |
| `uv run python run_tests.py all` | `uv run python scb_dp_cli.py tests all` | `scb tests all` |
| `uv run python run_tests.py unit` | `uv run python scb_dp_cli.py tests unit` | `scb tests unit` |
| `uv run python run_tests.py integration` | `uv run python scb_dp_cli.py tests integration` | `scb tests integration` |
| `uv run python run_tests.py builders` | `uv run python scb_dp_cli.py tests builders` | `scb tests builders` |
| `uv run python run_tests.py types` | `uv run python scb_dp_cli.py tests types` | `scb tests types` |
| `uv run python run_tests.py coverage` | `uv run python scb_dp_cli.py tests coverage` | `scb tests coverage` |
| `uv run python run_tests.py coverage-term` | `uv run python scb_dp_cli.py tests coverage-term` | `scb tests coverage-term` |
| `uv run python run_tests.py fast` | `uv run python scb_dp_cli.py tests fast` | `scb tests fast` |
| `uv run python run_tests.py quick` | `uv run python scb_dp_cli.py tests quick` | `scb tests quick` |
| `uv run python run_tests.py verbose` | `uv run python scb_dp_cli.py tests verbose` | `scb tests verbose` |
| `uv run python scb_types.py type-create` or `uv run python scb_types.py type_create` | `uv run python scb_dp_cli.py types create` | `scb types create` |
| `uv run python scb_types.py type-delete SCB_Database` or `uv run python scb_types.py type_delete SCB_Database` | `uv run python scb_dp_cli.py types delete SCB_Database` | `scb types delete SCB_Database` |
| `uv run python scb_types.py type-clean` or `uv run python scb_types.py type_clean` | `uv run python scb_dp_cli.py types clean` | `scb types clean` |
| `uv run python scb_dp.py entity-create` or `uv run python scb_dp.py entity_create` | `uv run python scb_dp_cli.py dp entity-create` | `scb dp entity-create` |
| `uv run python scb_dp.py entity-delete <GUID>` or `uv run python scb_dp.py entity_delete <GUID>` | `uv run python scb_dp_cli.py dp entity-delete <GUID>` | `scb dp entity-delete <GUID>` |
| `uv run python scb_dp_search.py catalog-search` or `uv run python scb_dp_search.py catalog_search` | `uv run python scb_dp_cli.py dp catalog-search` | `scb dp catalog-search` |
| `uv run python scb_dp_search.py process-find` or `uv run python scb_dp_search.py process_find` | `uv run python scb_dp_cli.py dp process-find` | `scb dp process-find` |

## Notes

- Legacy scripts are still supported as wrappers, but they now print a deprecation notice and delegate to `scb_dp_cli.py`.
- Use `scb --help` (or `uv run python scb_dp_cli.py --help`) to browse current commands.
- New command groups are:
  - `ingest`
  - `recreate`
  - `types`
  - `cleanup`
  - `sample-entities`
  - `diagnose`
  - `tests`
  - `dp`

