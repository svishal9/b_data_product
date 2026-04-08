# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This project provides a flexible Python framework for interacting with Apache Atlas service to create and manage data catalogs. It supports two approaches:

1. **JSON-driven approach** (primary): Create custom types and entities from Python dictionary configurations
2. **Excel-based approach** (legacy): Ingest metadata from Excel file for backward compatibility

The system allows creating any custom type in Atlas, not limited to DataProducts, with complete CRUD operations for entities and comprehensive type management capabilities.

## Development Commands

### Dependencies
- Uses `uv` for dependency management (see `pyproject.toml` and `uv.lock`)
- Install dependencies: `uv sync`

### Atlas Connection
- Default Atlas URL: `http://localhost:23000` (configured in `scb_atlas/atlas/constants.py`)
- Default credentials: `admin/admin` (hardcoded in scripts, can be updated)

### JSON-driven Commands (Primary Approach)

#### Type and ENUM Creation
- Create DataProduct type and all ENUMS: `uv run scb_dp_type.py dp_create`
- Create ENUMs only: `uv run scb_dp_type.py enums_create`
- Delete a type: `uv run scb_dp_type.py dp_delete <enum_name>`
- Delete an ENUM: `uv run scb_enums.py enums_delete <enum_name>`

#### Entity Operations
- Create an entity: `uv run scb_dp_entity.py entity_create`
- Update an entity: `uv run scb_dp_entity.py entity_update`
- Delete an entity by GUID: `uv run scb_dp_entity.py entity_delete <guid>`

### Excel-based Commands (Legacy Approach)
- Main entry point: `ingest_metadata.py`
- Run with: `uv run ingest_metadata.py`
- Default Excel file: `atlas_metadata_simple.xlsx` (configured in script)

## Architecture

### Atlas Integration
The code interacts with Apache Atlas to:
1. **Create custom types**: Define new types and ENUMs from Python dictionary configurations
2. **Manage entities**: Create, update, and delete entities in Atlas
3. **Type management**: Create and delete types/ENUMs dynamically
4. **Lineage relationships**: Support for tracking data lineage between sources and products

### Type Definition System
Types and ENUMs are defined in Python dictionaries within the main scripts. This provides:
- Human-readable configuration
- Easy modification without JSON parsing
- Type coercion support for converting input data
- Complete flexibility to define any custom type

### Entity Creation
Entities reference Atlas types and are created with attributes following specific naming conventions. The system supports:
- Automatic type creation (when creating entities)
- Qualified name management
- Lineage tracking through relationships
- Attribute coercion for different data types

## Key Files

### Atlas Integration Files
- **scb_atlas/atlas/constants.py**: Atlas URL configuration
- **scb_atlas/atlas/atlas_client.py**: Atlas client initialization
- **scb_atlas/atlas/type_service.py**: Type and ENUM creation and deletion
- **scb_atlas/atlas/entity_service.py**: Entity CRUD operations
- **scb_atlas/__init__.py**: Package initialization

### Type Definition Files
- **scb_dp_type.py**: Type and ENUM definitions for DataProduct in Python dictionary format
  - `dp_create()`: Creates DataProduct type and all ENUMs from Python dict
  - `enums_create()`: Creates ENUM definitions only
- **scb_enums.py**: Separate ENUM definitions (can be used independently)

### Entity Definition Files
- **scb_dp_entity.py**: Entity operations
  - `entity_create()`: Creates a DataProduct entity
  - `entity_update()`: Updates an entity
  - `entity_delete()`: Deletes an entity by GUID

### Legacy Files
- **ingest_metadata.py**: Excel-based metadata ingestion (legacy approach)
- **pyproject.toml**: Project configuration with Apache Atlas SDK dependency
- **atlas_metadata_simple.xlsx**: Excel template with Data Product catalog metadata

## Type Definition Structure

Types are defined as Python dictionaries with two main components:

### ENTITY Definitions
```text
{
    "entityDefs": [
        {
            "name": "SCB_DataProduct",
            "qualifiedName": "SCB_DataProduct",
            "DisplayName": "SCB Data Product",
            "superTypes": ["DataSet"],
            "category": "ENTITY",
            "typeVersion": "1.0",
            "attributeDefs": [
                {
                    "name": "Data Product Name",
                    "typeName": "string",
                    "cardinality": "SINGLE",
                    "isOptional": False,
                    "isUnique": True,
                    "isIndexable": True
                }
            ]
        }
    ]
}
```

**Attribute Definition Properties:**
- `name`: Attribute name (use spaces, e.g., "Data Product Name")
- `typeName`: Data type (e.g., "string", "array<string>", "SCB_Domain")
- `cardinality`: "SINGLE" for scalar, "LIST" for arrays
- `isOptional`: Boolean for required/optional fields
- `isUnique`: Boolean for unique constraint
- `isIndexable`: Boolean for index creation

### ENUM Definitions
```text
{
    "enumDefs": [
        {
            "name": "SCB_Domain",
            "description": "Domain of the data product",
            "category": "ENUM",
            "typeVersion": "1.0",
            "elementDefs": [
                {"value": "FM", "ordinal": 1},
                {"value": "IT", "ordinal": 2}
            ]
        }
    ]
}
```

**ENUM Element Properties:**
- `value`: Enum element value
- `ordinal`: Element order (ascending)

### Type Reference in Attributes
ENUMs are referenced in attribute definitions using their qualified name:
```text
{"name": "Domain", "typeName": "SCB_Domain", "cardinality": "SINGLE", ...}
```

## Entity Creation Structure

Entities are defined with a nested structure:

`{"entity": {"typeName": "SCB_DataProduct", "attributes": {...}}}`

**Entity Properties:**
- `typeName`: Type definition name (must exist in Atlas)
- `attributes`: Object with all attribute values using space-separated names (e.g., "Data Product Name")

## Excel Template Structure (Legacy)

The Excel file (`atlas_metadata_simple.xlsx`) provides a legacy approach for metadata ingestion:

**Required Columns:**
- Data Product Name
- Source System (comma-separated)
- Description
- Documentation URL
- Domain
- Business Owner
- Technical Owner
- Last Updated

**Note:** This legacy approach creates specific entity types (DataSet, DataProduct, Process) with predefined naming conventions and is maintained for backward compatibility.

## Atlas Configuration

The project connects to Apache Atlas with the following configuration:

- **URL**: `http://localhost:23000` (see `scb_atlas/atlas/constants.py`)
- **Authentication**: Username/password (currently hardcoded as `admin/admin`)
- **Client Setup**: All scripts use `create_atlas_client()` from `scb_atlas.atlas`

**Authentication Consideration:**
For production use, credentials should be moved to environment variables or configuration files rather than hardcoded.

## Extending the Framework

### Adding New Types
1. Define type and ENUMs in a Python dictionary in a new or existing script
2. Use the existing `create_typedef()` function to create the type
3. Follow the structure in `scb_dp_type.py` and `scb_enums.py`

### Creating New Entities
1. Define entity structure in a Python dictionary following the format in `scb_dp_entity.py`
2. Ensure the `typeName` matches an existing type in Atlas
3. Use `create_entity()` to create the entity
4. Attribute names should use spaces (e.g., "Data Product Name")

### Working with ENUMs
ENUM definitions follow a similar structure to types but are marked as `category: "ENUM"` with `elementDefs` instead of `attributeDefs`. When creating entities that reference ENUMs, use the ENUM's qualified name as the `typeName` for those attributes.