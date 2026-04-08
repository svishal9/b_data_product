# SCB Data Product - Component Interaction Diagram

## Component Architecture Overview

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          USER LAYER (CLI Scripts)                            │
├─────────────────────────────────────────────────────────────────────────────┤
│  scb_types.py          scb_enums.py         scb_dp.py      scb_dp_search.py │
│  (Type Mgmt)           (ENUM Mgmt)          (DP Mgmt)      (Search)         │
└───────────────────────────┬──────────────────────────────────┬───────────────┘
                            │                                  │
        ┌───────────────────┼──────────────────────────────────┼──────────────────┐
        │                   │                                  │                  │
        ▼                   ▼                                  ▼                  ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│                      SERVICE LAYER (scb_atlas/atlas/service/)               │
├──────────────────────┬──────────────────────┬───────────────────────────────┤
│ entity_service.py    │  type_service.py     │  discovery_service.py         │
├──────────────────────┼──────────────────────┼───────────────────────────────┤
│ • create_database    │ • create_typedef     │ • dsl_search                  │
│ • create_table       │ • delete_typedef     │ • search_by_type              │
│ • create_column      │ • get_typedef        │ • advanced_queries            │
│ • create_process     │ • validate_types     │                               │
│ • create_entity      │                      │                               │
│ • update_entity      │                      │                               │
│ • delete_entity      │                      │                               │
└──────┬───────────────┴──────┬───────────────┴───────────────────────────────┘
       │                      │
       └──────────────────────┼─────────────────────────────────┐
                              │                                 │
        ┌─────────────────────┼─────────────────┐              │
        │                     │                 │              │
        ▼                     ▼                 ▼              ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│               DEFINITION & BUILDER LAYER                                     │
├─────────────────────────┬──────────────────────┬──────────────────────────┤
│ Type Definitions        │ Entity Builders      │ Metadata Models          │
│ (atlas_type_def/)       │ (entity_builders.py) │ (metadata_models/)       │
├─────────────────────────┼──────────────────────┼──────────────────────────┤
│ • scb_entity.py         │ • DatabaseBuilder    │ • DataProductModel       │
│ • scb_enums.py          │ • TableBuilder       │ • DatabaseModel          │
│ • scb_structs.py        │ • ColumnBuilder      │ • TableModel             │
│ • scb_relationships.py  │ • ProcessBuilder     │ • ColumnModel            │
│ • scb_classifications.py│                      │ • ProcessModel           │
│ • base.py               │ Fluent API Pattern   │ • *Metadata              │
│ • utility.py            │ (Method Chaining)    │ (Pydantic Models)        │
└─────────────────────────┴──────────────────────┴──────────────────────────┘
        ▲                     ▲                      ▲
        │                     │                      │
        └─────────────────────┼──────────────────────┘
                              │
        ┌─────────────────────┴─────────────────────┐
        │                                           │
        ▼                                           ▼
┌─────────────────────────────┐      ┌──────────────────────────────┐
│  CORE CLIENT LAYER          │      │  EXCEPTION HANDLING          │
├─────────────────────────────┤      ├──────────────────────────────┤
│ • atlas_client.py           │      │ • exceptions.py              │
│   (Connection factory)      │      │   - AtlasConnectionError     │
│                             │      │   - EntityCreationError      │
│ • atlas_settings.py         │      │   - TypeDefinitionError      │
│   (Configuration)           │      │   - And more...              │
│                             │      │                              │
│ • constants.py              │      │ Custom exception hierarchy   │
│   (Category labels, etc.)   │      │ for better error handling    │
│                             │      │                              │
│ • read_data_product.py      │      │                              │
│   (Data product reader)     │      │                              │
└─────────────────────────────┘      └──────────────────────────────┘
        ▲                                    ▲
        │                                    │
        │                    ┌───────────────┘
        │                    │
        ▼                    ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│         APACHE ATLAS SDK (Third-party: apache-atlas library)                │
├─────────────────────────────────────────────────────────────────────────────┤
│ • AtlasClient (REST client)                                                 │
│ • Entity API integration                                                    │
│ • Type API integration                                                      │
│ • Search API integration                                                    │
└─────────────────────────────────────────────────────────────────────────────┘
        ▲
        │ HTTP/REST
        │ (JSON payloads)
        ▼
