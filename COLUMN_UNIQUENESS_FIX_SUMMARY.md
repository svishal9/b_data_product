# Column Uniqueness Bug Fix - Summary

## Problem Statement
When trying to create multiple data products with columns that share the same name (e.g., "id", "created_date"), Atlas rejected the operation with:
```
violates a uniqueness constraint
```

This prevented legitimate use cases like:
- DataProduct A with table T1 containing column "id"
- DataProduct B with table T2 containing column "id"

## Root Cause Analysis

### Before (Broken)
The `SCB_StandardColumn` entity type in `scb_entity.py` had:
```python
{ "name": "field_name", ..., "isUnique": True, ... }
```

This enforced **global uniqueness** on the column name across the entire Atlas system.

### After (Fixed)
Changed to:
```python
{ "name": "field_name", ..., "isUnique": False, ... }
```

Now allows columns with the same name in different tables/data products.

## Why This Fix Works

Atlas distinguishes between two levels of uniqueness:

1. **Attribute-level uniqueness** (`isUnique` on an attribute):
   - Controls whether that attribute value must be globally unique
   - Before: `field_name` was globally unique ❌
   - After: `field_name` is NOT globally unique ✅

2. **Entity-level uniqueness** (via `qualifiedName`):
   - All entities inherit a `qualifiedName` from parent types
   - For columns: `qualifiedName` = `database.table.field_name`
   - This ensures global uniqueness while allowing name reuse
   - ✅ Still enforced (inherited from DataSet)

## Files Changed

1. **scb_atlas/atlas/atlas_type_def/scb_entity.py**
   - Changed line 45: `"isUnique": True` → `"isUnique": False`

2. **tests/unit/test_atlas_types.py**
   - Added regression test: `test_column_field_name_not_globally_unique()`

3. **BUG_FIX_COLUMN_UNIQUENESS.md** (documentation)

## Verification

✅ All 42 existing tests pass
✅ New regression test passes
✅ No breaking changes to existing functionality

## Deployment Impact

### If Atlas is already deployed:
1. Delete the old `SCB_StandardColumn` type from Atlas
2. Redeploy with updated type definition
3. Re-ingest data products

### If starting fresh:
1. Deploy with updated `scb_entity.py`
2. Proceed normally - no special migration needed

## Expected Behavior After Fix

| Scenario | Before Fix | After Fix |
|----------|-----------|-----------|
| Column "id" in DataProduct A Table T1 | ✅ Works | ✅ Works |
| Column "id" in DataProduct B Table T2 | ❌ Fails: "violates uniqueness" | ✅ Works |
| Column "id" in DataProduct A Table T1 (duplicate) | ❌ Fails: "violates uniqueness" | ❌ Fails (correct - same table) |

## Testing the Fix Locally

```bash
# Run the new regression test
pytest tests/unit/test_atlas_types.py::TestColumnEntityType::test_column_field_name_not_globally_unique -v

# Run all atlas type tests
pytest tests/unit/test_atlas_types.py -v

# Expected: All tests pass ✅
```

