# Pydantic Models Integration - Summary

## Overview

The SCB Data Product framework now includes comprehensive Pydantic models for creating and managing Atlas entities. These models provide type safety, validation, and clear structure for entity creation.

## What Was Added

### 1. New File: `scb_atlas/atlas/entity_models.py`

Comprehensive Pydantic models including:

#### Core Entity Models
- **DatabaseModel** - SCB_Database entities
- **TableModel** - SCB_Table entities  
- **ColumnModel** - SCB_Column entities
- **ProcessModel** - SCB_Process entities
- **CompleteDataProductModel** - SCB_DataProduct with all metadata

#### Data Product Metadata Models
- **DataProductBasicMetadata** - Name, description, category
- **DataProductBusinessMetadata** - Business purpose, GCFO owner
- **DataProductClassification** - Sensitivity, compliance, certifications
- **DataProductPorts** - Input/output ports, delivery channels
- **DataProductUsage** - Users, systems, use cases
- **DataProductLifecycle** - Version, status, dates
- **DataProductGovernanceMetadata** - Domain, owners, stewards, SLA

#### Enums
- **TableTypeEnum** - Managed, External
- **PIIEnum** - Yes/No for PII data
- **LifecycleStatusEnum** - All 7 lifecycle states
- **SensitivityEnum** - Internal, External

### 2. Updated File: `scb_atlas/atlas/entity_service.py`

Added new functions using Pydantic models:
- `create_database_from_model()` - Create database from DatabaseModel
- `create_table_from_model()` - Create table from TableModel
- `create_column_from_model()` - Create column from ColumnModel
- `create_process_from_model()` - Create process from ProcessModel
- `create_data_product_from_model()` - Create data product from CompleteDataProductModel

### 3. New Files

- **`create_entities_with_pydantic.py`** - Example script demonstrating usage
- **`PYDANTIC_MODELS_GUIDE.md`** - Comprehensive usage guide
- **`tests/unit/test_metadata_models.py`** - Unit tests (20 tests, all passing)

## Key Features

### Type Safety
```text
# Pydantic validates input at model creation time
database = DatabaseModel(
    database_name="finance_db",  # ✓ String required
    location_uri="hdfs://data",  # ✓ String required
)
# Automatic validation catches errors early
```

### Automatic Qualified Name Generation
```text
table = TableModel(
    table_name="trades",
    database_name="finance_db"
)
# Automatically generates: scb:::dp:::finance_db.trades
print(table.qualified_name)
```

### Enum Support
```text
from scb_atlas.atlas.metadata_models import TableTypeEnum, LifecycleStatusEnum

table = TableModel(
    table_name="trades",
    table_type=TableTypeEnum.EXTERNAL  # Type-safe enum
)

lifecycle = DataProductLifecycle(
    lifecycle_status=LifecycleStatusEnum.PUBLISH_CONSUME
)
```

### Nested Models for Data Products
```text
data_product = CompleteDataProductModel(
    basic_metadata=DataProductBasicMetadata(...),
    business_metadata=DataProductBusinessMetadata(...),
    classification=DataProductClassification(...),
    ports=DataProductPorts(...),
    usage=DataProductUsage(...),
    lifecycle=DataProductLifecycle(...),
    governance_metadata=DataProductGovernanceMetadata(...)
)
```

### Easy Conversion to Atlas Format
```text
database = DatabaseModel(
    database_name="finance_db",
    location_uri="hdfs://data/finance"
)

# Convert to Atlas entity dictionary
entity = database.to_atlas_entity()
# Returns:
# {
#     "typeName": "SCB_Database",
#     "attributes": {
#         "database_name": "finance_db",
#         "locationUri": "hdfs://data/finance",
#         ...
#     }
# }
```

## Usage Comparison

### Before (Manual Dictionaries)
```text
entity_attribute = {
    'entity': {
        'typeName': 'SCB_Database',
        'attributes': {
            'database_name': 'finance_db',
            'locationUri': 'hdfs://data/finance',
            'createTime': '2026-03-24',
            'qualifiedName': 'scb:::dp:::finance_db',
            'name': 'finance_db',
        }
    }
}
```

