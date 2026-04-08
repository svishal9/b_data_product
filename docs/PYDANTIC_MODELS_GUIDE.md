# Using Pydantic Models for Atlas Entity Creation

This guide explains how to use the new Pydantic models for creating and managing Atlas entities. The Pydantic models provide:

- **Type safety** - Catch errors at model validation time
- **Clear documentation** - Each field has a description
- **Extensibility** - Easy to add new fields or models
- **Consistency** - Standardized entity creation

## Overview of Pydantic Models

All Pydantic models are defined in `scb_atlas/atlas/entity_models.py` and include:

### Core Entity Models

1. **DatabaseModel** - For creating SCB_Database entities
2. **TableModel** - For creating SCB_Table entities
3. **ColumnModel** - For creating SCB_Column entities
4. **ProcessModel** - For creating SCB_Process entities
5. **CompleteDataProductModel** - For creating SCB_DataProduct entities with all metadata

### Data Product Metadata Models

For comprehensive data product creation:

- **DataProductBasicMetadata** - Name, description, category
- **DataProductBusinessMetadata** - Business purpose, GCFO owner
- **DataProductClassification** - Sensitivity, personal data flag, compliance info
- **DataProductPorts** - Input/output ports, delivery channels, access rules
- **DataProductUsage** - User count, systems, use cases
- **DataProductLifecycle** - Version, environment, lifecycle status, delivery date
- **DataProductGovernanceMetadata** - Domain, owners, stewards, SLA, retention

## Usage Examples

### 1. Creating a Database

```text
from datetime import datetime, timezone
from scb_atlas.atlas.metadata_models import DatabaseModel
from scb_atlas.atlas.service.entity_service import create_database_from_model
from scb_atlas.atlas.atlas_client import create_atlas_client

# Initialize Atlas client
atlas_client = create_atlas_client()

# Create database model
database_model = DatabaseModel(
    database_name="finance_db",
    location_uri="hdfs://data/finance",
    create_time=datetime.now(timezone.utc),
    description="Finance database containing trading and transaction data"
)

# Create in Atlas
create_database_from_model(atlas_client, database_model)

# Access qualified name
print(database_model.qualified_name)  # Output: scb:::dp:::finance_db
```

### 2. Creating a Table

```text
from scb_atlas.atlas.metadata_models import TableModel
from scb_atlas.atlas.service.entity_service import create_table_from_model

# Create table model
table_model = TableModel(
    table_name="trades",
    database_name="finance_db",
    description="FX and derivatives trading transactions",
    table_type="EXTERNAL",
    create_time=date(2026, 3, 24)
)

# Create in Atlas with parent database relationship
create_table_from_model(
    atlas_client,
    table_model,
    database_qualified_name=database_model.qualified_name
)

# Access qualified name
print(table_model.qualified_name)  # Output: scb:::dp:::finance_db.trades
```

### 3. Creating Columns

```text
from scb_atlas.atlas.metadata_models import ColumnModel
from scb_atlas.atlas.service.entity_service import create_column_from_model

# Create column models
column_model = ColumnModel(
    column_name="trade_id",
    data_type="string",
    description="Unique trade identifier",
    table_name="trades",
    database_name="finance_db",
    position=1,
    pii=PIIEnum.NO
)

# Create in Atlas with parent table relationship
create_column_from_model(
    atlas_client,
    column_model,
    table_qualified_name=table_model.qualified_name
)

print(column_model.qualified_name)  # Output: scb:::dp:::finance_db.trades.trade_id
```

### 4. Creating a Process

```text
from scb_atlas.atlas.metadata_models import ProcessModel
from scb_atlas.atlas.service.entity_service import create_process_from_model

# Create process model
process_model = ProcessModel(
    process_name="daily_trade_aggregation",
    query_id="proc_daily_agg_001",
    query_text="""
        SELECT trade_date, COUNT(*) as total_trades
        FROM finance_db.trades
        WHERE trade_date = CURRENT_DATE
        GROUP BY trade_date
    """,
    user_name="data_pipeline",
    start_time=1774338243657,
    end_time=1774341843657
)

# Create in Atlas with input/output relationships
create_process_from_model(
    atlas_client,
    process_model,
    input_refs=[("SCB_Table", "scb:::dp:::finance_db.trades")],
    output_refs=[("SCB_Table", "scb:::dp:::finance_db.daily_summary")]
)

print(process_model.qualified_name)  # Output: scb:::dp:::proc_proc_daily_agg_001
```

### 5. Creating a Complete Data Product

