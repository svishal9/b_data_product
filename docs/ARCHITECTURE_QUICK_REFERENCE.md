# SCB Data Product - Architecture Quick Reference

## File Organization Map

```
PROJECT ROOT
├── 📚 DOCUMENTATION (Architecture & Guides)
│   ├── PROJECT_ARCHITECTURE.md           ← START HERE (this you're reading overview)
│   ├── ARCHITECTURE_DEEP_DIVE.md         ← Detailed patterns and hierarchies
│   ├── COMPONENT_INTERACTION_DIAGRAM.md  ← Visual interactions & sequences
│   ├── QUICK_START_ENTITIES.md           ← Getting started with entities
│   ├── ENTITY_TYPES.md                   ← Complete entity type reference
│   ├── PYDANTIC_MODELS_GUIDE.md          ← Data models documentation
│   └── README.md                         ← Quick start
│
├── 🏗️ CORE PACKAGE (scb_atlas/)
│   └── atlas/
│       ├── ⚙️ Configuration Layer
│       │   ├── atlas_client.py          ← Client factory
│       │   ├── atlas_settings.py        ← Settings (URL, auth)
│       │   ├── constants.py             ← Business constants
│       │   └── exceptions.py            ← Custom exceptions
│       │
│       ├── 📋 Type Definition Layer
│       │   └── atlas_type_def/
│       │       ├── scb_entity.py        ← Entity type definitions
│       │       ├── scb_enums.py         ← ENUM definitions
│       │       ├── scb_structs.py       ← Struct definitions
│       │       ├── scb_relationships.py ← Relationships
│       │       ├── scb_classifications.py ← Classifications
│       │       ├── base.py              ← Base classes
│       │       └── utility.py           ← Helper functions
│       │
│       ├── 📦 Data Model Layer (Pydantic)
│       │   └── metadata_models/
│       │       ├── data_product_model.py ← DataProduct models
│       │       ├── database.py           ← Database model
│       │       ├── table_model.py        ← Table model
│       │       ├── column_model.py       ← Column model
│       │       └── process_model.py      ← Process model
│       │
│       ├── 🏗️ Builder Layer (Fluent API)
│       │   └── entity_builders.py       ← Entity builders
│       │
│       ├── ⚡ Service Layer
│       │   └── service/
│       │       ├── entity_service.py    ← Entity CRUD operations
│       │       ├── type_service.py      ← Type management
│       │       └── discovery_service.py ← Search/query operations
│       │
│       └── 🔧 Utilities
│           ├── entity_models.py        ← Backward-compatible imports
│           └── read_data_product.py    ← Data product reader
│
├── 📝 CLI SCRIPTS (Entry Points)
│   ├── scb_types.py                     ← Type management CLI
│   ├── scb_enums.py                     ← ENUM management CLI
│   ├── scb_dp.py                        ← DataProduct CLI
│   ├── scb_dp_search.py                 ← Search CLI
│   └── ingest_workbook_to_atlas.py      ← Excel ingestion
│
├── 🧪 TESTS
│   ├── conftest.py                      ← Pytest configuration
│   ├── unit/                            ← Unit tests
│   └── integration/                     ← Integration tests
│
├── 📚 SCRIPTS
│   ├── prepare_atlas.sh                 ← Create types/enums
│   └── create_sample_data_products.sh   ← Sample data
│
├── 🐳 DOCKER
│   └── apache-atlas/                    ← Atlas deployment
│       └── docker-compose.yml           ← Docker setup
│
└── ⚙️ CONFIG
    ├── pyproject.toml                   ← Project config & deps
    ├── uv.lock                          ← Dependency lock
    └── CLAUDE.md                        ← Development guidance
```

---

## Layer Responsibilities

### 1. Client Layer (`atlas_client.py`)
**Responsibility**: Manage connection to Apache Atlas
```
User Code
    ↓
create_atlas_client()
    ↓
Apache Atlas REST API
```