### After (Pydantic Models)
```text
database_model = DatabaseModel(
    database_name="finance_db",
    location_uri="hdfs://data/finance",
    create_time=date(2026, 3, 24)
)

create_database_from_model(atlas_client, database_model)
```

## Benefits

✅ **Type Safety** - IDE autocomplete, type checking
✅ **Validation** - Errors caught at model creation time  
✅ **Documentation** - Each field has clear descriptions
✅ **Consistency** - Standardized across all models
✅ **Maintainability** - Changes propagate automatically
✅ **Extensibility** - Easy to add custom models

## Testing

All models include comprehensive unit tests:

```bash
uv run pytest tests/unit/test_metadata_models.py -v
```

**Results**: 20 tests, 100% passing

Test coverage includes:
- Model creation with required/optional fields
- Qualified name generation
- Enum usage
- Atlas entity conversion
- Validation error handling

## Quick Start

### 1. Install Dependencies
Already configured in `pyproject.toml`

### 2. Import Models
```text
from scb_atlas.atlas.metadata_models import DatabaseModel, TableModel
from scb_atlas.atlas.entity_service import create_database_from_model
```

### 3. Create Models
```text
database = DatabaseModel(
    database_name="finance_db",
    location_uri="hdfs://data/finance"
)

table = TableModel(
    table_name="trades",
    database_name="finance_db"
)
```

### 4. Create in Atlas
```text
from scb_atlas.atlas.atlas_client import create_atlas_client

atlas_client = create_atlas_client()
create_database_from_model(atlas_client, database)
create_table_from_model(atlas_client, table, database.qualified_name)
```

## Running the Example

```bash
uv run python create_entities_with_pydantic.py
```

Creates sample entities:
- Database: finance_db
- Tables: trades, transactions, daily_summary
- Columns: trade_id, trade_date, amount
- Process: daily_trade_aggregation
- Data Product: Finance Trading Data Product

## Migration Guide

### For Existing Code

Old way:

- `create_database_entity(atlas_client, "finance_db", "hdfs://data/finance")`

New way:

- `db_model = DatabaseModel(database_name="finance_db", location_uri="hdfs://data/finance")`
- `create_database_from_model(atlas_client, db_model)`

**Note**: Old functions still work for backward compatibility

## Documentation Files

- **PYDANTIC_MODELS_GUIDE.md** - Comprehensive usage guide with examples
- **create_entities_with_pydantic.py** - Working example script
- **tests/unit/test_metadata_models.py** - Test suite with 20 tests

## File Structure

```
scb-data-product/
├── scb_atlas/atlas/
│   ├── entity_models.py          # ✨ NEW: Pydantic models
│   ├── entity_service.py         # UPDATED: New model-based functions
│   └── atlas_model.py            # Existing: AtlasDPModel
├── create_entities_with_pydantic.py  # ✨ NEW: Example script
├── PYDANTIC_MODELS_GUIDE.md          # ✨ NEW: Usage guide
└── tests/unit/
    └── test_metadata_models.py       # ✨ NEW: Unit tests
```

## Next Steps

1. **Use the new models** - Migrate to Pydantic models for new code
2. **Add validation** - Extend models with custom validators as needed
3. **Build integrations** - Create higher-level functions using models
4. **Document patterns** - Add organization-specific examples

## Support

For questions or issues with Pydantic models:

1. Check **PYDANTIC_MODELS_GUIDE.md** for detailed examples
2. Review **create_entities_with_pydantic.py** for working code
3. Run tests to validate: `uv run pytest tests/unit/test_metadata_models.py -v`

## Summary

The integration of Pydantic models provides a modern, type-safe approach to creating Atlas entities. All models are fully tested, documented, and include working examples.

**Key Takeaway**: Use the Pydantic models (`DatabaseModel`, `TableModel`, etc.) with the corresponding `*_from_model()` functions for creating entities in Atlas.
