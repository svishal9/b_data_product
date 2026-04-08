# SCB Data Product - Architecture Visual Summary

## Single-Page Architecture Overview

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃                   SCB DATA PRODUCT ARCHITECTURE                        ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛

TIER 1: USER LAYER (Entry Points)
╔═══════════════════════════════════════════════════════════════════════╗
║  CLI Scripts: scb_types.py | scb_enums.py | scb_dp.py | scb_dp_search.py  ║
║  Framework: Typer (Click-based)                                       ║
╚═══════════════════════════════════════════════════════════════════════╝
                                 ▼

TIER 2: SERVICE LAYER (Business Logic)
╔═════════════════╦═════════════════╦══════════════════════════════════╗
║  entity_service ║  type_service   ║  discovery_service               ║
╠═════════════════╬═════════════════╬══════════════════════════════════╣
║ • create        ║ • create_typedef║ • dsl_search                     ║
║ • update        ║ • delete_typedef║ • search_by_type                 ║
║ • delete        ║ • get_typedef   ║ • search_by_attribute            ║
║ • read          ║                 ║                                  ║
╚═════════════════╩═════════════════╩══════════════════════════════════╝
                                 ▼

TIER 3: BUILDER & MODEL LAYER (Data Transformation)
╔═════════════════╦═════════════════╦══════════════════════════════════╗
║  Entity Builders║  Pydantic Models║  Type Definitions                ║
╠═════════════════╬═════════════════╬══════════════════════════════════╣
║ • DatabaseB.   ║ • CompleteDP    ║ • scb_entity.py                  ║
║ • TableB.      ║ • DatabaseM.    ║ • scb_enums.py                   ║
║ • ColumnB.     ║ • TableM.       ║ • scb_structs.py                 ║
║ • ProcessB.    ║ • ColumnM.      ║ • scb_relationships.py           ║
║   (Fluent API) ║ • ProcessM.     ║ • base.py, utility.py            ║
╚═════════════════╩═════════════════╩══════════════════════════════════╝
                                 ▼

TIER 4: CORE CLIENT LAYER (Configuration & Exceptions)
╔═════════════════════════════════════════════════════════════════════╗
║  atlas_client.py | atlas_settings.py | constants.py | exceptions.py ║
║  • Connection factory    • Config (URL, auth)   • Error handling     ║
╚═════════════════════════════════════════════════════════════════════╝
                                 ▼

TIER 5: APACHE ATLAS SDK (Third-party Library)
╔═════════════════════════════════════════════════════════════════════╗
║  AtlasClient (REST API wrapper)                                     ║
║  • Entity API | Type API | Search API | Audit API                   ║
╚═════════════════════════════════════════════════════════════════════╝
                                 ▼

TIER 6: EXTERNAL SERVICE (Docker Container)
╔═════════════════════════════════════════════════════════════════════╗
║  Apache Atlas Service (localhost:23000)                             ║
║  • Type Registry | Entity Store | Search Engine | Graph DB          ║
║  • REST Endpoints | Persistence | Indexing                          ║
╚═════════════════════════════════════════════════════════════════════╝
```

---

## Component Relationships (Dependency Graph)

```
                        ┌─────────────────┐
                        │  User Code      │
                        │  (CLI Scripts)  │
                        └────────┬────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
            ┌──────────────┐ ┌────────────┐ ┌──────────────┐
            │entity_service│ │type_service│ │discovery_svc │
            └──────┬───────┘ └─────┬──────┘ └───────┬──────┘
                   │               │                │
            ┌──────▼───────────────▼────────────────▼──────┐
            │                                              │
            │  Builders  +  Models  +  Type Definitions   │
            │ (Fluent)     (Pydantic)  (Python dicts)     │
            │                                              │
            └──────┬───────────────────────────────────────┘
                   │
            ┌──────▼──────────────────┐
            │  atlas_client.py        │
            │  create_atlas_client()  │
            └──────┬──────────────────┘
                   │
            ┌──────▼──────────────────┐
            │  apache-atlas SDK       │
            │  (Apache Atlas Python)  │
            └──────┬──────────────────┘
                   │
            ┌──────▼──────────────────┐
            │  Apache Atlas Service   │
            │  (localhost:23000)      │
            └──────────────────────────┘
