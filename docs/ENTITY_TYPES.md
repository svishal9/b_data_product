# SCB Atlas Entity Types Documentation

## Overview

This document describes the new entity types added to the SCB Atlas framework for managing data catalogs. In addition to the existing `SCB_DataProduct` entity type, the framework now supports:

- **SCB_Database**: Represents a database or data storage system
- **SCB_Table**: Represents a table within a database
- **SCB_Column**: Represents a column within a table
- **SCB_Process**: Represents a data processing or transformation process

These entities enable building a complete data lineage and governance model, showing how data flows from source systems through transformations to data products.

## Entity Type Definitions

### SCB_Database

Represents a database or data storage system in your data landscape.

**Super Type**: `DataSet`

**Attributes**:

| Attribute | Type | Required | Unique | Indexable | Description |
|-----------|------|----------|--------|-----------|-------------|
| database_name | string | Yes | Yes | Yes | Name of the database |
| locationUri | string | Yes | No | Yes | URI location of the database |
| createTime | date | Yes | No | Yes | Date the database was created |
| description | string | No | No | No | Database description |

**Example**:
```text
from scb_atlas.atlas.entity_builders import DatabaseEntityBuilder

builder = DatabaseEntityBuilder("fin_trades_db", "hdfs://data/finance/trades")
builder.set_description("Finance trades database")
entity = builder.build()
```

### SCB_Table

Represents a table within a database or data storage system.

**Super Type**: `DataSet`

**Attributes**:

| Attribute | Type | Required | Unique | Indexable | Description |
|-----------|------|----------|--------|-----------|-------------|
| table_name | string | Yes | Yes | Yes | Name of the table |
| createTime | date | No | No | Yes | Date the table was created |
| tableType | string | No | No | Yes | Type of table (EXTERNAL, MANAGED, etc.) |
| temporary | boolean | No | No | No | Whether the table is temporary |
| serde1 | string | No | No | No | SerDe (serialization/deserialization) information |
| serde2 | string | No | No | No | Additional SerDe information |
| description | string | No | No | No | Table description |

**Example**:
```text
from scb_atlas.atlas.entity_builders import TableEntityBuilder

builder = TableEntityBuilder("fx_trades", "fin_trades_db")
builder.set_table_type("EXTERNAL")
builder.set_description("Contains FX trading transactions")
entity = builder.build()
```

### SCB_Column

Represents a column within a table.

**Super Type**: `DataSet`

**Attributes**:

| Attribute | Type | Required | Unique | Indexable | Description |
|-----------|------|----------|--------|-----------|-------------|
| column_name | string | Yes | Yes | Yes | Name of the column |
| dataType | string | No | No | Yes | Data type of the column |
| comment | string | No | No | Yes | Column comment or description |
| position | int | No | No | No | Position of column in table |

**Example**:
```text
from scb_atlas.atlas.entity_builders import ColumnEntityBuilder

builder = ColumnEntityBuilder("trade_id", "string", "fin_trades_db.fx_trades")
builder.set_comment("Unique identifier for the trade")
builder.set_position(1)
entity = builder.build()
```

### SCB_Process

Represents a data processing or transformation process that produces output from input data.

**Super Type**: `Process`

**Attributes**:

| Attribute | Type | Required | Unique | Indexable | Description |
|-----------|------|----------|--------|-----------|-------------|
| process_name | string | Yes | Yes | Yes | Name of the process |
| queryId | string | Yes | Yes | Yes | Unique identifier for the query/process |
| queryText | string | Yes | No | Yes | The query or transformation logic text |
| userName | string | No | No | Yes | Name of user who ran the process |
| startTime | long | No | No | Yes | Start time (Unix timestamp in milliseconds) |
| endTime | long | No | No | Yes | End time (Unix timestamp in milliseconds) |

**Example**:
```text
from scb_atlas.atlas.entity_builders import ProcessEntityBuilder

builder = ProcessEntityBuilder(
    "fx_trades_aggregation_daily",
    "proc_fx_agg_001",
    "SELECT trade_date, SUM(amount) FROM fx_trades GROUP BY trade_date"
)
builder.set_user_name("data_pipeline")
builder.set_start_time(1708953600000)
builder.set_end_time(1708957200000)
entity = builder.build()
```

## Creating Entities

### Using Entity Builders

The builder pattern provides a fluent API for creating entities:

```text
from scb_atlas.atlas.atlas_client import create_atlas_client
from scb_atlas.atlas.entity_builders import (
    DatabaseEntityBuilder,
    TableEntityBuilder,
    ColumnEntityBuilder,
    ProcessEntityBuilder
)

# Initialize client
atlas_client = create_atlas_client()

# Create database
db_builder = DatabaseEntityBuilder("my_db", "hdfs://data/my_db")
db_builder.set_description("My database")
db_entity = db_builder.build()

# Create table
table_builder = TableEntityBuilder("my_table", "my_db")
table_builder.set_table_type("EXTERNAL")
table_entity = table_builder.build()

# Create column
col_builder = ColumnEntityBuilder("id", "bigint", "my_db.my_table")
col_builder.set_comment("Primary key")
col_builder.set_position(1)
col_entity = col_builder.build()

# Create process
process_builder = ProcessEntityBuilder(
    "my_process",
    "query_001",
    "SELECT * FROM my_table WHERE id > 100"
)
process_builder.set_user_name("etl_user")
process_entity = process_builder.build()
```