```text
from scb_atlas.atlas.metadata_models import (
    CompleteDataProductModel,
    DataProductBasicMetadata,
    DataProductBusinessMetadata,
    DataProductClassification,
    DataProductPorts,
    DataProductUsage,
    DataProductLifecycle,
    DataProductGovernanceMetadata,
    LifecycleStatusEnum,
)
from scb_atlas.atlas.service.entity_service import create_data_product_from_model

# Create comprehensive data product model
data_product_model = CompleteDataProductModel(
    basic_metadata=DataProductBasicMetadata(
        data_product_name="Finance Trading Data Product",
        description="Comprehensive data product for trading and transaction data",
        data_product_category="Source-Aligned"
    ),
    business_metadata=DataProductBusinessMetadata(
        business_purpose="Source Aligned DP Finance",
        gcfo_owner_name="Jane Smith",
        gcfo_owner_contact="jane.smith@company.com"
    ),
    classification=DataProductClassification(
        sensitivity="Internal",
        personal=False,
        geo_location_access=["EU", "Singapore", "UK"],
        regulatory_flags=["BCBS239", "MAS TRM"],
        certifications=["Attested by GCFO"],
        approval="Approved for Enterprise Use"
    ),
    ports=DataProductPorts(
        data_product_input_ports=["scb:::dp:::finance_db.trades"],
        data_product_output_port="scb:::dp:::finance_db.daily_summary",
        delivery_channels=["REST API", "PowerBI"],
        data_landing_pattern="API - FDP Staging Table"
    ),
    usage=DataProductUsage(
        users=2500,
        systems=5,
        usecases=["Accounting", "Capital", "Liquidity"]
    ),
    lifecycle=DataProductLifecycle(
        version="1.0",
        environment="Production",
        lifecycle_status=LifecycleStatusEnum.PUBLISH_CONSUME,
        delivery_date=date(2026, 2, 1)
    ),
    governance_metadata=DataProductGovernanceMetadata(
        domain="FM",
        sub_domain="FX",
        refresh_frequency="Daily (T+0)",
        data_product_owner="John Doe",
        data_product_owner_contact_information="john.doe@company.com",
        domain_owner="FM Domain Owner",
        data_steward="Alice Johnson",
        support_contact="Support Team",
        data_retention="3 years",
        sla="99.9% availability"
    )
)

# Create in Atlas with port relationships
create_data_product_from_model(
    atlas_client,
    data_product_model,
    input_port_qualified_names=["scb:::dp:::finance_db.trades"],
    output_port_qualified_name="scb:::dp:::finance_db.daily_summary"
)

print(data_product_model.qualified_name)
```

## Model Field Validation

All Pydantic models validate their inputs. For example:

```text
from pydantic import ValidationError
from scb_atlas.atlas.metadata_models import DatabaseModel

# This will raise ValidationError - missing required field
try:
    db = DatabaseModel(location_uri="hdfs://data")
except ValidationError as e:
    print(e)
    # ValidationError: database_name: field required
```

## Converting to Atlas Entity Dictionary

Each model includes a `to_atlas_entity()` method that converts the model to Atlas API format:

```text
database_model = DatabaseModel(
    database_name="finance_db",
    location_uri="hdfs://data/finance"
)

entity_dict = database_model.to_atlas_entity()
# Output:
# {
#     "typeName": "SCB_Database",
#     "attributes": {
#         "database_name": "finance_db",
#         "locationUri": "hdfs://data/finance",
#         ...
#     }
# }
```

## Automatic Qualified Name Generation

All models use `@computed_field` to automatically generate qualified names:

```text
table_model = TableModel(
    table_name="trades",
    database_name="finance_db"
)

# Qualified name is automatically generated
print(table_model.qualified_name)  # scb:::dp:::finance_db.trades
```

## Optional Fields

Most fields are optional. Create minimal models when needed:

```text
# Minimal table - only required fields
table_model = TableModel(
    table_name="trades"
)

# Enhanced table - with optional fields
table_model = TableModel(
    table_name="trades",
    database_name="finance_db",
    description="Trading data",
    table_type="EXTERNAL",
    temporary=False
)
```

## Enums for Standardized Values

Use provided Enums for consistency:

```text
from scb_atlas.atlas.metadata_models import (
    TableTypeEnum,
    PIIEnum,
    LifecycleStatusEnum,
)

# Table type enum
table_model = TableModel(
    table_name="trades",
    table_type=TableTypeEnum.EXTERNAL  # Not just "EXTERNAL" string
)

# PII enum
column_model = ColumnModel(
    column_name="customer_id",
    data_type="string",
    pii=PIIEnum.YES  # Clearly indicates PII data
)

# Lifecycle status enum
lifecycle = DataProductLifecycle(
    lifecycle_status=LifecycleStatusEnum.PUBLISH_CONSUME
)
```

## Running the Example

Execute the example script to create sample entities:

```bash
uv run python create_entities_with_pydantic.py
```

This will:
1. Create all necessary type definitions
2. Create a sample database
3. Create sample tables
4. Create sample columns
5. Create a sample process
6. Create a complete data product with all metadata

## Benefits Over Manual Dictionary Creation

### Before (Manual Dictionaries):
```text
entity_attribute = {
    'entity': {
        'typeName': 'SCB_Database',
        'attributes': {
            'database_name': 'finance_db',
            'locationUri': 'hdfs://data/finance',
            'createTime': '2026-03-24',
            'description': 'Finance database',
            'qualifiedName': 'scb:::dp:::finance_db',
            'name': 'finance_db',
        }
    }
}
```

### After (Pydantic Models):
```text
database_model = DatabaseModel(
    database_name="finance_db",
    location_uri="hdfs://data/finance",
    create_time=date(2026, 3, 24),
    description="Finance database"
)
```

**Advantages:**
- ✅ Type checking - Errors caught at validation time
- ✅ Clear field names - IDE autocomplete support
- ✅ Documentation - Each field has a description
- ✅ Consistency - Standard structure across all models
- ✅ Maintainability - Changes in one place affect all code
- ✅ Validation - Invalid data is caught immediately

## Adding New Fields

To extend models with custom fields:

- `from pydantic import BaseModel, Field`
- `class ExtendedDatabaseModel(DatabaseModel):`
- `    custom_metadata: Optional[str] = Field(None, description="Custom metadata")`
- `    owner_team: Optional[str] = Field(None, description="Team owning the database")`
- `    def to_atlas_entity(self) -> dict: ...`

## Summary

The Pydantic model approach provides:

1. **Type Safety** - Validation at model creation time
2. **Clarity** - Self-documenting code
3. **Flexibility** - Optional fields, extensibility
4. **Consistency** - Standardized across all entities
5. **Maintainability** - Changes propagated automatically

For more examples, see `create_entities_with_pydantic.py`.