```

---

## Module Count by Layer

```
┌─────────────────────────────────────────────────────┐
│  LAYER                          │ MODULES │ PURPOSE │
├─────────────────────────────────┼─────────┼─────────┤
│ User/CLI                        │    4    │ Commands│
│ Service                         │    3    │ Logic   │
│ Builders                        │    1    │ Fluent  │
│ Models (Pydantic)              │    5    │ Validate│
│ Type Definitions               │    7    │ Schemas │
│ Client & Configuration         │    4    │ Setup   │
│ Exceptions                     │    1    │ Errors  │
│ Tests                          │   2+    │ Coverage│
├─────────────────────────────────┼─────────┼─────────┤
│ TOTAL                           │  27+    │         │
└─────────────────────────────────────────────────────┘
```

---

## Data Flow Lifecycle

```
CREATE ENTITY FLOW
═════════════════════════════════════════════════════════════

START
  │
  ├─► INPUT DATA (dict, model, builder)
  │
  ├─► VALIDATION (Pydantic)
  │   └─ Required fields, types, constraints
  │
  ├─► TRANSFORMATION (Builders)
  │   └─ Generate qualified names, structure data
  │
  ├─► SERVICE LAYER (entity_service)
  │   └─ Convert to Atlas format, business logic
  │
  ├─► ATLAS SDK (apache-atlas library)
  │   └─ HTTP POST to Atlas API
  │
  ├─► ATLAS SERVICE (localhost:23000)
  │   ├─ Type validation against schema
  │   ├─ Unique constraint checks
  │   ├─ Generate GUID
  │   ├─ Persist to database
  │   └─ Update search indexes
  │
  ├─► RESPONSE HANDLING
  │   └─ Extract GUID, log, return to caller
  │
  ▼ END: GUID returned
```

---

## Class Hierarchy

```
ENTITY TYPES
────────────────────────────────
Referenceable (Atlas built-in)
    │
    ├─► DataSet (Atlas built-in)
    │       │
    │       ├─► SCB_Database
    │       ├─► SCB_Table
    │       ├─► SCB_Column
    │       └─► SCB_DataProduct
    │
    └─► Process (Atlas built-in)
            │
            └─► SCB_Process


ENUM TYPES
────────────────────────────────
Enum (Python enum.Enum)
    │
    ├─► SCB_DataProductCategory
    ├─► SCB_Domain
    ├─► SCB_Granularity
    ├─► SCB_Lifecycle
    ├─► SCB_BusinessDomain
    └─► (More ENUMs...)


DATA MODELS
────────────────────────────────
BaseModel (Pydantic)
    │
    ├─► DataProductBasicMetadata
    ├─► DataProductBusinessMetadata
    ├─► DataProductClassification
    ├─► DataProductPorts
    ├─► DataProductSchemaField
    ├─► DataProductUsage
    ├─► DataProductLifecycle
    ├─► DataProductGovernanceMetadata
    ├─► CompleteDataProductModel
    ├─► DatabaseModel
    ├─► TableModel
    ├─► ColumnModel
    └─► ProcessModel


BUILDERS
────────────────────────────────
Builder Pattern
    │
    ├─► DatabaseEntityBuilder
    ├─► TableEntityBuilder
    ├─► ColumnEntityBuilder
    └─► ProcessEntityBuilder


EXCEPTIONS
────────────────────────────────
Exception (Python)
    │
    ├─► AtlasConnectionError
    ├─► AtlasAuthenticationError
    ├─► EntityCreationError
    ├─► EntityUpdateError
    ├─► EntityDeletionError
    ├─► EntityNotFoundError
    ├─► TypeDefinitionError
    └─► SearchError
```

---

## Communication Pattern

```
REQUEST FLOW TO ATLAS
═════════════════════════════════════════════════════════