### Using Service Functions

Direct service functions are available for convenience:

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
    database_name="my_db",
    location_uri="hdfs://data/my_db",
    description="My database"
)

# Create table
create_table_entity(
    atlas_client,
    table_name="my_table",
    database_name="my_db",
    table_type="EXTERNAL",
    description="My table"
)

# Create column
create_column_entity(
    atlas_client,
    column_name="id",
    data_type="bigint",
    table_name="my_db.my_table",
    comment="Primary key",
    position=1
)

# Create process
create_process_entity_advanced(
    atlas_client,
    process_name="my_process",
    query_id="query_001",
    query_text="SELECT * FROM my_table",
    user_name="etl_user",
    start_time=1708953600000,
    end_time=1708957200000
)
```

## Data Lineage and Relationships

Processes can link input and output entities to represent data lineage:

```text
from scb_atlas.atlas.entity_builders import ProcessEntityBuilder

builder = ProcessEntityBuilder(
    "daily_aggregation",
    "agg_001",
    "SELECT date, SUM(amount) FROM transactions GROUP BY date"
)

# Add input (source table)
builder.add_input_entity(
    "SCB_Table",
    "scb:table:source_db.transactions"
)

# Add output (data product)
builder.add_output_entity(
    "SCB_DataProduct",
    "scb:dataproduct:daily_transactions_summary"
)

entity = builder.build()
```

## Type Registration

All entity types are automatically registered in Atlas when you run the type creation command:

```bash
# Create all types including database, table, column, and process
uv run scb_types.py type-create
```

The type definitions are located in: `scb_atlas/atlas/atlas_types.py`

## Complete Example

See `scb_example_entities.py` for a comprehensive example that demonstrates:

1. Creating a database with multiple tables
2. Creating columns for each table
3. Creating processes that link tables to data products
4. Building a complete data lineage

Run the example:
```bash
uv run scb_example_entities.py
```

## Best Practices

### Naming Conventions

- **Database Names**: Use lowercase with underscores (e.g., `fin_trades_db`)
- **Table Names**: Use lowercase with underscores (e.g., `fx_trades`)
- **Column Names**: Use lowercase with underscores (e.g., `trade_date`)
- **Process Names**: Use descriptive names with process type and frequency (e.g., `fx_trades_aggregation_daily`)
- **Query IDs**: Use unique identifiers (e.g., `proc_fx_agg_001`)

### Qualified Names

All entities use qualified names for uniqueness. The `prepare_qualified_name()` utility generates qualified names:

```text
from scb_atlas.atlas.atlas_type_def import prepare_qualified_name

qn = prepare_qualified_name("my_database")
# Returns: "scb:database:my_database"
```

### Relationships

To establish parent-child relationships:

1. **Database → Table**: Include database name when creating tables
2. **Table → Column**: Include table name when creating columns
3. **Process → Entities**: Add input/output references for lineage

### Unique Attributes

These attributes are marked as unique and must be unique within their scope:

- `database_name` (globally unique)
- `table_name` (unique per database)
- `column_name` (unique per table)
- `process_name` (globally unique)
- `queryId` (globally unique)

## API Reference

### DatabaseEntityBuilder

```text
builder = DatabaseEntityBuilder(database_name, location_uri)
builder.set_description(description) -> DatabaseEntityBuilder
builder.build() -> dict
```

### TableEntityBuilder

```text
builder = TableEntityBuilder(table_name, database_name=None)
builder.set_table_type(table_type) -> TableEntityBuilder
builder.set_temporary(temporary) -> TableEntityBuilder
builder.set_serde(serde1, serde2=None) -> TableEntityBuilder
builder.set_description(description) -> TableEntityBuilder
builder.set_create_time(create_time) -> TableEntityBuilder
builder.build() -> dict
```

### ColumnEntityBuilder

```text
builder = ColumnEntityBuilder(column_name, data_type, table_name=None)
builder.set_comment(comment) -> ColumnEntityBuilder
builder.set_position(position) -> ColumnEntityBuilder
builder.build() -> dict
```

### ProcessEntityBuilder

```text
builder = ProcessEntityBuilder(process_name, query_id, query_text)
builder.set_user_name(user_name) -> ProcessEntityBuilder
builder.set_start_time(start_time) -> ProcessEntityBuilder
builder.set_end_time(end_time) -> ProcessEntityBuilder
builder.add_input_entity(type_name, qualified_name) -> ProcessEntityBuilder
builder.add_output_entity(type_name, qualified_name) -> ProcessEntityBuilder
builder.build() -> dict
```

## Troubleshooting

### Type Not Found Error

If you see "Type X not found", ensure all types are created:
```bash
uv run scb_types.py type-create
```

### Unique Constraint Violation

If you get a unique constraint error, the entity already exists. To update it, create a new entity with the same unique attribute (Atlas will merge).

### Missing Qualified Names

Ensure `qualifiedName` attribute is set for all entities. Use the `prepare_qualified_name()` utility:

```text
from scb_atlas.atlas.atlas_type_def import prepare_qualified_name
qualified_name = prepare_qualified_name("entity_name")
```

## Related Documentation

- Main CLAUDE.md: Project overview and architecture
- `atlas_types.py`: Type definitions source
- `entity_service.py`: Entity CRUD operations
- `entity_builders.py`: Entity builder implementations

