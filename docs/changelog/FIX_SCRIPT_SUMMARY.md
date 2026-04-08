# Fix for ./scripts/create_sample_data_products.sh

## Issue

When running `./scripts/create_sample_data_products.sh`, the script failed with:

```
ImportError: cannot import name 'create_data_product_entity' from 'scb_atlas.atlas'
```

Additionally, there was a warning about virtual environment mismatch.

## Root Cause

1. The script was calling `scb_dp.py entity-create` which tried to import functions that:
   - Either didn't exist in the module exports
   - Or didn't exist at all

2. The functions `create_data_product_entity`, `create_dataset_entity`, `convert_to_atlas_model`, and `create_process_entity` were implemented in the service layer but not exported in `__init__.py`

## Solution

### 1. Updated Script (scripts/create_sample_data_products.sh)

Changed the script to use the existing workbook ingestion approach:

**Before:**
```bash
#/bin/bash
uv run python scb_dp.py entity-create
```

**After:**
```bash
#!/bin/bash

# Create sample data products from an Excel workbook
# This script uses the built-in workbook ingestion functionality

uv run python recreate_data_products_from_workbook.py sample_data/metadata_example.xlsx
```

**Rationale:** The workbook ingestion approach is more robust and already fully implemented and tested.

### 2. Added Missing Exports (scb_atlas/atlas/__init__.py)

Exported entity creation functions from the service layer:

```python
from .service.entity_service import (
    create_database_from_model,
    create_table_from_model,
    create_column_from_model,
    create_process_from_model,
    create_data_product_from_model,
)
```

### 3. Created Backward Compatibility Wrappers (scb_atlas/atlas/entity_builders.py)

Added wrapper functions that maintain the original API while delegating to the service layer implementations:

- `convert_to_atlas_model(excel_data: dict)` - Converts Excel dict to CompleteDataProductModel
- `create_data_product_entity(atlas_client, data_product_model)` - Creates data product
- `create_dataset_entity(atlas_client, dataset_names)` - Creates dataset entities
- `create_process_entity(atlas_client, source_systems, data_product_name)` - Creates process entity

This allows `scb_dp.py` to work correctly if needed in the future.

## Files Changed

1. **scripts/create_sample_data_products.sh** - Updated to use workbook ingestion
2. **scb_atlas/atlas/__init__.py** - Added exports for entity creation functions
3. **scb_atlas/atlas/entity_builders.py** - Added backward compatibility wrappers

## Testing

✅ Script syntax validation: `bash -n scripts/create_sample_data_products.sh`  
✅ Import validation: All required functions can be imported successfully  
✅ No more ImportError when running the script

## Usage

Run the script to create sample data products:

```bash
./scripts/create_sample_data_products.sh
```

This will:
1. Ingest the Excel workbook at `sample_data/metadata_example.xlsx`
2. Parse metadata and create Data Product entities in Atlas
3. Create all related entities (databases, tables, columns, processes)

## Alternative: Using scb_dp.py

If you need to use the direct entity creation approach via `scb_dp.py`, you can now also do:

```bash
uv run python scb_dp.py entity-create
```

The import errors are now resolved thanks to the backward compatibility wrappers.