┌─────────────────────────────────────────────────────────────────────────────┐
│      APACHE ATLAS SERVICE (Docker Container - localhost:23000)             │
├─────────────────────────────────────────────────────────────────────────────┤
│ • REST API Endpoints                                                        │
│ • Type Registry                                                             │
│ • Entity Store                                                              │
│ • Search Engine                                                             │
│ • Graph Database (stores relationships/lineage)                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Flow Interactions

### 1. Type Creation Sequence

```
┌──────────┐
│  User    │
└────┬─────┘
     │
     │ uv run scb_types.py type-create
     ▼
┌──────────────────┐
│ scb_types.py     │
│ CLI Script       │
└────┬─────────────┘
     │
     │ import all_types from atlas_type_def
     ▼
┌──────────────────────┐
│ type_service.py      │
│ create_typedef()     │
└────┬─────────────────┘
     │
     │ Convert Python dict to Atlas API format
     │ Validate type definitions
     │ Generate JSON payload
     │
     ▼
┌──────────────────────┐
│ atlas_client.py      │
│ AtlasClient          │
└────┬─────────────────┘
     │
     │ POST /api/atlas/v2/types/typedefs
     │ (Apache Atlas SDK)
     │
     ▼
┌─────────────────────────────────────────────┐
│ Apache Atlas Service                        │
│ • Validates type definitions                │
│ • Stores type metadata in database          │
│ • Makes types available for entity creation │
└─────────────────────────────────────────────┘
     │
     │ Response: Success/Error
     ▼
┌──────────────────────┐
│ create_typedef()     │
│ returns result       │
└────┬─────────────────┘
     │
     │ Log: "Type created successfully"
     ▼
┌──────────────┐
│ Console      │
│ Output       │
└──────────────┘
```

### 2. Entity Creation Sequence

```
┌──────────────────┐
│ User Code        │
│ scb_dp.py        │
└────┬─────────────┘
     │
     │ Prepare entity data (dict or Excel)
     ▼
┌──────────────────────────────────┐
│ Pydantic Model                   │
│ (e.g., CompleteDataProductModel) │
└────┬─────────────────────────────┘
     │
     │ Validate and coerce data types
     │ Check required fields
     │ Apply defaults
     │
     ▼
┌──────────────────────────────────┐
│ Entity Builder (Optional)        │
│ (e.g., DatabaseEntityBuilder)    │
└────┬─────────────────────────────┘
     │
     │ Fluent API: builder.set_xxx().build()
     │ Generates qualified names
     │ Constructs final entity dict
     │
     ▼
┌──────────────────────────────────┐
│ entity_service.py                │
│ create_[type]_entity()           │
└────┬─────────────────────────────┘
     │
     │ Prepare Atlas entity payload
     │ Handle relationships/lineage
     │ Pre-creation validation
     │
     ▼
┌──────────────────────────────────┐
│ atlas_client.py                  │
│ AtlasClient.entity.create()      │
└────┬─────────────────────────────┘
     │
     │ POST /api/atlas/v2/entity
     │ Send JSON payload
     │ (Apache Atlas SDK)
     │
     ▼
┌─────────────────────────────────────────────┐
│ Apache Atlas Service                        │
│ • Validates entity against type definition  │
│ • Validates unique constraints              │
│ • Generates GUID                            │
│ • Persists entity data                      │
│ • Updates search indexes                    │
└─────────────────────────────────────────────┘
     │
     │ Response: {guid: "uuid", ...}
     ▼
┌──────────────────────────────────┐
│ entity_service returns GUID      │
└────┬─────────────────────────────┘
     │
     │ Entity created successfully
     ▼
┌──────────────────────────────────┐
│ User gets GUID                   │
│ Can use for relationships,       │
│ lineage, updates                 │
└──────────────────────────────────┘
```

### 3. Search/Discovery Sequence

