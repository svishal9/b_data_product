# Migration Guide: Using Pydantic Models

This guide shows how to migrate your existing code to use the new Pydantic models.

## Table of Contents

1. [Database Migration](#database-migration)
2. [Table Migration](#table-migration)
3. [Column Migration](#column-migration)
4. [Process Migration](#process-migration)
5. [Data Product Migration](#data-product-migration)
6. [Complete Example](#complete-example)

## Database Migration

### Old Approach

```text
from scb_atlas.atlas.entity_service import create_database_entity

# Using string parameters
create_database_entity(
    atlas_client,
    database_name="finance_db",
    location_uri="hdfs://data/finance",
    description="Finance database"
)
```

### New Approach

```text
from datetime import datetime, timezone
from scb_atlas.atlas.metadata_models import DatabaseModel
from scb_atlas.atlas.service.entity_service import create_database_from_model

# Using Pydantic model with type safety
database_model = DatabaseModel(
    database_name="finance_db",
    location_uri="hdfs://data/finance",
    create_time=datetime.now(timezone.utc),
    description="Finance database"
)

create_database_from_model(atlas_client, database_model)

# Access properties
print(database_model.qualified_name)  # scb:::dp:::finance_db
```

**Benefits**:
- ✅ Type safety - IDE catches errors
- ✅ Validation - Invalid data caught early
- ✅ Automatic qualified name generation
- ✅ Easy to serialize/deserialize

## Table Migration

### Old Approach

```text
from scb_atlas.atlas.entity_service import create_table_entity

create_table_entity(
    atlas_client,
    table_name="trades",
    database_name="finance_db",
    table_type="EXTERNAL",
    description="Trading data"
)
```

### New Approach

```text
from datetime import datetime, timezone
from scb_atlas.atlas.metadata_models import TableModel, TableTypeEnum
from scb_atlas.atlas.service.entity_service import create_table_from_model

table_model = TableModel(
    table_name="trades",
    database_name="finance_db",
    table_type=TableTypeEnum.EXTERNAL,
    description="Trading data",
    create_time=datetime.now(timezone.utc)
)

# Get parent database qualified name
db_qname = database_model.qualified_name

create_table_from_model(
    atlas_client,
    table_model,
    database_qualified_name=db_qname
)

# Access properties
print(table_model.qualified_name)  # scb:::dp:::finance_db.trades
```

**Benefits**:
- ✅ Type-safe enum for table type
- ✅ Automatic qualified name with database prefix
- ✅ Clear relationship to parent database

## Column Migration

### Old Approach

```text
from scb_atlas.atlas.entity_service import create_column_entity

create_column_entity(
    atlas_client,
    column_name="trade_id",
    data_type="string",
    table_name="trades",
    comment="Unique trade identifier",
    position=1
)
```

### New Approach

```text
from scb_atlas.atlas.metadata_models import ColumnModel, PIIEnum
from scb_atlas.atlas.service.entity_service import create_column_from_model

column_model = ColumnModel(
    column_name="trade_id",
    data_type="string",
    table_name="trades",
    database_name="finance_db",
    description="Unique trade identifier",
    position=1,
    pii=PIIEnum.NO
)

create_column_from_model(
    atlas_client,
    column_model,
    table_qualified_name=table_model.qualified_name
)

# Access properties
print(column_model.qualified_name)  # scb:::dp:::finance_db.trades.trade_id
```

**Benefits**:
- ✅ Type-safe PII enum
- ✅ Automatic qualified name with full path
- ✅ Clear relationship to parent table

## Process Migration

### Old Approach

```text
from scb_atlas.atlas.entity_service import create_process_entity_advanced

create_process_entity_advanced(
    atlas_client,
    process_name="daily_aggregation",
    query_id="proc_001",
    query_text="SELECT * FROM trades",
    user_name="data_pipeline",
    start_time=1774338243657,
    end_time=1774341843657,
    input_refs=[("SCB_Table", "scb:::dp:::finance_db.trades")],
    output_refs=[("SCB_Table", "scb:::dp:::finance_db.daily_summary")]
)
```

### New Approach

```text
from scb_atlas.atlas.metadata_models import ProcessModel
from scb_atlas.atlas.service.entity_service import create_process_from_model

process_model = ProcessModel(
    process_name="daily_aggregation",
    query_id="proc_001",
    query_text="""
        SELECT 
            trade_date,
            COUNT(*) as total_trades,
            SUM(amount) as total_volume
        FROM finance_db.trades
        GROUP BY trade_date
    """,
    user_name="data_pipeline",
    start_time=1774338243657,
    end_time=1774341843657
)

create_process_from_model(
    atlas_client,
    process_model,
    input_refs=[("SCB_Table", "scb:::dp:::finance_db.trades")],
    output_refs=[("SCB_Table", "scb:::dp:::finance_db.daily_summary")]
)

# Access properties
print(process_model.qualified_name)  # scb:::dp:::proc_proc_001
```

**Benefits**:
- ✅ Clear model structure
- ✅ Automatic qualified name from query_id
- ✅ Multi-line query support

## Data Product Migration

### Old Approach

```text
# Note: This demonstrates the older pattern for reference
# Using direct API calls and string-based parameters
from scb_atlas.atlas.atlas_client import create_atlas_client
from scb_atlas.atlas.service.entity_service import create_data_product_from_model

atlas_client = create_atlas_client()

# Manually constructing entity payload (error-prone)
product_payload = {
    "typeName": "SCB_DataProduct",
    "attributes": {
        "name": "Finance Trading Data Product",
        "description": "Trading and transaction data",
        "data_product_category": "Source-Aligned",
        "owner": "John Doe",
        "qualifiedName": "scb:::dp:::FM_Trading"
    }
}

# Direct API call without validation
result = atlas_client.entity_post(product_payload)
```

### New Approach

```text
from datetime import date
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

data_product_model = CompleteDataProductModel(
    basic_metadata=DataProductBasicMetadata(
        data_product_name="Finance Trading Data Product",
        description="Trading and transaction data",
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
        geo_location_access=["EU", "Singapore"],
        regulatory_flags=["BCBS239"],
        certifications=["Attested by GCFO"]
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

create_data_product_from_model(
    atlas_client,
    data_product_model,
    input_port_qualified_names=["scb:::dp:::finance_db.trades"],
    output_port_qualified_name="scb:::dp:::finance_db.daily_summary"
)
```

**Benefits**:
- ✅ All metadata in one model
- ✅ Clear structure with nested models
- ✅ Type-safe enums for lifecycle status
- ✅ Comprehensive governance metadata

## Complete Example

Here's a complete migration showing all entity types:

### Before Migration

```text
from scb_atlas.atlas.atlas_client import create_atlas_client
from scb_atlas.atlas.service.entity_service import (
    create_database_entity,
    create_table_entity,
    create_column_entity,
    create_process_entity_advanced,
)

atlas_client = create_atlas_client()

# Create database
create_database_entity(atlas_client, "finance_db", "hdfs://data/finance")

# Create table
create_table_entity(atlas_client, "trades", "finance_db", "EXTERNAL")

# Create column
create_column_entity(atlas_client, "trade_id", "string", "trades")

# Create process
create_process_entity_advanced(
    atlas_client,
    "aggregation",
    "proc_001",
    "SELECT * FROM trades"
)
```

### After Migration

```text
from datetime import datetime, timezone
from scb_atlas.atlas.atlas_client import create_atlas_client
from scb_atlas.atlas.metadata_models import (
    DatabaseModel,
    TableModel,
    ColumnModel,
    ProcessModel,
    TableTypeEnum,
    PIIEnum,
)
from scb_atlas.atlas.service.entity_service import (
    create_database_from_model,
    create_table_from_model,
    create_column_from_model,
    create_process_from_model,
)

atlas_client = create_atlas_client()

# Create database model
database_model = DatabaseModel(
    database_name="finance_db",
    location_uri="hdfs://data/finance",
    create_time=datetime.now(timezone.utc)
)
create_database_from_model(atlas_client, database_model)

# Create table model
table_model = TableModel(
    table_name="trades",
    database_name="finance_db",
    table_type=TableTypeEnum.EXTERNAL,
    create_time=datetime.now(timezone.utc)
)
create_table_from_model(atlas_client, table_model, database_model.qualified_name)

# Create column model
column_model = ColumnModel(
    column_name="trade_id",
    data_type="string",
    table_name="trades",
    database_name="finance_db",
    pii=PIIEnum.NO
)
create_column_from_model(atlas_client, column_model, table_model.qualified_name)

# Create process model
process_model = ProcessModel(
    process_name="aggregation",
    query_id="proc_001",
    query_text="SELECT * FROM trades"
)
create_process_from_model(
    atlas_client,
    process_model,
    input_refs=[("SCB_Table", table_model.qualified_name)]
)
```

**Key Differences**:
- Models are created first, then passed to creation functions
- Qualified names are automatically generated and used for relationships
- Type-safe enums ensure consistency
- Code is more readable and maintainable

## Validation Example

```text
from pydantic import ValidationError
from scb_atlas.atlas.metadata_models import DatabaseModel

# Before: Errors would occur during Atlas API call
# After: Errors caught immediately

try:
    # Missing required field
    db = DatabaseModel(location_uri="hdfs://data/finance")
except ValidationError as e:
    print(f"Validation error: {e}")
    # database_name: field required

try:
    # Invalid type
    db = DatabaseModel(
        database_name="finance_db",
        location_uri="hdfs://data/finance",
        create_time="2026-03-24"  # Should be date, not string
    )
except ValidationError as e:
    print(f"Type error: {e}")
    # create_time: input should be a valid date
```

## Backward Compatibility

**Important**: Old functions still work!

```text
# Old way still works
create_database_entity(atlas_client, "finance_db", "hdfs://data/finance")

# New way is recommended for new code
database_model = DatabaseModel(
    database_name="finance_db",
    location_uri="hdfs://data/finance"
)
create_database_from_model(atlas_client, database_model)
```

You can migrate gradually:
1. Use new models for new code
2. Keep old functions for existing code
3. Gradually refactor existing code to use models

## Testing Migration

Before and after should produce the same results:

```text
# Both create the same Atlas entity
old_result = create_database_entity(atlas_client, "test_db", "hdfs://test")
new_model = DatabaseModel(database_name="test_db", location_uri="hdfs://test")
new_result = create_database_from_model(atlas_client, new_model)

# Same entities created in Atlas
```

## Summary

**Migration Checklist**:

- [ ] Replace `create_database_entity()` with `DatabaseModel` + `create_database_from_model()`
- [ ] Replace `create_table_entity()` with `TableModel` + `create_table_from_model()`
- [ ] Replace `create_column_entity()` with `ColumnModel` + `create_column_from_model()`
- [ ] Replace `create_process_entity_advanced()` with `ProcessModel` + `create_process_from_model()`
- [ ] Replace `create_data_product_entity()` with `CompleteDataProductModel` + `create_data_product_from_model()`
- [ ] Run tests to verify
- [ ] Update documentation

**Benefits After Migration**:
- ✅ Type safety and IDE support
- ✅ Early error detection
- ✅ Consistent API across all entity types
- ✅ Automatic qualified name generation
- ✅ Easier to maintain and extend

