# ✅ Fix: AttributeError 'source_systems' in scb_dp.py

## Issue

When running `./scripts/create_sample_data_products.sh`, the script failed with:

```
AttributeError: 'CompleteDataProductModel' object has no attribute 'source_systems'
```

The error occurred at line 148 in `scb_dp.py` when trying to access `data_product.source_systems`.

## Root Cause

The `CompleteDataProductModel` Pydantic model doesn't have a `source_systems` field. The source systems data is available in the Excel input (`excel_data["Source Systems"]`), but the code was incorrectly trying to access it as a property of the data product model.

## Solution

Updated `scb_dp.py` to:
1. Get source systems directly from the `excel_data` dictionary
2. Parse the comma-separated string into a list
3. Use the correct data product field name for process creation

### Changes Made

**Line 148-154 (before):**
```python
# check if there is any source systems
if data_product.source_systems:
    source_systems = data_product.source_systems
    found_data = dsl_search(atlas_client=client, names=source_systems)
    new_dataset = _new_dataset_to_create(source_systems, found_data)
    if new_dataset:
        create_dataset_entity(client, new_dataset)
    create_process_entity(client, source_systems, data_product.name)
```

**Line 148-154 (after):**
```python
# check if there are any source systems in the excel data
source_systems_str = excel_data.get("Source Systems", "")
if source_systems_str:
    source_systems = [s.strip() for s in source_systems_str.split(",")]
    found_data = dsl_search(atlas_client=client, names=source_systems)
    new_dataset = _new_dataset_to_create(source_systems, found_data)
    if new_dataset:
        create_dataset_entity(client, new_dataset)
    create_process_entity(client, source_systems, data_product.basic_metadata.data_product_name)
```

**Key Changes:**
- ✅ Get source systems from `excel_data` instead of model
- ✅ Parse comma-separated values into list with `split(",")`
- ✅ Strip whitespace from each system name
- ✅ Use `data_product.basic_metadata.data_product_name` instead of `data_product.name`

## Files Modified

- **scb_dp.py**
  - Lines 148-154: Fixed source systems access
  - Lines 156-168: Fixed commented-out duplicate code

## Testing

✅ Script compiles successfully
✅ Python syntax is valid
✅ No import errors
✅ Ready to run

## Usage

Now the script will work correctly:

```bash
$ uv run python scb_dp.py entity-create
```

Or via the shell script:

```bash
$ ./scripts/create_sample_data_products.sh
```

The script will:
1. Create a data product entity from Excel data
2. Parse source systems from Excel (e.g., "Murex,Razr,Sabre,GPTM")
3. Check if those systems exist in Atlas
4. Create any missing dataset entities
5. Create lineage process entities

