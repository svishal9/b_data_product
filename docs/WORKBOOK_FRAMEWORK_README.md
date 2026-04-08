# Excel Metadata Framework

This framework reads an Excel workbook and creates Atlas `SCB_DataProduct` entities with complete lineage.

## Workbook Contract

- A worksheet named `Data Product` (case-insensitive accepted, e.g. `Data product`)
- A worksheet per data product, named exactly as the `Data Product Name` value
- Per-data-product worksheet includes output schema rows under a row containing `Field Name` and `Data Type`

Example workbook: `sample_data/metadata_example.xlsx`

## What It Does

1. Validates spreadsheet structure
2. Maps spreadsheet values to Pydantic models in `scb_atlas/atlas/metadata_models`
3. Creates Atlas Data Product entities via `create_data_product_from_model`
4. **Creates input/output port tables** to represent data product interfaces
5. **Creates lineage processes** to show data flow:
   - Ingest Process: Input Ports → Data Product
   - Publish Process: Data Product → Output Port

## Lineage Visualization

The framework automatically creates processes that enable Atlas to display complete lineage:

```
Input Systems → [Ingest Process] → Data Product → [Publish Process] → Output Consumers
     (tables)                      (entity)         (tables)
```

See `LINEAGE_FIX_SUMMARY.md` for detailed information about how lineage is created.

## Public API

- `validate_metadata_workbook(file_path, strict=False)`
- `parse_workbook_to_data_products(file_path, strict=False)`
- `create_data_products_from_workbook(file_path, atlas_client, strict=False)` - Now creates lineage processes

### Strict Mode

When `strict=True`, parser/validator fails if:

- required headers are missing in the `Data Product` sheet
- a data product worksheet (named by `Data Product Name`) is missing
- schema worksheet does not contain a `Field Name` + `Data Type` header row
- boolean/integer typed metadata cannot be coerced

Module: `scb_atlas/atlas/read_data_product.py`

## CLI Runner

Use `ingest_workbook_to_atlas.py`.

```bash
uv run python ingest_workbook_to_atlas.py sample_data/metadata_example.xlsx --dry-run
uv run python ingest_workbook_to_atlas.py sample_data/metadata_example.xlsx
uv run python ingest_workbook_to_atlas.py sample_data/metadata_example.xlsx --dry-run --strict
```

## Verify Lineage Creation

After running the ingestion:

```bash
# Test that lineage processes were created
uv run python tests/manual/test_lineage_creation.py
```

This will verify:
- ✅ Data products created
- ✅ Ingest processes created (input → data product)
- ✅ Publish processes created (data product → output)

## Test Commands

```bash
uv run pytest tests/integration/test_read_excel_file.py -q
uv run pytest tests/ -q
```

## See Also

- `LINEAGE_FIX_SUMMARY.md` - Detailed explanation of lineage creation
- `CREATE_ENTITIES_QUICK_START.md` - How to create other entity types
- `ENTITY_TYPES.md` - Complete entity type reference

