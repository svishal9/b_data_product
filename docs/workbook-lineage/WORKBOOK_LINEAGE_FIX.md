# ✅ WORKBOOK LINEAGE FIX - COMPLETE

## Problem Solved

When running `uv run python ingest_workbook_to_atlas.py sample_data/metadata_example.xlsx`, the data products were created but **lineage was missing** - you could not see the flow from input ports → data product → output port in Atlas.

## Solution Implemented

Added automatic creation of **lineage processes** that connect:
1. **Input Ports → Data Product** (Ingest Process)
2. **Data Product → Output Port** (Publish Process)

This enables the complete lineage visualization in Atlas UI.

---

## What Changed

### File: `scb_atlas/atlas/read_data_product.py`

✅ **Added imports:**
- `ProcessModel` from metadata_models
- `create_process_from_model` from service.entity_service

✅ **Added new function:** `_create_lineage_processes()`
- Creates two processes representing the data flow
- Called automatically after creating each data product

✅ **Updated function:** `create_data_products_from_workbook()`
- Now calls `_create_lineage_processes()` for each data product

### Files Created

✅ `test_lineage_creation.py` - Verification script
✅ `docs/LINEAGE_FIX_SUMMARY.md` - Detailed documentation

### Files Updated

✅ `docs/WORKBOOK_FRAMEWORK_README.md` - Added lineage section

---

## How It Works Now

When you run the workbook ingestion:

```bash
uv run python ingest_workbook_to_atlas.py sample_data/metadata_example.xlsx
```

For each data product in the workbook, the system creates:

```
1. Input Port Tables (one per source system)
   ↓
2. [Ingest Process] ← NEW: Creates lineage edge
   ↓
3. Data Product Entity
   ↓
4. [Publish Process] ← NEW: Creates lineage edge
   ↓
5. Output Port Table
```

---

## Verify It Works

### Method 1: Test Script (Recommended)

```bash
uv run python tests/manual/test_lineage_creation.py
```

This will:
- Create data products from the workbook
- Search for ingest processes
- Search for publish processes
- Confirm everything is connected

Output will show:
```
✅ Created 1 data product(s):
   - Your Data Product Name

📊 Found 1 ingest process(es):
   - Your Data Product Name_ingest_process

📊 Found 1 publish process(es):
   - Your Data Product Name_publish_process

✅ Lineage processes created successfully!
```

### Method 2: Atlas UI

1. Open: `http://localhost:23000`
2. Login: `admin/admin`
3. Search → Advanced Search
4. Type: `SCB_DataProduct`
5. Click on a data product
6. Click **Lineage** tab
7. You should see:
   ```
   Input Port → Ingest Process → Data Product → Publish Process → Output Port
   ```

### Method 3: Check Database Connection

Ensure Atlas is still running and responsive:

```bash
curl http://localhost:23000/
# Expected: HTTP/1.1 401 Unauthorized (that's OK!)
```

---

## Code Changes Summary

### New Function Added

```python
def _create_lineage_processes(
    atlas_client: Any,
    model: CompleteDataProductModel,
    input_port_qualified_names: list[str] | None,
    output_port_qualified_name: str | None,
) -> None:
    """Create processes to represent data lineage."""
    # Creates two processes:
    # 1. Ingest: Input Ports → Data Product
    # 2. Publish: Data Product → Output Port
```

### Updated Function

```python
def create_data_products_from_workbook(...):
    # ... existing code ...
    
    # NEW: Create lineage processes
    _create_lineage_processes(
        atlas_client,
        model,
        input_port_qualified_names,
        output_port_qualified_name,
    )
```

---

## Usage Examples

### Run with dry-run (preview only)

```bash
uv run python ingest_workbook_to_atlas.py sample_data/metadata_example.xlsx --dry-run
```

### Run with strict validation

```bash
uv run python ingest_workbook_to_atlas.py sample_data/metadata_example.xlsx --strict
```

### Verify lineage created

```bash
uv run python tests/manual/test_lineage_creation.py
```

---

## Expected Output

After running the fix, you should see in Atlas UI:

**Before Fix:**
```
Lineage tab shows:
- Input port table (standalone)
- Data product (standalone)
- Output port table (standalone)
- No visible connections
```

**After Fix:**
```
Lineage tab shows:
INPUT_PORT --[ingest process]--> DATA_PRODUCT --[publish process]--> OUTPUT_PORT
(complete connected chain with processes as intermediate nodes)
```

---

## Architecture Notes

The fix aligns with Apache Atlas best practices:

1. **Processes represent transformations** - Data lineage uses processes as transformation steps
2. **Qualified names** - All entities use consistent qualified naming for linking
3. **Type safety** - Uses proper SCB_Table and SCB_DataProduct type names
4. **Consistency** - Follows same pattern as `entity_builders.py::create_data_product_with_lineage()`

---

## Troubleshooting

**Q: Still don't see lineage?**
- Wait 5-10 seconds for Atlas to index
- Refresh browser
- Check that processes were created: `uv run python tests/manual/test_lineage_creation.py`
- Check Atlas logs for errors

**Q: How to verify from command line?**
```bash
# This tests the entire flow
uv run python tests/manual/test_lineage_creation.py
```

**Q: Can I use this with my own workbook?**
Yes! As long as your workbook follows the format:
- "Data Product" sheet with metadata
- Per-data-product worksheet with schema

See `WORKBOOK_FRAMEWORK_README.md` for workbook format requirements.

---

## Next Steps

1. ✅ Run: `uv run python ingest_workbook_to_atlas.py sample_data/metadata_example.xlsx`
2. ✅ Verify: `uv run python tests/manual/test_lineage_creation.py`
3. ✅ View in Atlas UI: Open Lineage tab on any data product
4. ✅ Test with your workbook: Prepare your own metadata workbook
5. ✅ Review: Check `LINEAGE_FIX_SUMMARY.md` for detailed technical info

---

## Files Changed

| File | Change | Status |
|------|--------|--------|
| `scb_atlas/atlas/read_data_product.py` | Added lineage process creation | ✅ Modified |
| `test_lineage_creation.py` | New test/verification script | ✅ Created |
| `docs/LINEAGE_FIX_SUMMARY.md` | Detailed documentation | ✅ Created |
| `docs/WORKBOOK_FRAMEWORK_README.md` | Updated with lineage info | ✅ Updated |

---

## Support

For more details:
- `docs/LINEAGE_FIX_SUMMARY.md` - Complete technical documentation
- `docs/WORKBOOK_FRAMEWORK_README.md` - Workbook framework reference
- `test_lineage_creation.py` - Example verification script

**The lineage is now complete!** 🎉


