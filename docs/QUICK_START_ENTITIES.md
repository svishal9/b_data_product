# SCB Atlas Entity Types - Quick Reference Guide

## What Was Added

Four new entity types have been successfully added to the SCB Atlas framework:

### 1. **SCB_Database**
- Represents databases or data storage systems
- Extends: `DataSet`
- Key attributes: `database_name`, `locationUri`, `createTime`, `description`

### 2. **SCB_Table**  
- Represents tables within databases
- Extends: `DataSet`
- Key attributes: `table_name`, `tableType`, `temporary`, `serde1`, `serde2`, `description`

### 3. **SCB_Column**
- Represents columns within tables
- Extends: `DataSet`
- Key attributes: `column_name`, `dataType`, `comment`, `position`

### 4. **SCB_Process**
- Represents data processing and transformation processes
- Extends: `Process`
- Key attributes: `process_name`, `queryId`, `queryText`, `userName`, `startTime`, `endTime`

## How to Use

### Method 1: Using Builders (Fluent API)
```text
from scb_atlas.atlas.atlas_client import create_atlas_client
from scb_atlas.atlas.entity_builders import DatabaseEntityBuilder

atlas_client = create_atlas_client()

# Create database
builder = DatabaseEntityBuilder("my_database", "hdfs://data/my_database")
builder.set_description("My database description")
entity = builder.build()
```

### Method 2: Using Service Functions (Direct)
```text
from scb_atlas.atlas.entity_service import create_database_entity

create_database_entity(
    atlas_client,
    database_name="my_database",
    location_uri="hdfs://data/my_database",
    description="My database description"
)
```

## Files Added

1. **scb_atlas/atlas/entity_builders.py** - Entity builder classes
   - `DatabaseEntityBuilder`
   - `TableEntityBuilder`
   - `ColumnEntityBuilder`
   - `ProcessEntityBuilder`

2. **scb_example_entities.py** - Complete working example
   - Shows full end-to-end workflow
   - Creates database → tables → columns → processes
   - Ready to run: `uv run scb_example_entities.py`

3. **ENTITY_TYPES.md** - Full API documentation
   - Detailed specifications for each entity type
   - Usage examples for all builders
   - Best practices and naming conventions
   - Troubleshooting guide

## Files Modified

1. **scb_atlas/atlas/atlas_types.py**
   - Added 4 entity type definitions
   - Updated `type_definitions` to include all new types

2. **scb_atlas/atlas/entity_service.py**
   - Added 4 new creation functions
   - All functions support optional parameters
   - Full error handling and logging

## Getting Started

### Step 1: Create All Types in Atlas
```bash
uv run scb_types.py type-create
```

### Step 2: Run the Example
```bash
uv run scb_example_entities.py
```

### Step 3: View in Atlas UI
Navigate to `http://localhost:23000` and search for your created entities.

## Example Workflow

```text
from scb_atlas.atlas.atlas_client import create_atlas_client
from scb_atlas.atlas.entity_service import (
    create_database_entity,
    create_table_entity,
    create_column_entity,
    create_process_entity_advanced
)

atlas_client = create_atlas_client()

# Create database
create_database_entity(
    atlas_client,
    database_name="finance_db",
    location_uri="hdfs://data/finance",
    description="Finance database"
)

# Create table
create_table_entity(
    atlas_client,
    table_name="trades",
    database_name="finance_db",
    table_type="EXTERNAL",
    description="Trading transactions"
)

# Create columns
create_column_entity(
    atlas_client,
    column_name="trade_id",
    data_type="string",
    table_name="finance_db.trades",
    comment="Unique trade identifier",
    position=1
)

# Create process
create_process_entity_advanced(
    atlas_client,
    process_name="daily_trades_aggregation",
    query_id="trades_agg_001",
    query_text="SELECT * FROM trades WHERE date = CURRENT_DATE",
    user_name="etl_user"
)
```

## Data Lineage

Create lineage between processes and tables:

```text
from scb_atlas.atlas.entity_builders import ProcessEntityBuilder

builder = ProcessEntityBuilder("etl_job", "job_001", "SELECT * FROM source")
builder.add_input_entity("SCB_Table", "scb:::dp:::source_db.source_table")
builder.add_output_entity("SCB_DataProduct", "scb:::dp:::output_product")
entity = builder.build()
```

## Key Features

✓ Type-safe with Python type hints
✓ Fluent builder pattern for ease of use
✓ Service functions for quick creation
✓ Automatic qualified name generation
✓ Full error handling and logging
✓ Seamless integration with DataProducts
✓ Complete documentation and examples

## Troubleshooting

**Error: Type not found**
→ Run: `uv run scb_types.py type-create`

**Error: Unique constraint violation**
→ Entity already exists; create with same unique attribute to update

**Missing qualified names**
→ Use builders or service functions; they auto-generate qualified names

## Documentation

- **ENTITY_TYPES.md** - Complete API reference and usage guide
- **IMPLEMENTATION_SUMMARY.md** - Technical implementation details
- **scb_example_entities.py** - Working code example

## Integration with Data Products

The new entity types fully integrate with existing `SCB_DataProduct`:

```text
# Create infrastructure
create_database_entity(atlas_client, "raw_db", "hdfs://raw")
create_table_entity(atlas_client, "raw_data", "raw_db")

# Create data product from infrastructure
data_product = AtlasDPModel(
    name="Processed Dataset",
    owner="data_team",
    source_systems=["raw_db"]
)
create_data_product_entity(atlas_client, data_product)
```

## Summary

You now have a complete system for:
- Creating and managing databases, tables, and columns
- Building data transformation processes
- Tracking data lineage from source to product
- Integrating with existing data product management
- Full governance and metadata capabilities

Start with `scb_example_entities.py` to see it in action!

