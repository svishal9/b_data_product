# Column Uniqueness Bug Fix - Technical Details

## Issue
Atlas rejects column creation with error "violates a uniqueness constraint" when different data products contain columns with the same name.

## Root Cause
In `scb_atlas/atlas/atlas_type_def/scb_entity.py`, the `SCB_StandardColumn` entity had `field_name` marked as globally unique (`"isUnique": True`). This prevented semantic column name reuse across different tables/data products.

## Solution Applied

### File: `scb_atlas/atlas/atlas_type_def/scb_entity.py`
**Line 45: Changed `field_name` uniqueness constraint**

```diff
scb_standard_column = BaseEntityCategory(
    atlas_name="SCB_StandardColumn",
    display_name="SCB Standard Column",
    super_types=["DataSet"],
    attributes=[
-       { "name": "field_name", "displayName": "Field Name", "typeName": "string", "cardinality": "SINGLE", "isOptional": False, "isUnique": True, "isIndexable": True },
+       { "name": "field_name", "displayName": "Field Name", "typeName": "string", "cardinality": "SINGLE", "isOptional": False, "isUnique": False, "isIndexable": True },
        { "name": "data_type", "displayName": "Data Type", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
```

### File: `tests/unit/test_atlas_types.py`
**Added regression test to prevent future recurrence**

```python
def test_column_field_name_not_globally_unique(self):
    """Test that field_name is NOT globally unique (allows same column name in different tables/data products).
    
    This is a regression test for the bug where field_name was marked as unique,
    causing "violates uniqueness constraint" errors when creating columns with
    the same name in different data products.
    
    Uniqueness should be enforced at the qualifiedName level (inherited from DataSet),
    not at the field_name level, to allow semantic reuse of column names across tables.
    """
    col_entity = [scb_standard_column.prepare_atlas_type_definition()][0]
    attrs = {attr['name']: attr for attr in col_entity['attributeDefs']}

    # field_name should NOT be unique globally
    assert attrs['field_name']['isUnique'] == False, \
        "field_name must not be globally unique to allow same column name in different tables"
```

## Why This Works

### Atlas Uniqueness Model
1. **Attribute Uniqueness** (`isUnique` flag):
   - Controls if the attribute value must be unique **globally**
   - Was preventing same column names across tables ❌
   - Now allows name reuse ✅

2. **Entity Uniqueness** (`qualifiedName`):
   - Built-in Atlas feature (inherited from DataSet super type)
   - Automatically includes the full path: `database.table.column_name`
   - Guarantees global uniqueness without restricting field_name ✅

### Result
- ✅ Column "id" can exist in DataProduct A Table T1
- ✅ Column "id" can exist in DataProduct B Table T2
- ✅ Both have unique qualifiedNames (`dp_a.t1.id` vs `dp_b.t2.id`)
- ✅ No conflicts or constraint violations

## Testing

### All Tests Pass (42/42)
```
tests/unit/test_atlas_types.py::TestColumnEntityType::test_column_entity_extends_dataset PASSED
tests/unit/test_atlas_types.py::TestColumnEntityType::test_column_entity_has_required_attributes PASSED
tests/unit/test_atlas_types.py::TestColumnEntityType::test_column_attributes_types PASSED
tests/unit/test_atlas_types.py::TestColumnEntityType::test_column_optional_attributes_are_optional PASSED
tests/unit/test_atlas_types.py::TestColumnEntityType::test_column_field_name_not_globally_unique PASSED ✅ NEW
... (37 more)
```

## Migration Guide

### For Running Deployments
1. Stop ingestion processes
2. Connect to Atlas database
3. Delete `SCB_StandardColumn` type (this also removes existing columns - they'll need to be re-created)
4. Deploy updated application code
5. Re-ingest data products - columns will now be created successfully

### For Fresh Deployments
1. Deploy application with fix
2. Create type definitions (they'll include the fix automatically)
3. Proceed normally

## Backward Compatibility
- ✅ Existing qualified names remain valid
- ✅ No changes to entity structure
- ✅ Only the uniqueness constraint is relaxed
- ✅ Atlas will accept re-ingestion of same data

## Verification Commands
```bash
# Check that the fix is in place
grep -A1 '"field_name"' scb_atlas/atlas/atlas_type_def/scb_entity.py | grep "isUnique"
# Should output: "isUnique": False

# Run regression test
pytest tests/unit/test_atlas_types.py::TestColumnEntityType::test_column_field_name_not_globally_unique -v

# Run all type definition tests  
pytest tests/unit/test_atlas_types.py -v

# Expected: All pass with no failures
```

## Related Documentation
- See `BUG_FIX_COLUMN_UNIQUENESS.md` for detailed explanation
- See `COLUMN_UNIQUENESS_FIX_SUMMARY.md` for high-level overview
- See `scb_relationships.py` for column relationship definitions (unchanged)

