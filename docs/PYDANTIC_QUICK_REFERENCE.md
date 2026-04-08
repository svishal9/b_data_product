<!--suppress PyUnresolvedReferences,PyArgumentList,PyTypeChecker,PyRedeclaration,PyStatementEffect,SqlNoDataSourceInspection -->

# Pydantic Models - Quick Reference Card

## Model Quick Reference

### DatabaseModel
```text
from scb_atlas.atlas.metadata_models import DatabaseModel
from scb_atlas.atlas.service.entity_service import create_database_from_model

db = DatabaseModel(
    database_name="finance_db",           # Required: string
    location_uri="hdfs://data/finance",   # Required: string
    create_time=date(2026, 3, 24),        # Optional: date
    description="Finance database"         # Optional: string
)

create_database_from_model(atlas_client, db)
# Auto-generated qualified name: scb:::dp:::finance_db
```

---

### TableModel
```text
from scb_atlas.atlas.metadata_models import TableModel, TableTypeEnum
from scb_atlas.atlas.service.entity_service import create_table_from_model

table = TableModel(
    table_name="trades",                  # Required: string
    database_name="finance_db",           # Optional: string (for qualified name)
    table_type=TableTypeEnum.EXTERNAL,    # Optional: EXTERNAL or MANAGED
    description="Trading data",           # Optional: string
    create_time=date(2026, 3, 24),       # Optional: date
    temporary=False,                      # Optional: boolean
)

create_table_from_model(atlas_client, table, db.qualified_name)
# Auto-generated: scb:::dp:::finance_db.trades
```

---

### ColumnModel
```text
from scb_atlas.atlas.metadata_models import ColumnModel, PIIEnum
from scb_atlas.atlas.service.entity_service import create_column_from_model

column = ColumnModel(
    column_name="trade_id",               # Required: string
    data_type="string",                   # Required: string
    table_name="trades",                  # Optional: string
    database_name="finance_db",           # Optional: string
    description="Unique trade identifier",# Optional: string
    position=1,                           # Optional: int
    pii=PIIEnum.NO,                       # Optional: YES or NO
    create_time=date(2026, 3, 24),       # Optional: date
)

create_column_from_model(atlas_client, column, table.qualified_name)
# Auto-generated: scb:::dp:::finance_db.trades.trade_id
```

---

### ProcessModel
```text
from scb_atlas.atlas.metadata_models import ProcessModel
from scb_atlas.atlas.service.entity_service import create_process_from_model

process = ProcessModel(
    process_name="daily_aggregation",     # Required: string
    query_id="proc_001",                  # Required: string
    query_text="SELECT * FROM trades",    # Required: string
    user_name="data_pipeline",            # Optional: string
    start_time=1774338243657,             # Optional: int (epoch ms)
    end_time=1774341843657,               # Optional: int (epoch ms)
)

create_process_from_model(
    atlas_client,
    process,
    input_refs=[("SCB_Table", "scb:::dp:::finance_db.trades")],
    output_refs=[("SCB_Table", "scb:::dp:::finance_db.daily_summary")]
)
# Auto-generated: scb:::dp:::proc_proc_001
```

---

### CompleteDataProductModel
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

dp = CompleteDataProductModel(
    basic_metadata=DataProductBasicMetadata(
        data_product_name="Finance DP",
        description="Finance data product",
        data_product_category="Source-Aligned"
    ),
    business_metadata=DataProductBusinessMetadata(
        business_purpose="Finance operations",
        gcfo_owner_name="Jane Smith",
        gcfo_owner_contact="jane@company.com"
    ),
    classification=DataProductClassification(
        sensitivity="Internal",
        personal=False,
        certifications=["Attested by GCFO"]
    ),
    ports=DataProductPorts(
        data_product_input_ports=["scb:::dp:::finance_db.trades"],
        data_product_output_port="scb:::dp:::finance_db.daily_summary"
    ),
    usage=DataProductUsage(
        users=2500,
        systems=5,
        usecases=["Accounting", "Capital"]
    ),
    lifecycle=DataProductLifecycle(
        version="1.0",
        environment="Production",
        lifecycle_status=LifecycleStatusEnum.PUBLISH_CONSUME
    ),
    governance_metadata=DataProductGovernanceMetadata(
        domain="FM",
        sub_domain="FX",
        refresh_frequency="Daily (T+0)",
        data_product_owner="John Doe",
        data_steward="Alice Johnson",
        support_contact="Support Team",
        data_retention="3 years"
    )
)

create_data_product_from_model(atlas_client, dp)
# Auto-generated: scb:::dp:::finance_dp
```

---

## Enum Reference

### TableTypeEnum
```text
TableTypeEnum.MANAGED    # "Managed"
TableTypeEnum.EXTERNAL   # "External"
```

### PIIEnum
```text
PIIEnum.YES              # "True"
PIIEnum.NO               # "False"
```

### LifecycleStatusEnum
```text
LifecycleStatusEnum.IDEATE_PROPOSE         # "Ideate & Propose"
LifecycleStatusEnum.DEFINE_DESIGN          # "Define & Design"
LifecycleStatusEnum.DEVELOP_BUILD          # "Develop & Build"
LifecycleStatusEnum.VALIDATE_APPROVE       # "Validate & Approve"
LifecycleStatusEnum.PUBLISH_CONSUME        # "Publish & Consume"
LifecycleStatusEnum.MONITOR_MAINTAIN       # "Monitor & Maintain"
LifecycleStatusEnum.CHANGE_RETIRE          # "Change & Retire"
```

### SensitivityEnum
```text
SensitivityEnum.SENSITIVE_INTERNAL    # "Internal"
SensitivityEnum.SENSITIVE_EXTERNAL    # "External"
```

---

## Common Patterns

### Create Database → Table → Column Hierarchy
```text
# 1. Create database
db = DatabaseModel(database_name="finance_db", location_uri="hdfs://data/finance")
create_database_from_model(atlas_client, db)

