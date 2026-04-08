# Bug Fix: Column Uniqueness Constraint

## Issue
When creating columns with the same name in different data products, Atlas rejects the creation with error:
```
violates a uniqueness constraint
```

## Root Cause
In `scb_atlas/atlas/atlas_type_def/scb_entity.py`, the `SCB_StandardColumn` entity type had the `field_name` attribute marked as globally unique (`"isUnique": True`). This prevented any two columns from having the same name anywhere in the system, even if they belonged to different tables or data products.

## Solution
Changed the `field_name` attribute from `"isUnique": True` to `"isUnique": False` in `scb_entity.py`.

**Key insight**: 
- Columns should be allowed to have the same field name if they exist in different tables/data products
- Global uniqueness is enforced by the `qualifiedName` attribute (inherited from the `DataSet` super type)
- `qualifiedName` includes the full hierarchical path: `database.table.column_name`, which is globally unique
- Allowing `field_name` to be non-unique while `qualifiedName` is unique enables proper semantic modeling

## Changes Made

### 1. Fixed Type Definition (`scb_atlas/atlas/atlas_type_def/scb_entity.py`)
```python
# Before:
{ "name": "field_name", "displayName": "Field Name", "typeName": "string", "cardinality": "SINGLE", "isOptional": False, "isUnique": True, "isIndexable": True }

# After:
{ "name": "field_name", "displayName": "Field Name", "typeName": "string", "cardinality": "SINGLE", "isOptional": False, "isUnique": False, "isIndexable": True }
```

### 2. Added Regression Test (`tests/unit/test_atlas_types.py`)
Added `test_column_field_name_not_globally_unique()` to ensure:
- `field_name` is not marked as globally unique
- Same column names can exist in different tables/data products
- Prevents future regression of this bug

## Testing
All tests pass:
```
tests/unit/test_atlas_types.py::TestColumnEntityType::test_column_entity_extends_dataset PASSED
tests/unit/test_atlas_types.py::TestColumnEntityType::test_column_entity_has_required_attributes PASSED
tests/unit/test_atlas_types.py::TestColumnEntityType::test_column_attributes_types PASSED
tests/unit/test_atlas_types.py::TestColumnEntityType::test_column_optional_attributes_are_optional PASSED
tests/unit/test_atlas_types.py::TestColumnEntityType::test_column_field_name_not_globally_unique PASSED ✅ (New)
```

## Impact
- ✅ Allows columns with the same name in different tables/data products
- ✅ Maintains global uniqueness via `qualifiedName` (inherited from DataSet)
- ✅ No breaking changes - existing qualified names remain valid
- ✅ Aligns with standard database modeling patterns (columns can be reused across tables)

## Migration
If you have Atlas already deployed with `SCB_StandardColumn` type:
1. Delete the existing `SCB_StandardColumn` type from Atlas
2. Apply the updated type definition (which automatically recreates it with the fix)
3. Re-ingest data products - columns will now be created successfully even with name reuse across data products

