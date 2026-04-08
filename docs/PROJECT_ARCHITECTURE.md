# SCB Data Product - Project Architecture

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Project Structure](#project-structure)
4. [Core Components](#core-components)
5. [Data Flow](#data-flow)
6. [Design Patterns](#design-patterns)
7. [Technology Stack](#technology-stack)
8. [Integration Points](#integration-points)
9. [Extensibility](#extensibility)

---

## Overview

**SCB Data Product** is a Python framework for interacting with Apache Atlas to create, manage, and track data catalogs. It provides a flexible, type-safe approach to metadata management with support for:

- **Custom Type Definitions**: Create any entity type in Atlas dynamically
- **Entity Management**: Full CRUD operations for catalog entities
- **Data Lineage**: Track relationships between data sources, processes, and products
- **Multiple Interfaces**: JSON-driven, Excel-based, and Python API approaches
- **Governance**: Classifications, tags, and lifecycle management

---

## System Architecture

### High-Level Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                    Client Applications                       │
│  (scb_dp.py, scb_types.py, scb_enums.py, etc.)             │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│            Service Layer (scb_atlas/atlas/service/)         │
│  ┌─────────────────┬──────────────────┬──────────────────┐  │
│  │ entity_service  │ type_service     │ discovery_service│  │
│  │ (CRUD)          │ (Type creation)  │ (DSL Search)     │  │
│  └─────────────────┴──────────────────┴──────────────────┘  │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│        Entity & Type Definition Layer                        │
│  ┌──────────────┬──────────────┬──────────────────────────┐ │
│  │   Builders   │ Type Defs    │   Metadata Models        │ │
│  │ (Fluent API) │ (Pydantic)   │   (Pydantic Models)      │ │
│  └──────────────┴──────────────┴──────────────────────────┘ │
│  ┌──────────────┬──────────────────────────────────────────┐ │
│  │ atlas_type_def/ (Type configurations)                  │ │
│  │ - scb_entity.py (Entity types)                         │ │
│  │ - scb_enums.py (ENUM definitions)                      │ │
│  │ - scb_structs.py (Struct types)                        │ │
│  └──────────────┬──────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│              Atlas Client Layer                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │  apache-atlas SDK (Base client)                        │ │
│  │  - Entity API                                          │ │
│  │  - Type API                                            │ │
│  │  - Search API                                          │ │
│  └────────────────────────────────────────────────────────┘ │
└──────────────────┬──────────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────────┐
│          Apache Atlas Service (Docker Container)            │
│  - Port: 23000                                              │
│  - Authentication: admin/admin (default)                    │
│  - REST API endpoints                                       │
└──────────────────────────────────────────────────────────────┘
```

---

## Project Structure

```
scb-data-product/
├── scb_atlas/                          # Main package
│   ├── __init__.py                     # Package exports
│   └── atlas/                          # Atlas integration module
│       ├── __init__.py                 # Service exports
│       ├── atlas_client.py             # Client factory & connection
│       ├── atlas_settings.py           # Configuration (URL, auth)
│       ├── constants.py                # Constants (categories, labels)
│       ├── entity_builders.py          # Builder classes (Fluent API)
│       ├── entity_models.py            # Backward-compatible imports
│       ├── exceptions.py               # Custom exceptions
│       ├── read_data_product.py        # Data product reader utility
│       │
│       ├── service/                    # Service layer
│       │   ├── __init__.py            # Service exports
│       │   ├── entity_service.py      # Entity CRUD operations
│       │   ├── type_service.py        # Type creation/deletion
│       │   └── discovery_service.py   # DSL search queries
│       │
│       ├── atlas_type_def/            # Type definitions package
│       │   ├── __init__.py            # Type definition exports
│       │   ├── base.py                # Base type category class
│       │   ├── scb_entity.py          # Entity type definitions
│       │   ├── scb_enums.py           # ENUM definitions
│       │   ├── scb_structs.py         # Struct type definitions
│       │   ├── scb_relationships.py   # Relationship definitions
│       │   ├── scb_classifications.py # Classification definitions
│       │   └── utility.py             # Type utility functions
│       │
│       └── metadata_models/           # Pydantic models
│           ├── __init__.py            # Model exports
│           ├── data_product_model.py  # Data Product models
│           ├── database.py            # Database model
│           ├── table_model.py         # Table model
│           ├── column_model.py        # Column model
│           └── process_model.py       # Process model
│
├── tests/                              # Test suite
│   ├── conftest.py                    # Pytest configuration
│   ├── unit/                          # Unit tests
│   └── integration/                   # Integration tests
│       ├── test_entity_services.py
│       └── ...
│
├── scripts/                            # Shell scripts
│   ├── prepare_atlas.sh               # Setup types and enums
│   └── create_sample_data_products.sh # Create sample entities
│
├── Main CLI Scripts
│   ├── scb_types.py                   # Type management CLI
│   ├── scb_enums.py                   # ENUM management CLI
│   ├── scb_dp.py                      # Data Product management CLI
│   ├── scb_dp_search.py               # Search utility
│   └── ingest_workbook_to_atlas.py    # Excel ingestion
│
├── Configuration
│   ├── pyproject.toml                 # Project configuration & dependencies
│   ├── uv.lock                        # Lock file (uv package manager)
│   └── CLAUDE.md                      # Development guidance
│
├── Documentation
│   ├── README.md                      # Quick start guide
│   ├── ENTITY_TYPES.md                # Entity types reference
│   ├── QUICK_START_ENTITIES.md        # Quick start for entities
│   ├── PYDANTIC_MODELS_GUIDE.md       # Pydantic models guide
│   ├── WORKBOOK_FRAMEWORK_README.md   # Workbook framework
│   ├── PROJECT_ARCHITECTURE.md        # This file
│   └── ...
│
└── apache-atlas/                       # Docker compose setup
    ├── docker-compose.yml
    ├── Dockerfile
    ├── atlas-deployment.yaml
    ├── atlas-service.yaml
    └── ...
```

---

## Core Components

### 1. **Atlas Client Layer** (`atlas_client.py`)

**Purpose**: Manages connection to Apache Atlas

```text
create_atlas_client(username="admin", password="admin") -> AtlasClient
```

**Responsibilities**:
- Initialize Apache Atlas client with credentials
- Handle connection errors and authentication failures
- Provide singleton-like access to Atlas API

**Key Features**:
- Configuration from `atlas_settings.py`
- Error handling with custom `AtlasConnectionError`
- Logging for debugging

---

### 2. **Type Definition System** (`atlas_type_def/`)

**Purpose**: Define custom types and ENUMs that can be created in Atlas

#### Components:

**a) Base Classes** (`base.py`)
```text
class BaseEntityCategory:
    """Base class for defining entity types"""
    atlas_name: str
    display_name: str
    super_types: List[str]
    attributes: List[Dict]
```

**b) Entity Definitions** (`scb_entity.py`)
- `scb_database`: Database storage system
- `scb_table`: Table within a database
- `scb_column`: Column within a table
- `scb_process`: Data transformation process
- `scb_data_product`: Data product catalog entry
- `scb_source_aligned_data_product`: Source-aligned data product variant

**c) ENUM Definitions** (`scb_enums.py`)
- `SCB_DataProductCategory`: Source-Aligned, Intermediate, Consumer-Aligned
- `SCB_Domain`: Business domains
- `SCB_Granularity`: Data granularity levels
- `SCB_Lifecycle`: Status progression
- And more...

**d) Struct Types** (`scb_structs.py`)
- `SCB_BusinessInfo`: Business metadata structure
- `SCB_Flags`: Classification flags
- `SCB_DataAccess`: Data access rules
- And more...

**Key Pattern**: Python dictionaries define types, transformed to Atlas API format by `type_service`

---

### 3. **Service Layer** (`service/`)

#### 3.1 Entity Service (`entity_service.py`)

**Core Functions**:

| Function | Purpose |
|----------|---------|
| `create_database_entity()` | Create SCB_Database entity |
| `create_table_entity()` | Create SCB_Table entity |
| `create_column_entity()` | Create SCB_Column entity |
| `create_process_entity()` | Create SCB_Process entity |
| `create_data_product_entity()` | Create SCB_DataProduct entity |
| `delete_entity()` | Delete entity by GUID |
| `update_entity()` | Update existing entity |

**Pattern**: Each function takes Atlas client and model parameters, returns entity GUID

#### 3.2 Type Service (`type_service.py`)

**Functions**:
- `create_typedef()`: Register custom types in Atlas
- `delete_typedef()`: Remove custom types from Atlas
- `get_typedef()`: Retrieve type definition

**Workflow**:
1. Takes type definitions from `atlas_type_def`
2. Validates with Apache Atlas SDK
3. Creates/updates types via REST API

#### 3.3 Discovery Service (`discovery_service.py`)

**Functions**:
- `dsl_search()`: Execute DSL queries to find entities
- Search by type, attribute values
- Support filtering and sorting

---

### 4. **Entity Builders** (`entity_builders.py`)

**Pattern**: Fluent API for constructing entities

**Classes**:
- `DatabaseEntityBuilder`
- `TableEntityBuilder`
- `ColumnEntityBuilder`
- `ProcessEntityBuilder`

**Example Usage**:
```text
builder = DatabaseEntityBuilder("my_db", "hdfs://data")
builder.set_description("My database")
builder.add_owner("john.doe@scb.com")
entity = builder.build()  # Returns dict ready for Atlas
```

**Benefits**:
- Type-safe construction
- Optional parameters with defaults
- Method chaining
- Automatic qualified name generation

---

### 5. **Metadata Models** (`metadata_models/`)

**Technology**: Pydantic v2 for data validation

#### 5.1 Data Product Model (`data_product_model.py`)

**Classes**:
- `DataProductBasicMetadata`: Name, description, category
- `DataProductBusinessMetadata`: Owner, purpose
- `DataProductClassification`: Sensitivity, PII flags
- `DataProductPorts`: Input/output specifications
- `DataProductSchemaField`: Schema field definitions
- `DataProductUsage`: Adoption/usage tracking
- `DataProductGovernanceMetadata`: Compliance, approvals
- `CompleteDataProductModel`: Composite model (all the above)

**Features**:
- Automatic validation on instantiation
- Type coercion
- Field descriptions
- Optional/required field handling
- Computed properties with `@computed_field`

#### 5.2 Infrastructure Models
- `DatabaseModel`: Database structure
- `TableModel`: Table definitions with lineage
- `ColumnModel`: Column with data types
- `ProcessModel`: Transformation process definitions

---

### 6. **Exceptions** (`exceptions.py`)

**Custom Exceptions**:
- `AtlasConnectionError`: Connection failures
- `AtlasAuthenticationError`: Auth failures
- `EntityCreationError`: Entity creation failures
- `EntityDeletionError`: Entity deletion failures
- `TypeDefinitionError`: Type validation errors

---

## Data Flow

### 1. **Type Creation Flow**

```
Type Definitions (Python Dict)
    ↓
Type Service (Validation & API call)
    ↓
Apache Atlas REST API (/types)
    ↓
Atlas Service (Persists type metadata)
    ↓
Available for entity creation
```

**Example**:
```text
from scb_atlas.atlas import create_atlas_client, create_typedef
from scb_atlas.atlas.atlas_type_def import all_types

client = create_atlas_client()
create_typedef(all_types, client)  # Creates all types
```

---

### 2. **Entity Creation Flow**

```
Python Code / User Input
    ↓
Pydantic Model (Validation)
    ↓
Entity Builder (Optional - Fluent API)
    ↓
Service Function (entity_service)
    ↓
Atlas Client (API call)
    ↓
Apache Atlas REST API (/entities)
    ↓
Atlas Service (Persists entity)
    ↓
Returns GUID
```

**Example**:
```text
from scb_atlas.atlas import create_atlas_client, create_database_entity
from scb_atlas.atlas.metadata_models import DatabaseModel

client = create_atlas_client()

# Method 1: Direct service call
guid = create_database_entity(
    client,
    database_name="my_db",
    location_uri="hdfs://data",
    description="My database"
)

# Method 2: Using model + builder
model = DatabaseModel(
    database_name="my_db",
    location_uri="hdfs://data",
    description="My database"
)
guid = create_database_entity(client, **model.dict())
```

---

### 3. **Entity Search Flow**

```
DSL Query (Python code)
    ↓
Discovery Service (Query construction)
    ↓
Apache Atlas DSL API (/search/dsl)
    ↓
Atlas Service (Executes query)
    ↓
Returns matching entities with attributes
```

---

### 4. **Data Lineage Flow**

```
Source Entity (Table/Database)
    ↓
Process Entity (Transformation)
    ↓
Output Entity (Table/DataProduct)
    ↓
Stored as relationships in Atlas
    ↓
Visible in Data Lineage UI
```

---

## Design Patterns

### 1. **Builder Pattern**
- **Where**: `entity_builders.py`
- **Why**: Fluent API for complex object construction
- **Benefit**: Type-safe, readable, chainable

### 2. **Facade Pattern**
- **Where**: `service/` (service layer)
- **Why**: Simplifies Atlas API interactions
- **Benefit**: Hide complexity of Atlas REST calls

### 3. **Repository Pattern**
- **Where**: `discovery_service.py`
- **Why**: Abstracts data retrieval logic
- **Benefit**: Single source for queries, reusability

### 4. **Validation Pattern**
- **Where**: `metadata_models/` (Pydantic)
- **Why**: Ensure data integrity before sending to Atlas
- **Benefit**: Type safety, early error detection

### 5. **Configuration Pattern**
- **Where**: `atlas_settings.py`
- **Why**: Environment-based configuration
- **Benefit**: Easy deployment across environments

### 6. **Factory Pattern**
- **Where**: `atlas_client.py` (`create_atlas_client()`)
- **Why**: Centralized client creation
- **Benefit**: Consistent initialization, easy mocking for tests

---

## Technology Stack

### Core Dependencies

| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Atlas Integration** | apache-atlas | >=0.0.16 | Apache Atlas Python SDK |
| **CLI Framework** | typer | >=0.24.0 | Command-line interface creation |
| **Data Validation** | pydantic | >=2.12.5 | Data model validation |
| **Data Processing** | pandas | >=3.0.1 | Excel file handling |
| **Excel Support** | openpyxl | >=3.1.5 | Excel file I/O |
| **Testing** | pytest | >=9.0.2 | Unit & integration tests |
| **Package Manager** | uv | - | Fast Python package manager |

### Python Version
- **Required**: Python >=3.13
- **Target**: Modern Python with type hints support

### External Services
- **Apache Atlas**: REST API service
- **Docker**: Container runtime for Atlas

---

## Integration Points

### 1. **Apache Atlas REST API**

**Endpoints Used**:
- `POST /api/atlas/v2/types/typedefs` - Create types
- `DELETE /api/atlas/v2/types/typedef/name/{name}` - Delete types
- `POST /api/atlas/v2/entity` - Create entities
- `PUT /api/atlas/v2/entity` - Update entities
- `DELETE /api/atlas/v2/entity/guid/{guid}` - Delete entities
- `POST /api/atlas/v2/search/dsl` - DSL search

**Authentication**: Basic Auth (username/password)

---

### 2. **Excel Integration**

**Components**:
- `ingest_workbook_to_atlas.py` - Main ingestion script
- Uses `openpyxl` and `pandas` for parsing

**Workflow**:
```
Excel File
    ↓
pandas.read_excel()
    ↓
Data transformation
    ↓
Pydantic model validation
    ↓
Entity creation via service
    ↓
Result summary
```

---

### 3. **CLI Entry Points**

**Scripts**:
- `scb_types.py` - Type management (`type-create`, `type-delete`, `type-clean`)
- `scb_enums.py` - ENUM management
- `scb_dp.py` - Data product operations
- `scb_dp_search.py` - Search utilities

**Framework**: Typer (built on Click)

---

## Extensibility

### 1. **Adding New Entity Types**

**Steps**:
1. Define type in `atlas_type_def/scb_entity.py`:
```text
my_custom_entity = BaseEntityCategory(
    atlas_name="SCB_MyCustomType",
    display_name="My Custom Type",
    super_types=["DataSet"],
    attributes=[
        {"name": "attr1", "typeName": "string", ...},
        {"name": "attr2", "typeName": "int", ...}
    ]
)
```

2. Add to entity exports in `atlas_type_def/__init__.py`

3. Create Pydantic model in `metadata_models/`:
```text
class MyCustomModel(BaseModel):
    attr1: str
    attr2: int
```

4. Create builder in `entity_builders.py`:
```text
class MyCustomBuilder:
    def __init__(self, attr1: str, attr2: int):
        ...
    def build(self) -> dict:
        ...
```

5. Create service function in `service/entity_service.py`:
```text
def create_my_custom_entity(client, **kwargs):
    ...
```

---

### 2. **Adding New ENUMs**

**Steps**:
1. Define in `atlas_type_def/scb_enums.py`:
```text
my_enum = {
    "name": "SCB_MyEnum",
    "description": "My custom enum",
    "elementDefs": [
        {"value": "OPTION_1", "ordinal": 1},
        {"value": "OPTION_2", "ordinal": 2}
    ]
}
```

2. Add to exports and `all_enums` list

---

### 3. **Adding New Services**

**Steps**:
1. Create new file in `service/`:
```text
# service/my_service.py
def my_operation(client: AtlasClient, **kwargs):
    ...
```

2. Export from `service/__init__.py`

3. Import and use in CLI scripts

---

### 4. **Custom Search Queries**

**Extend** `discovery_service.py`:
```text
def search_by_custom_criteria(client, criteria):
    # Build DSL query
    query = {
        "query": {
            "match": {...}
        }
    }
    response = dsl_search(client, query)
    return response
```

---

## Testing Architecture

### Test Structure

```
tests/
├── conftest.py                 # Shared fixtures
├── unit/                       # Unit tests
│   └── ...
└── integration/                # Integration tests
    ├── conftest.py            # Integration fixtures (Atlas connection)
    ├── test_entity_services.py
    └── ...
```

### Test Patterns

**Unit Tests**:
- Mock Atlas client
- Test builders, models, utilities
- No Atlas connection required

**Integration Tests**:
- Real Atlas connection (Docker container)
- End-to-end workflows
- Type creation → entity creation → search → deletion

---

## Deployment & Configuration

### Configuration Files

**`atlas_settings.py`**:
```text
ATLAS_URL = "http://localhost:23000"  # Configurable
USERNAME = "admin"  # From env or default
PASSWORD = "admin"  # From env or default
```

**`pyproject.toml`**:
- Project metadata
- Dependencies
- Development tools

### Docker Deployment

**Atlas Service**:
```bash
cd apache-atlas
docker compose up -d
# Access at http://localhost:23000
```

### Running the Project

```bash
# Install dependencies
uv sync

# Create types and enums
uv run scb_types.py type-create

# Create sample data products
uv run scb_dp.py

# Run tests
uv run pytest tests/

# Run integration tests
uv run pytest tests/integration/
```

---

## Summary

| Layer | Responsibility | Technologies |
|-------|-----------------|--------------|
| **Presentation** | CLI commands, user interfaces | Typer, Click |
| **Service** | Business logic, API orchestration | Custom services |
| **Model** | Data validation, type safety | Pydantic |
| **Builder** | Fluent entity construction | Design pattern |
| **Definition** | Type and ENUM specifications | Python dictionaries |
| **Client** | Atlas communication | apache-atlas SDK |
| **Integration** | Apache Atlas REST API | HTTP/REST |
| **Persistence** | Data storage | Atlas database |

This architecture ensures:
- ✅ **Separation of Concerns**: Each layer has clear responsibility
- ✅ **Testability**: Layers can be tested independently
- ✅ **Maintainability**: Easy to understand and modify
- ✅ **Extensibility**: New types and services can be added easily
- ✅ **Type Safety**: Pydantic provides compile-time checking
- ✅ **Error Handling**: Custom exceptions for debugging
- ✅ **Documentation**: Code is self-documenting through types and docstrings