```
┌──────────────────────┐
│ User Code            │
│ scb_dp_search.py     │
└────┬─────────────────┘
     │
     │ Construct search criteria
     │ (type, attributes, filters)
     │
     ▼
┌──────────────────────────────────┐
│ discovery_service.py             │
│ dsl_search(client, query)        │
└────┬─────────────────────────────┘
     │
     │ Build DSL query JSON
     │ { "query": { "match": {...} } }
     │
     ▼
┌──────────────────────────────────┐
│ atlas_client.py                  │
│ AtlasClient.search.dsl()         │
└────┬─────────────────────────────┘
     │
     │ POST /api/atlas/v2/search/dsl
     │ Send query JSON
     │ (Apache Atlas SDK)
     │
     ▼
┌─────────────────────────────────────────────┐
│ Apache Atlas Service                        │
│ • Parses DSL query                          │
│ • Searches indexes                          │
│ • Applies filters                           │
│ • Returns matching entities                 │
└─────────────────────────────────────────────┘
     │
     │ Response: { entities: [...], count: N }
     ▼
┌──────────────────────────────────┐
│ discovery_service               │
│ Processes results               │
└────┬─────────────────────────────┘
     │
     │ Returns formatted results
     ▼
┌──────────────────────────────────┐
│ User receives list of entities   │
│ with full attributes             │
└──────────────────────────────────┘
```

---

## Module Dependencies

```
scb_dp.py
  └── create_atlas_client()                 [atlas_client.py]
  └── create_data_product_entity()          [entity_service.py]
  └── CompleteDataProductModel              [metadata_models/data_product_model.py]
  └── dsl_search()                          [discovery_service.py]

scb_types.py
  └── create_atlas_client()                 [atlas_client.py]
  └── create_typedef()                      [type_service.py]
  └── delete_typedef()                      [type_service.py]
  └── all_types                             [atlas_type_def/__init__.py]
      └── scb_entity definitions            [atlas_type_def/scb_entity.py]
      └── scb_enum definitions              [atlas_type_def/scb_enums.py]
      └── scb_struct definitions            [atlas_type_def/scb_structs.py]

entity_service.py
  └── create_atlas_client()                 [atlas_client.py]
  └── *EntityBuilder classes                [entity_builders.py]
  └── *Model classes                        [metadata_models/]
  └── type_coerce()                         [apache_atlas SDK]
  └── dsl_search()                          [discovery_service.py]
  └── Custom exceptions                     [exceptions.py]

entity_builders.py
  └── prepare_qualified_name()              [atlas_type_def/utility.py]

type_service.py
  └── Custom exceptions                     [exceptions.py]
```

---

## Deployment Topology

```
Development Machine
┌──────────────────────────────────────────────────────────────┐
│                                                              │
│  Python Environment                                          │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ scb_atlas Package                                      │  │
│  │  ├── Service Layer                                     │  │
│  │  ├── Builders & Models                                 │  │
│  │  └── Client Layer                                      │  │
│  └────────────────────────────────────────────────────────┘  │
│  ┌────────────────────────────────────────────────────────┐  │
│  │ CLI Scripts (scb_dp.py, scb_types.py, etc.)           │  │
│  │  └── Execute: uv run script.py                         │  │
│  └────────────────────────────────────────────────────────┘  │
│           │                                                   │
│           │ HTTP REST Calls                                   │
│           │ (Apache Atlas SDK)                               │
│           │                                                   │
└───────────┼────────────────────────────────────────────────┬──┘
            │                                                 │
┌───────────▼─────────────────────────────────────────────────▼──┐
│          Docker Container: Apache Atlas                        │
├────────────────────────────────────────────────────────────────┤
│ Service Port: 23000                                            │
│ ┌──────────────────────────────────────────────────────────┐   │
│ │ REST API Endpoints                                       │   │
│ │  • /api/atlas/v2/types/typedefs                         │   │
│ │  • /api/atlas/v2/entity                                 │   │
│ │  • /api/atlas/v2/search/dsl                             │   │
│ │  • etc.                                                  │   │
│ └────┬─────────────────────────────────────────────────────┘   │
│      │                                                          │
│ ┌────▼─────────────────────────────────────────────────────┐   │
│ │ Atlas Core Services                                      │   │
│ │  • Type Registry                                         │   │
│ │  • Entity Store                                          │   │
│ │  • Search Engine                                         │   │
│ │  • Audit Log                                             │   │
│ └────┬─────────────────────────────────────────────────────┘   │
│      │                                                          │
│ ┌────▼─────────────────────────────────────────────────────┐   │
│ │ Persistent Storage                                       │   │
│ │  • PostgreSQL/HBase (type definitions)                   │   │
│ │  • Graph DB (relationships/lineage)                      │   │
│ │  • Search indexes                                        │   │
│ └──────────────────────────────────────────────────────────┘   │
└────────────────────────────────────────────────────────────────┘
```

