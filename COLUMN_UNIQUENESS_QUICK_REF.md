# Quick Reference: Column Uniqueness Bug Fix

## TL;DR
**Fixed:** Columns now allow the same name in different data products
**Changed:** 1 line in `scb_entity.py` (line 45)
**Impact:** `"isUnique": True` → `"isUnique": False` for `field_name` attribute

## The Bug
```
Error: violates a uniqueness constraint
When: Creating column "id" in DataProduct B (when "id" already exists in DataProduct A)
```

## The Fix
```python
# File: scb_atlas/atlas/atlas_type_def/scb_entity.py, Line 45

# BEFORE (broken):
{ "name": "field_name", ..., "isUnique": True, ... }

# AFTER (fixed):
{ "name": "field_name", ..., "isUnique": False, ... }
```

## Why It Works
- **Before:** `field_name` was globally unique → prevented name reuse
- **After:** `field_name` is NOT globally unique → allows name reuse
- **Safety:** Global uniqueness is still enforced via `qualifiedName` (inherited from DataSet)
  - Example: `scb:::dp:::database.table.field_name` is still globally unique

## Test It
```bash
# Verify the fix
grep '"field_name"' scb_atlas/atlas/atlas_type_def/scb_entity.py | grep "isUnique"
# Should show: "isUnique": False ✅

# Run regression test
pytest tests/unit/test_atlas_types.py::TestColumnEntityType::test_column_field_name_not_globally_unique -v
# Should PASS ✅

# Run all tests
pytest tests/unit/test_atlas_types.py -v
# Should all PASS (42/42) ✅
```

## Files Changed
| File | Change | Line |
|------|--------|------|
| `scb_atlas/atlas/atlas_type_def/scb_entity.py` | `isUnique: True` → `False` | 45 |
| `tests/unit/test_atlas_types.py` | Added regression test | +11 lines |
| `BUG_FIX_COLUMN_UNIQUENESS.md` | Documentation | New |
| `COLUMN_UNIQUENESS_FIX_SUMMARY.md` | Documentation | New |
| `COLUMN_UNIQUENESS_FIX_TECHNICAL.md` | Documentation | New |

## Deployment
```bash
# 1. Delete old type (if Atlas is running)
# In Atlas UI or via API: Delete SCB_StandardColumn

# 2. Deploy updated code
git pull
cd /Users/vishal/IdeaProjects/scb-data-product

# 3. Re-ingest data products
# Same column names will now work across data products ✅
```

## Result
✅ DataProduct A Table T1 can have column "id"
✅ DataProduct B Table T2 can have column "id"  
✅ No "violates uniqueness" errors
✅ All tests passing (42/42)