User Code
   │
   ├─► Service Function
   │   └─ Orchestrates operation
   │
   ├─► Builder/Model
   │   └─ Validates and transforms data
   │
   ├─► Apache Atlas SDK
   │   └─ Constructs HTTP request
   │
   └─► HTTP POST/PUT/DELETE/GET
       └─ /api/atlas/v2/entity
       └─ /api/atlas/v2/types/typedefs
       └─ /api/atlas/v2/search/dsl
       └─ etc.


RESPONSE FLOW FROM ATLAS
═════════════════════════════════════════════════════════

Atlas Service
   │
   ├─► HTTP Response (JSON)
   │   └─ Status code, body with results
   │
   ├─► Apache Atlas SDK
   │   └─ Deserializes JSON to Python objects
   │
   ├─► Service Function
   │   └─ Processes response, handles errors
   │
   └─► User Code
       └─ Returns GUID, results, or raises exception
```

---

## File Importance Matrix

```
┌────────────────────────────────────────┐
│ CRITICALITY   │   FILE                 │
├────────────────────────────────────────┤
│ ⭐⭐⭐⭐⭐      │ atlas_client.py        │
│ (Essential)  │ entity_service.py      │
│              │ type_service.py        │
│              │ discovery_service.py   │
│              │ entity_builders.py     │
│              │ scb_entity.py          │
│              │ scb_enums.py           │
├────────────────────────────────────────┤
│ ⭐⭐⭐⭐       │ metadata_models/*      │
│ (Important)  │ atlas_settings.py      │
│              │ exceptions.py          │
│              │ base.py                │
├────────────────────────────────────────┤
│ ⭐⭐⭐        │ scb_structs.py         │
│ (Useful)     │ scb_relationships.py   │
│              │ scb_classifications.py │
│              │ utility.py             │
├────────────────────────────────────────┤
│ ⭐⭐         │ read_data_product.py   │
│ (Optional)   │ entity_models.py       │
│              │ constants.py           │
└────────────────────────────────────────┘
```

---

## Technology Stack

```
RUNTIME
  └─ Python 3.13+

PACKAGE MANAGEMENT
  └─ uv (fast Python package manager)

CORE DEPENDENCIES
  ├─ apache-atlas (≥0.0.16)      → Atlas REST API SDK
  ├─ pydantic (≥2.12.5)          → Data validation
  ├─ typer (≥0.24.0)             → CLI framework
  ├─ pandas (≥3.0.1)             → Data processing
  ├─ openpyxl (≥3.1.5)           → Excel support
  └─ pytest (≥9.0.2)             → Testing

EXTERNAL SERVICE
  └─ Apache Atlas (Docker container on port 23000)

IDE/TOOLS
  ├─ JetBrains IU (IntelliJ IDEA Ultimate)
  ├─ VS Code (alternative)
  └─ Git (version control)
```

---

## Architecture Strengths

```
✅ MODULARITY
   └─ Each layer has single responsibility
   
✅ TYPE SAFETY
   └─ Pydantic ensures data integrity
   
✅ EXTENSIBILITY
   └─ Easy to add new entity types
   
✅ TESTABILITY
   └─ Unit and integration tests supported
   
✅ ERROR HANDLING
   └─ Custom exceptions for debugging
   
✅ DOCUMENTATION
   └─ Self-documenting code with types
   
✅ FLEXIBILITY
   └─ Multiple ways to create entities
      (Builders, Models, Direct functions)
   
✅ REUSABILITY
   └─ Service functions used by all CLI scripts
```

---

## Architecture Weaknesses & Future Improvements

```
⚠️ CURRENT LIMITATIONS
   ├─ Synchronous operations only
   │   └─ Could add async support
   │
   ├─ Hardcoded credentials in some places
   │   └─ Should use secrets manager
   │
   ├─ Limited error recovery
   │   └─ Could add retry logic
   │
   ├─ No caching
   │   └─ Could cache type definitions
   │
   └─ No rate limiting
       └─ Could add exponential backoff

🚀 POTENTIAL ENHANCEMENTS
   ├─ Async/await support for bulk operations
   ├─ GraphQL API support
   ├─ Event-driven architecture
   ├─ Streaming data ingestion
   ├─ Advanced lineage tracking
   ├─ Quality metrics integration
   ├─ Data governance dashboard
   ├─ Workflow orchestration
   └─ Multi-tenant support
```

---

## Integration Points

```
INTERNAL INTEGRATIONS
├─ Service layer ↔ Builders/Models
├─ Builders/Models ↔ Client
├─ Client ↔ Configuration
├─ Services ↔ Type definitions
└─ Services ↔ Exception handling

EXTERNAL INTEGRATIONS
├─ Apache Atlas REST API
├─ Excel files (openpyxl, pandas)
├─ Environment variables (configuration)
└─ Docker (Atlas container)

POTENTIAL INTEGRATIONS
├─ Kafka (streaming metadata)
├─ Spark (big data lineage)
├─ Airflow (workflow metadata)
├─ Data catalogs (federation)
└─ BI tools (power BI, tableau)
```

---

## Deployment Architecture

```
DEVELOPMENT
┌──────────────────────────────┐
│ Python Environment           │
│  (Local machine)             │
├──────────────────────────────┤
│ • CLI scripts                │
│ • scb_atlas package          │
│ • Tests                      │
└────────────┬─────────────────┘
             │
             │ HTTP (port 23000)
             ▼
┌──────────────────────────────┐
│ Docker Container             │
│  (Apache Atlas)              │
├──────────────────────────────┤
│ • REST API endpoints         │
│ • Type registry              │
│ • Entity store               │
│ • Search engine              │
│ • Database (PostgreSQL)      │
│ • Graph DB (HBase)           │
└──────────────────────────────┘


PRODUCTION DEPLOYMENT
┌──────────────────────────────┐
│ Python Runtime               │
│  (Kubernetes / Virtual)      │
├──────────────────────────────┤
│ • Containerized app          │
│ • scb_atlas package          │
│ • Health checks              │
│ • Logging/monitoring         │
└────────────┬─────────────────┘
             │ (Secure)
             ▼
┌──────────────────────────────┐
│ Atlas Cluster (HA)           │
│  (On-premise / Cloud)        │
├──────────────────────────────┤
│ • Multiple Atlas nodes       │
│ • Load balancer              │
│ • High availability DB       │
│ • Replication/Backup         │
│ • Security (SSL/TLS)         │
│ • Authentication (LDAP/SAML) │
└──────────────────────────────┘
```

---

## Performance Characteristics

```
OPERATION              │ TIME          │ NOTES
───────────────────────┼───────────────┼──────────────────
Type creation          │ 100-500ms     │ One-time operation
Entity creation        │ 500-2000ms    │ Network + validation
Entity update          │ 500-2000ms    │ Similar to creation
Entity deletion        │ 500-2000ms    │ Includes purge
Search (DSL)          │ 100-1000ms    │ Depends on data size
Batch operations      │ Linear scale  │ Process N entities
Connection init       │ 50-200ms      │ Once per session

SCALABILITY LIMITS
├─ Single Atlas instance: ~1M entities
├─ Concurrent connections: ~100-500
└─ Query complexity: O(n) with indexes
```

---

## Documentation Map

```
📄 ARCHITECTURE_QUICK_REFERENCE.md
   └─ THIS FILE: Quick lookup guide
   
📄 PROJECT_ARCHITECTURE.md
   └─ Overview: System design, layers, patterns
   
📄 ARCHITECTURE_DEEP_DIVE.md
   └─ Details: Class hierarchies, lifecycles, patterns
   
📄 COMPONENT_INTERACTION_DIAGRAM.md
   └─ Interactions: Data flows, sequences, dependencies
   
📄 QUICK_START_ENTITIES.md
   └─ Tutorial: Getting started with entities
   
📄 ENTITY_TYPES.md
   └─ Reference: Complete entity type documentation
   
📄 PYDANTIC_MODELS_GUIDE.md
   └─ Guide: Data models and validation
   
📄 README.md
   └─ Start: Installation and basic usage
```