### 2. Definition Layer (`atlas_type_def/`)
**Responsibility**: Define entity types, enums, and structures
```text
# File: scb_entity.py
scb_database = BaseEntityCategory(
    atlas_name="SCB_Database",
    display_name="SCB Database",
    super_types=["DataSet"],
    attributes=[...]
)

# File: scb_enums.py
{
    "name": "SCB_DataProductCategory",
    "elementDefs": [...]
}
```

### 3. Model Layer (`metadata_models/`)
**Responsibility**: Validate and structure data with Pydantic
```text
class CompleteDataProductModel(BaseModel):
    basic: DataProductBasicMetadata
    business: DataProductBusinessMetadata
    classification: DataProductClassification
    # ... more sections
```

### 4. Builder Layer (`entity_builders.py`)
**Responsibility**: Fluent API for entity construction
```text
builder = DatabaseEntityBuilder("name", "uri")
entity = builder.set_description("desc").build()
```

### 5. Service Layer (`service/`)
**Responsibility**: Business logic and API orchestration

| Service | Function |
|---------|----------|
| `entity_service` | Entity CRUD: create, read, update, delete |
| `type_service` | Type management: create, delete types |
| `discovery_service` | Search/query: DSL queries |

### 6. Exception Layer (`exceptions.py`)
**Responsibility**: Error handling and custom exceptions

| Exception | Use Case |
|-----------|----------|
| `AtlasConnectionError` | Connection failures |
| `EntityCreationError` | Entity creation failed |
| `UniqueConstraintViolationError` | Duplicate unique field |
| `SearchError` | Search query failed |

---

## Key Design Patterns

### 1. **Builder Pattern** (Fluent API)
```text
# File: entity_builders.py
builder = DatabaseEntityBuilder("db_name", "hdfs://uri")
entity = (builder
    .set_description("My database")
    .set_create_time("2024-01-01")
    .build()
)
```

### 2. **Service Layer Pattern** (Facade)
```text
# File: service/entity_service.py
def create_database_entity(client, database_name, location_uri):
    # Orchestrates: validation → building → API call
    pass
```

### 3. **Model Validation Pattern** (Pydantic)
```text
# File: metadata_models/data_product_model.py
class DataProductModel(BaseModel):
    name: str  # Required
    description: Optional[str] = None  # Optional
    
    # Validation automatically on instantiation
```

### 4. **Repository Pattern** (Search)
```text
# File: service/discovery_service.py
def dsl_search(client, query):
    # Abstracts search logic
    pass
```

### 5. **Factory Pattern** (Client Creation)
```text
# File: atlas_client.py
def create_atlas_client(username, password):
    # Centralized client creation
    pass
```

---

## Data Flow Diagram

```
QUICK REFERENCE FLOW:

1. CREATE TYPES
   ┌─ scb_types.py
   ├─ create_typedef()
   ├─ Atlas API
   └─ Types registered

2. CREATE ENTITY
   ┌─ Pydantic Model (validation)
   ├─ Builder (optional)
   ├─ entity_service
   ├─ Atlas API
   └─ Returns GUID

3. SEARCH ENTITIES
   ┌─ dsl_search()
   ├─ Atlas API (DSL)
   ├─ Returns matches
   └─ Format results

4. UPDATE ENTITY
   ┌─ Get by GUID
   ├─ Merge updates
   ├─ PUT Atlas API
   └─ Confirm update

5. DELETE ENTITY
   ┌─ Get GUID(s)
   ├─ DELETE Atlas API
   ├─ PURGE Atlas API
   └─ Confirm deletion
```

---

## Module Import Map

### From User Code
```text
# Import from main package
from scb_atlas.atlas import (
    create_atlas_client,
    create_database_entity,
    create_table_entity,
    create_column_entity,
    create_process_entity,
    create_data_product_entity,
    delete_entity,
    update_entity,
    dsl_search,
    # Models
    CompleteDataProductModel,
    DatabaseModel,
    TableModel,
    ColumnModel,
    ProcessModel,
    # Builders
    DatabaseEntityBuilder,
    TableEntityBuilder,
    ColumnEntityBuilder,
    ProcessEntityBuilder,
    # Exceptions
    EntityCreationError,
    AtlasConnectionError,
)
```