---

## Class Hierarchy

```
BaseModel (Pydantic)
├── DataProductBasicMetadata
├── DataProductBusinessMetadata
├── DataProductClassification
├── DataProductPorts
├── DataProductSchemaField
├── DataProductUsage
├── DataProductLifecycle
├── DataProductGovernanceMetadata
├── CompleteDataProductModel
├── DatabaseModel
├── TableModel
├── ColumnModel
└── ProcessModel


BaseEntityCategory
├── scb_database
├── scb_table
├── scb_column
├── scb_process
└── scb_data_product


Builder Pattern
├── DatabaseEntityBuilder
│   ├── set_description()
│   ├── set_create_time()
│   └── build()
├── TableEntityBuilder
│   ├── set_table_type()
│   ├── set_temporary()
│   └── build()
├── ColumnEntityBuilder
│   ├── set_data_type()
│   ├── set_position()
│   └── build()
└── ProcessEntityBuilder
    ├── add_input_entity()
    ├── add_output_entity()
    └── build()


Exception Hierarchy
├── AtlasConnectionError
├── AtlasAuthenticationError
├── EntityCreationError
├── EntityDeletionError
├── EntityUpdateError
└── TypeDefinitionError
```

---

## Configuration & Settings

```
atlas_settings.py
├── ATLAS_URL = "http://localhost:23000"
│   └── Configurable via environment: ATLAS_URL
├── USERNAME = "admin"
│   └── Configurable via environment: ATLAS_USERNAME
└── PASSWORD = "admin"
    └── Configurable via environment: ATLAS_PASSWORD


pyproject.toml
├── Project metadata
├── Dependencies
│   ├── apache-atlas>=0.0.16
│   ├── openpyxl>=3.1.5
│   ├── pandas>=3.0.1
│   ├── pydantic>=2.12.5
│   ├── pytest>=9.0.2
│   └── typer>=0.24.0
└── Dev dependencies
    └── ruff>=0.15.7
```

---

## API Contract Summary

### Service Functions Pattern
```text
def create_entity_type(
    atlas_client: AtlasClient,
    param1: str,
    param2: str,
    optional_param: Optional[str] = None
) -> str:
    """
    Args:
        atlas_client: Connected Atlas client
        param1: Required parameter
        param2: Required parameter
        optional_param: Optional parameter
        
    Returns:
        str: GUID of created entity
        
    Raises:
        EntityCreationError: If creation fails
    """
    # Implementation
    pass
```

### Model Validation Pattern
```text
from pydantic import BaseModel, Field

class MyModel(BaseModel):
    required_field: str = Field(..., description="...")
    optional_field: Optional[str] = Field(None, description="...")
    typed_field: int = Field(default=0, description="...")
    
    # Validation
    @field_validator('required_field')
    def validate_required(cls, v):
        if not v.strip():
            raise ValueError("...")
        return v
```

### Builder Pattern
```text
class MyBuilder:
    def __init__(self, required1: str, required2: str):
        self.required1 = required1
        self.required2 = required2
        self.optional = None
        
    def set_optional(self, value: str) -> 'MyBuilder':
        self.optional = value
        return self
        
    def build(self) -> dict:
        return {
            "required1": self.required1,
            "required2": self.required2,
            "optional": self.optional
        }

# Usage
entity = MyBuilder("value1", "value2").set_optional("opt").build()
```

---

## Performance Considerations

1. **Batch Operations**: Consider batching multiple entity creations
2. **Search Optimization**: Use specific search criteria to reduce results
3. **Type Caching**: Types are created once and reused
4. **Connection Pooling**: Atlas client handles connection management
5. **Async Operations**: Current implementation is synchronous (can be extended)