# 2. Create table with parent relationship
table = TableModel(table_name="trades", database_name="finance_db")
create_table_from_model(atlas_client, table, db.qualified_name)

# 3. Create columns with parent relationship
for col_name, col_type in [("trade_id", "string"), ("amount", "decimal")]:
    col = ColumnModel(
        column_name=col_name,
        data_type=col_type,
        table_name="trades",
        database_name="finance_db"
    )
    create_column_from_model(atlas_client, col, table.qualified_name)
```

### Create Process with Input/Output
```text
process = ProcessModel(
    process_name="etl_job",
    query_id="etl_001",
    query_text="ETL SQL here"
)

create_process_from_model(
    atlas_client,
    process,
    input_refs=[
        ("SCB_Table", "scb:::dp:::db.source_table1"),
        ("SCB_Table", "scb:::dp:::db.source_table2"),
    ],
    output_refs=[
        ("SCB_Table", "scb:::dp:::db.output_table"),
    ]
)
```

### Create Data Product with Complete Metadata
```text
dp = CompleteDataProductModel(
    basic_metadata=DataProductBasicMetadata(
        data_product_name="My Data Product",
        description="Description here",
        data_product_category="Source-Aligned"
    ),
    governance_metadata=DataProductGovernanceMetadata(
        domain="FM",
        sub_domain="FX"
    )
)

create_data_product_from_model(
    atlas_client,
    dp,
    input_port_qualified_names=["scb:::dp:::db.input_table"],
    output_port_qualified_name="scb:::dp:::db.output_table"
)
```

---

## Validation Examples

### Catch Validation Errors
```text
from pydantic import ValidationError

try:
    # Missing required field
    db = DatabaseModel(location_uri="hdfs://data")
except ValidationError as e:
    print(f"Error: {e}")
    # database_name: field required

try:
    # Invalid type
    table = TableModel(table_name=123)  # Should be string
except ValidationError as e:
    print(f"Error: {e}")
    # table_name: input should be a valid string
```

---

## Model Properties

### All Models Support
```text
# Automatic qualified name generation
model.qualified_name  # Auto-generated string

# Conversion to Atlas entity format
entity = model.to_atlas_entity()  # Returns dict for Atlas API
```

---

## Service Functions

### Creation Functions
```text
create_database_from_model(atlas_client, model)
create_table_from_model(atlas_client, model, db_qualified_name)
create_column_from_model(atlas_client, model, table_qualified_name)
create_process_from_model(atlas_client, model, input_refs, output_refs)
create_data_product_from_model(atlas_client, model, input_ports, output_port)
```

---

## Import Statements

### Complete Imports for Common Use
```text
from datetime import datetime, timezone
from scb_atlas.atlas.metadata_models import (
    DatabaseModel,
    TableModel,
    ColumnModel,
    ProcessModel,
    CompleteDataProductModel,
    DataProductBasicMetadata,
    DataProductGovernanceMetadata,
    TableTypeEnum,
    PIIEnum,
    LifecycleStatusEnum,
)
from scb_atlas.atlas.service.entity_service import (
    create_database_from_model,
    create_table_from_model,
    create_column_from_model,
    create_process_from_model,
    create_data_product_from_model,
)
from scb_atlas.atlas.atlas_client import create_atlas_client
```

---

## Quick Troubleshooting

| Issue | Solution |
|-------|----------|
| Import error | Use `scb_atlas.atlas.entity_models`, not `atlas_models` |
| Validation error | Check field types and required fields |
| Missing qualified name | Use `model.qualified_name` (auto-generated) |
| Relationship not created | Pass parent's qualified name to creation function |
| Enum error | Use enum values (e.g., `TableTypeEnum.EXTERNAL`) |
| Relationship refs | Use tuples: `("SCB_Table", "scb:::dp:::path")` |

---

## Testing

### Run Tests
```bash
uv run pytest tests/unit/test_metadata_models.py -v
```

### Run Example
```bash
uv run python create_entities_with_pydantic.py
```

---

## Documentation Links

- **Usage Guide**: `PYDANTIC_MODELS_GUIDE.md`
- **Migration Guide**: `MIGRATION_GUIDE.md`
- **Complete Index**: `PYDANTIC_MODELS_INDEX.md`
- **Summary**: `PYDANTIC_INTEGRATION_SUMMARY.md`
- **Example Code**: `create_entities_with_pydantic.py`

---

## Key Takeaways

✅ Use Pydantic models for type-safe entity creation  
✅ Access `model.qualified_name` for relationships  
✅ Use enums for standardized values  
✅ Call `*_from_model()` functions to create in Atlas  
✅ Pass parent qualified name for relationships  
✅ Validation happens automatically at model creation  

---

**Last Updated**: March 2026  
**Status**: ✅ Production Ready