### From CLI Scripts
```text
# scb_types.py
from scb_atlas.atlas import (
    create_atlas_client,
    create_typedef,
    delete_typedef,
)
from scb_atlas.atlas.atlas_type_def import all_types, all_type_names

# scb_dp.py
from scb_atlas.atlas import (
    create_atlas_client,
    create_data_product_entity,
    dsl_search,
)
```

---

## Configuration Reference

### Environment Variables
```bash
# Atlas Connection
export ATLAS_URL="http://localhost:23000"
export ATLAS_USERNAME="admin"
export ATLAS_PASSWORD="admin"
```

### Python Configuration
```text
# File: atlas_settings.py
ATLAS_URL = os.getenv("ATLAS_URL", "http://localhost:23000")
USERNAME = os.getenv("ATLAS_USERNAME", "admin")
PASSWORD = os.getenv("ATLAS_PASSWORD", "admin")
```

---

## Common Usage Patterns

### Pattern 1: Create Database + Table + Columns
```text
from scb_atlas.atlas import (
    create_atlas_client,
    create_database_entity,
    create_table_entity,
    create_column_entity,
)

client = create_atlas_client()

# Create database
db_guid = create_database_entity(
    client,
    database_name="my_db",
    location_uri="hdfs://data/my_db"
)

# Create table
table_guid = create_table_entity(
    client,
    table_name="my_table",
    database_name="my_db"
)

# Create columns
col1_guid = create_column_entity(
    client,
    column_name="id",
    data_type="string",
    table_name="my_db.my_table",
    position=1
)
```

### Pattern 2: Create Data Product
```text
from scb_atlas.atlas import (
    create_atlas_client,
    create_data_product_entity,
)
from scb_atlas.atlas.metadata_models import CompleteDataProductModel

client = create_atlas_client()

model = CompleteDataProductModel(
    data_product_name="My DP",
    description="My data product",
    # ... more fields
)

guid = create_data_product_entity(client, **model.model_dump())
```

### Pattern 3: Search Entities
```text
from scb_atlas.atlas import (
    create_atlas_client,
    dsl_search,
)

client = create_atlas_client()

query = {
    "query": {
        "match": {
            "typeName": "SCB_Database"
        }
    }
}

results = dsl_search(client, query)
for entity in results['entities']:
    print(entity['attributes']['database_name'])
```

### Pattern 4: Error Handling
```text
from scb_atlas.atlas import (
    create_atlas_client,
    create_database_entity,
)
from scb_atlas.atlas.exceptions import (
    EntityCreationError,
    AtlasConnectionError,
    UniqueConstraintViolationError,
)

client = create_atlas_client()

try:
    guid = create_database_entity(client, "db", "hdfs://db")
except UniqueConstraintViolationError as e:
    print(f"Database already exists: {e}")
except EntityCreationError as e:
    print(f"Creation failed: {e}")
except AtlasConnectionError as e:
    print(f"Connection failed: {e}")
```

---

## Service Function Reference

### Entity Service

```text
# Database
create_database_entity(client, database_name, location_uri, description=None) -> str

# Table
create_table_entity(client, table_name, database_name, table_type=None, ...) -> str

# Column
create_column_entity(client, column_name, data_type, table_name, position, ...) -> str

# Process
create_process_entity(client, process_name, query_id, query_text, user_name=None, ...) -> str

# DataProduct
create_data_product_entity(client, **kwargs) -> str
create_dataset_entity(client, **kwargs) -> str

# Generic
create_entity(client, entity_dict) -> str
update_entity(client, guid, updates) -> bool
delete_entity(client, guids) -> bool
get_entity_by_guid(client, guid) -> Dict
```

### Type Service

```text
# Type Management
create_typedef(typedefs, client) -> List[str]
delete_typedef(client, type_name) -> bool
get_typedef(client, type_name) -> Dict
```

### Discovery Service

- `dsl_search(client, query) -> Dict`
- `search_by_type(client, type_name, limit=10) -> List[Entity]`
- `search_by_attribute(client, type_name, attr, value) -> List[Entity]`
- `advanced_search(client, query_obj) -> List[Entity]`

---

## Type Definitions Available

