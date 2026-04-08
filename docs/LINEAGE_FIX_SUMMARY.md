# ✅ LINEAGE FIX FOR WORKBOOK INGESTION

<!--suppress ALL -->

## What Was Fixed

When running `uv run python ingest_workbook_to_atlas.py sample_data/metadata_example.xlsx`, the data products were being created with input/output port tables, but **the lineage processes were missing**. This meant the graph in Atlas showed:

❌ **Before (Missing Lineage):**
```
Input Port [table]  →  Data Product  →  Output Port [table]
(no visible connection)
```

✅ **After (Complete Lineage):**
```
Input Port [table] → [Ingest Process] → Data Product → [Publish Process] → Output Port [table]
```

---

## Changes Made

### File: `scb_atlas/atlas/read_data_product.py`

#### 1. Added Imports

- Added `create_process_from_model` to service imports in `scb_atlas/atlas/read_data_product.py`.
- Added `ProcessModel` to metadata model imports in `scb_atlas/atlas/read_data_product.py`.

#### 2. Added New Function: `_create_lineage_processes()`

This function creates two processes representing the data lineage:

**Process 1: Ingest Process**
- Input: All input port tables
- Output: The data product
- Represents: "How data flows from source systems into the data product"

**Process 2: Publish Process**
- Input: The data product
- Output: The output port table
- Represents: "How data flows from the data product to consumers"

Implementation summary:
- Added `_create_lineage_processes(...)` that computes the data-product qualified name and name.
- If input ports exist, it creates an `<data_product_name>_ingest_process` with:
  - inputs = all input port tables
  - outputs = the data product
- If an output port exists, it creates a `<data_product_name>_publish_process` with:
  - inputs = the data product
  - outputs = the output port table

#### 3. Updated Function: `create_data_products_from_workbook()`

Added call to create the lineage processes after creating the data product:

Flow update in `create_data_products_from_workbook(...)`:
- Parse workbook models.
- Ensure/create port database and port assets.
- Create the data product entity.
- **New step:** call `_create_lineage_processes(...)` immediately after product creation.
- Return created product names.

---

## How to Use

### Run the Fixed Script

```bash
# Clean run (optionally delete old entities first)
uv run python ingest_workbook_to_atlas.py sample_data/metadata_example.xlsx

# Or with dry-run to see what will be created
uv run python ingest_workbook_to_atlas.py sample_data/metadata_example.xlsx --dry-run

# Test the lineage creation
uv run python tests/manual/test_lineage_creation.py
```

### What Gets Created Now

For each data product in the workbook:

1. ✅ **Input Port Tables** - One table per input source system
2. ✅ **Data Product Entity** - The main data product
3. ✅ **Output Port Table** - One table representing the output schema
4. ✅ **Ingest Process** - Links input ports → data product
5. ✅ **Publish Process** - Links data product → output port

### View Lineage in Atlas UI

1. Open Atlas: `http://localhost:23000`
2. Login: `admin/admin`
3. Search → Advanced Search
4. Select type: `SCB_DataProduct`
5. Click on a data product
6. **Lineage** tab shows the complete flow:
   ```
   Input Port → Ingest Process → Data Product → Publish Process → Output Port
   ```

---

## Testing

A test script has been created to verify lineage creation:

```bash
uv run python tests/manual/test_lineage_creation.py
```

This will:
- Create data products from the sample workbook
- Search for ingest processes
- Search for publish processes
- Confirm the lineage is properly connected

---

## Related Workflows

This fix aligns with the pattern used in:
- `scb_atlas/atlas/entity_builders.py` - `create_data_product_with_lineage()`
- `tests/unit/test_entity_builders.py` - Process lineage tests

---

## Lineage Visualization

**Before Fix:**
```
source_systems table
           ↓
      (no connection)
           ↓
    Data Product
           ↓
      (no connection)
           ↓
   output_port table
```

**After Fix:**
```
source_systems table
           ↓
    [Ingest Process]  ← Creates visible lineage edge
           ↓
    Data Product
           ↓
   [Publish Process]  ← Creates visible lineage edge
           ↓
   output_port table
```

---

## Architecture Notes

The fix maintains consistency with Atlas best practices:

1. **Processes represent transformations** - In Apache Atlas, data lineage is typically shown through processes that connect input/output entities
2. **Qualified names** - All entities use consistent qualified naming for proper linking
3. **Relationship attributes** - Data products retain direct relationships to ports (for UI) while processes add the lineage graph
4. **Type safety** - All references use proper SCB_Table and SCB_DataProduct type names

---

## Files Modified

- ✅ `/scb_atlas/atlas/read_data_product.py` - Added lineage process creation
  - Added imports: `create_process_from_model`, `ProcessModel`
  - Added function: `_create_lineage_processes()`
  - Updated function: `create_data_products_from_workbook()`

## Files Created

- ✅ `/tests/manual/test_lineage_creation.py` - Test script to verify lineage creation
- ✅ `/docs/LINEAGE_FIX_SUMMARY.md` - This documentation

---

## Next Steps

1. ✅ Run the workbook ingestion script
2. ✅ Verify lineage appears in Atlas UI
3. ✅ Check Lineage tab shows complete flow
4. ✅ Test with your own workbook
5. ✅ Clean up if needed: `uv run python clean_up_atlas.py`

---

## Troubleshooting

**Q: Lineage still not showing?**
- Wait 5-10 seconds for Atlas to index the processes
- Refresh the browser
- Ensure you're viewing the correct data product
- Check Atlas logs for errors

**Q: Only one process showing?**
- Ingest process only shows if data product has input ports (source systems)
- Publish process only shows if data product has output port schema
- Both should show for complete lineage

**Q: How to verify from command line?**
```bash
uv run python tests/manual/test_lineage_creation.py
```

This will search for and display all created processes.

---