### Entity Types
- **SCB_Database**: Database storage system
- **SCB_Table**: Table within database
- **SCB_Column**: Column within table
- **SCB_Process**: Data transformation
- **SCB_DataProduct**: Data product catalog entry

### ENUM Types
- **SCB_DataProductCategory**: Source-Aligned, Intermediate, Consumer-Aligned
- **SCB_Domain**: Business domains
- **SCB_Granularity**: Data granularity
- **SCB_Lifecycle**: Lifecycle statuses
- **SCB_BusinessDomain**: Business domain classification
- And more...

### Struct Types
- **SCB_BusinessInfo**: Business metadata
- **SCB_Flags**: Classification flags
- **SCB_DataAccess**: Access rules
- **SCB_Adoption**: Usage/adoption info
- **SCB_Lifecycle**: Lifecycle details
- And more...

---

## Testing Reference

### Run All Tests
```bash
uv run pytest tests/
```

### Run Unit Tests Only
```bash
uv run pytest tests/unit/
```

### Run Integration Tests
```bash
uv run pytest tests/integration/
```

### Run Specific Test
```bash
uv run pytest tests/unit/test_entity_builders.py::test_database_builder
```

---

## Common Commands

```bash
# Install dependencies
uv sync

# Create all types and enums
uv run scb_types.py type-create

# Create sample data products
uv run scb_dp.py

# Search for data products
uv run scb_dp_search.py

# Run tests
uv run pytest tests/

# Start Atlas (Docker)
cd apache-atlas && docker compose up -d

# Access Atlas UI
# Navigate to: http://localhost:23000
```

---

## Troubleshooting Quick Reference

| Problem | Solution |
|---------|----------|
| "Type not found" | Run: `uv run scb_types.py type-create` |
| "Connection refused" | Start Atlas: `docker compose -f apache-atlas/docker-compose.yml up -d` |
| "Unique constraint error" | Entity already exists; verify attributes |
| "Authentication failed" | Check ATLAS_USERNAME and ATLAS_PASSWORD |
| "Entity not found" | Verify GUID or qualified name |
| "Validation error" | Check Pydantic model; review error message |

---

## Next Steps

1. **Read**: `PROJECT_ARCHITECTURE.md` for overview
2. **Explore**: `ARCHITECTURE_DEEP_DIVE.md` for patterns
3. **Visualize**: `COMPONENT_INTERACTION_DIAGRAM.md` for flows
4. **Learn**: `QUICK_START_ENTITIES.md` for hands-on
5. **Reference**: `ENTITY_TYPES.md` for API details
6. **Code**: Use patterns from `PYDANTIC_MODELS_GUIDE.md`

---

## Architecture Metrics

- **Total Modules**: 15+ (core package + services)
- **Type Definitions**: 6 custom entity types
- **ENUM Types**: 10+ enum definitions
- **Data Models**: 20+ Pydantic models
- **Exception Types**: 8+ custom exceptions
- **Service Functions**: 50+ functions
- **Builder Classes**: 5 builder classes
- **Lines of Code**: ~3000+ (core logic)
- **Documentation**: 20+ guide documents

---

## Architecture Principles

✅ **Single Responsibility**: Each module has one job
✅ **Open/Closed**: Easy to extend without modifying
✅ **Liskov Substitution**: Models are interchangeable
✅ **Interface Segregation**: Small, focused interfaces
✅ **Dependency Inversion**: Depend on abstractions
✅ **DRY**: Don't Repeat Yourself
✅ **KISS**: Keep It Simple, Stupid
✅ **YAGNI**: You Aren't Gonna Need It

---

## Glossary

| Term | Definition |
|------|-----------|
| **Atlas** | Apache Atlas metadata management system |
| **Entity** | Instance of a type (e.g., a specific database) |
| **Type** | Definition/schema for entities |
| **ENUM** | Set of predefined values |
| **STRUCT** | Complex data type with multiple fields |
| **GUID** | Global Unique Identifier for entities |
| **Qualified Name** | Unique string identifier (alternative to GUID) |
| **Lineage** | Relationships showing data flow |
| **Classification** | Tag/label attached to entities |
| **DSL** | Domain Specific Language (for queries) |

