# SCB Data Product - Architecture Deep Dive

## Table of Contents
1. [Package Structure Hierarchy](#package-structure-hierarchy)
2. [Type System Architecture](#type-system-architecture)
3. [Entity Lifecycle](#entity-lifecycle)
4. [Data Model Architecture](#data-model-architecture)
5. [Service Layer Design](#service-layer-design)
6. [Error Handling Strategy](#error-handling-strategy)
7. [Configuration Strategy](#configuration-strategy)
8. [Testing Architecture](#testing-architecture)

---

## Package Structure Hierarchy

### scb_atlas Package Organization

```
scb_atlas/
│
├── __init__.py
│   └── Exports public API:
│       ├── create_atlas_client
│       ├── create_typedef, delete_typedef
│       ├── create_*_entity functions
│       ├── delete_entity, update_entity
│       ├── dsl_search
│       └── All exception classes
│
└── atlas/
    │
    ├── __init__.py
    │   └── Re-exports service functions and models
    │
    ├── CONFIGURATION LAYER
    │   ├── constants.py
    │   │   └── Category labels and business constants
    │   ├── atlas_settings.py
    │   │   ├── ATLAS_URL
    │   │   ├── USERNAME
    │   │   └── PASSWORD (from environment or defaults)
    │   └── atlas_client.py
    │       └── create_atlas_client(username, password) -> AtlasClient
    │
    ├── DEFINITION LAYER
    │   ├── atlas_type_def/
    │   │   │
    │   │   ├── __init__.py
    │   │   │   └── Exports:
    │   │   │       ├── all_types (list of all type defs)
    │   │   │       ├── all_type_names (list of type names)
    │   │   │       ├── all_enums, all_structs
    │   │   │       └── Individual type objects
    │   │   │
    │   │   ├── base.py
    │   │   │   ├── BaseEntityCategory
    │   │   │   │   ├── atlas_name: str
    │   │   │   │   ├── display_name: str
    │   │   │   │   ├── super_types: List[str]
    │   │   │   │   └── attributes: List[Dict]
    │   │   │   └── prepare_type_definition() -> Dict
    │   │   │
    │   │   ├── scb_entity.py (Entity Types)
    │   │   │   ├── scb_database: BaseEntityCategory
    │   │   │   │   └── Attributes: database_name, locationUri, createTime
    │   │   │   ├── scb_table: BaseEntityCategory
    │   │   │   │   └── Attributes: table_name, tableType, temporary, etc.
    │   │   │   ├── scb_column: BaseEntityCategory
    │   │   │   │   └── Attributes: column_name, dataType, comment, position
    │   │   │   ├── scb_process: BaseEntityCategory
    │   │   │   │   └── Attributes: process_name, queryId, queryText, etc.
    │   │   │   └── scb_data_product: BaseEntityCategory
    │   │   │       └── Attributes: data_product_name, category, tags, etc.
    │   │   │
    │   │   ├── scb_enums.py (ENUM Types)
    │   │   │   ├── SCB_DataProductCategory enum
    │   │   │   ├── SCB_Domain enum
    │   │   │   ├── SCB_Granularity enum
    │   │   │   ├── SCB_Lifecycle enum
    │   │   │   └── ... (more enums)
    │   │   │
    │   │   ├── scb_structs.py (Struct Types)
    │   │   │   ├── SCB_BusinessInfo struct
    │   │   │   ├── SCB_Flags struct
    │   │   │   ├── SCB_DataAccess struct
    │   │   │   └── ... (more structs)
    │   │   │
    │   │   ├── scb_relationships.py
    │   │   │   └── Relationship type definitions
    │   │   │
    │   │   ├── scb_classifications.py
    │   │   │   └── Classification/tag definitions
    │   │   │
    │   │   └── utility.py
    │   │       ├── prepare_qualified_name(entity_type, name) -> str
    │   │       ├── generate_guid() -> str
    │   │       └── Helper functions
    │   │
    │   ├── metadata_models/
    │   │   │
    │   │   ├── __init__.py
    │   │   │   └── Exports all Pydantic models
    │   │   │
    │   │   ├── data_product_model.py
    │   │   │   ├── DataProductBasicMetadata (Pydantic)
    │   │   │   ├── DataProductBusinessMetadata (Pydantic)
    │   │   │   ├── DataProductClassification (Pydantic)
    │   │   │   ├── DataProductPorts (Pydantic)
    │   │   │   ├── DataProductSchemaField (Pydantic)
    │   │   │   ├── DataProductUsage (Pydantic)
    │   │   │   ├── DataProductLifecycle (Pydantic)
    │   │   │   ├── DataProductGovernanceMetadata (Pydantic)
    │   │   │   ├── CompleteDataProductModel (Pydantic - Composite)
    │   │   │   ├── LifecycleStatusEnum (str, Enum)
    │   │   │   └── SensitivityEnum (str, Enum)
    │   │   │
    │   │   ├── database.py
    │   │   │   └── DatabaseModel (Pydantic)
    │   │   │
    │   │   ├── table_model.py
    │   │   │   ├── TableTypeEnum (str, Enum)
    │   │   │   └── TableModel (Pydantic)
    │   │   │
    │   │   ├── column_model.py
    │   │   │   └── ColumnModel (Pydantic)
    │   │   │
    │   │   └── process_model.py
    │   │       └── ProcessModel (Pydantic)
    │   │
    │   └── entity_builders.py
    │       ├── DatabaseEntityBuilder
    │       │   ├── __init__(database_name, location_uri)
    │       │   ├── set_description(desc) -> self
    │       │   ├── set_create_time(time) -> self
    │       │   └── build() -> Dict
    │       ├── TableEntityBuilder
    │       │   ├── __init__(table_name, database_name)
    │       │   ├── set_table_type(type) -> self
    │       │   ├── set_temporary(bool) -> self
    │       │   └── build() -> Dict
    │       ├── ColumnEntityBuilder
    │       │   ├── __init__(column_name, data_type, table_name)
    │       │   ├── set_position(pos) -> self
    │       │   ├── set_comment(comment) -> self
    │       │   └── build() -> Dict
    │       ├── ProcessEntityBuilder
    │       │   ├── __init__(process_name, query_id, query_text)
    │       │   ├── add_input_entity(type, qname) -> self
    │       │   ├── add_output_entity(type, qname) -> self
    │       │   ├── set_user_name(user) -> self
    │       │   └── build() -> Dict
    │       └── (More builders...)
    │
    ├── SERVICE LAYER
    │   └── service/
    │       │
    │       ├── __init__.py
    │       │   └── Exports service functions
    │       │
    │       ├── entity_service.py
    │       │   ├── Database Operations
    │       │   │   └── create_database_entity(client, **kwargs) -> str (GUID)
    │       │   ├── Table Operations
    │       │   │   └── create_table_entity(client, **kwargs) -> str
    │       │   ├── Column Operations
    │       │   │   └── create_column_entity(client, **kwargs) -> str
    │       │   ├── Process Operations
    │       │   │   └── create_process_entity(client, **kwargs) -> str
    │       │   ├── DataProduct Operations
    │       │   │   ├── create_data_product_entity(client, **kwargs) -> str
    │       │   │   └── create_dataset_entity(client, **kwargs) -> str
    │       │   ├── Generic Operations
    │       │   │   ├── create_entity(client, entity_dict) -> str
    │       │   │   ├── update_entity(client, guid, updates) -> bool
    │       │   │   ├── delete_entity(client, guids) -> bool
    │       │   │   └── get_entity_by_guid(client, guid) -> Dict
    │       │   └── Utility
    │       │       ├── convert_to_atlas_model(data) -> Dict
    │       │       └── _convert_to_atlas_attributes(entity_dict) -> Dict
    │       │
    │       ├── type_service.py
    │       │   ├── create_typedef(typedefs, client) -> List[str]
    │       │   ├── delete_typedef(client, type_name) -> bool
    │       │   ├── get_typedef(client, type_name) -> Dict
    │       │   ├── Validation
    │       │   │   └── _validate_typedef(typedef) -> bool
    │       │   └── Conversion
    │       │       └── _convert_types(typedefs) -> Dict (for API)
    │       │
    │       └── discovery_service.py
    │           ├── dsl_search(client, query) -> Dict[entities]
    │           ├── search_by_type(client, type_name, limit) -> List[Entity]
    │           ├── search_by_attribute(client, type, attr, value) -> List[Entity]
    │           ├── advanced_search(client, query_obj) -> List[Entity]
    │           └── Query Building
    │               └── _build_dsl_query(criteria) -> Dict
    │
    ├── EXCEPTION LAYER
    │   └── exceptions.py
    │       ├── AtlasConnectionError
    │       ├── AtlasAuthenticationError
    │       ├── EntityCreationError
    │       ├── EntityDeletionError
    │       ├── EntityUpdateError
    │       ├── EntityNotFoundError
    │       ├── TypeDefinitionError
    │       ├── TypeAlreadyExistsError
    │       ├── UniqueConstraintViolationError
    │       └── SearchError
    │
    ├── UTILITY LAYER
    │   ├── entity_models.py
    │   │   └── Backward-compatible imports from metadata_models
    │   ├── read_data_product.py
    │   │   ├── read_data_product(atlas_client, guid) -> CompleteDataProductModel
    │   │   ├── read_by_qualified_name(client, qname) -> Entity
    │   │   └── format_for_display(entity) -> Dict
    │   │
    │   └── exceptions.py (already listed above)
```

---

## Type System Architecture

### Type Definition Hierarchy

```
╔════════════════════════════════════════╗
║   Apache Atlas Type System              ║
╚════════════════════════════════════════╝
          ▲
          │ Inherits
          │
    ┌─────┴──────┬──────────────┬─────────┐
    │            │              │         │
    ▼            ▼              ▼         ▼
 STRUCT      ENTITY           ENUM    CLASSIFICATION
 (Complex)   (Instance-able)  (Value)  (Tags/Labels)
    │            │              │         │
    ├── Attributes definitions
    │
    └── Atlas Built-in Types
        ├── DataSet
        │   └── Hierarchy:
        │       ├── scb_database
        │       ├── scb_table
        │       ├── scb_column
        │       └── scb_data_product
        │
        ├── Process
        │   └── Hierarchy:
        │       └── scb_process
        │
        ├── Referenceable (built-in)
        │
        └── Glossary (built-in)


Inheritance Chain Example:
┌──────────────────────────────────┐
│ Referenceable (Atlas built-in)   │
│ • qualifiedName (unique)         │
│ • name                           │
│ • description                    │
│ • owner                          │
│ • labels                         │
│ • classifications               │
│ • attributes                    │
└──────────────────────────────────┘
          ▲
          │ extends
          │
┌──────────────────────────────────┐
│ DataSet (Atlas built-in)         │
│ • Inherited from Referenceable   │
│ • schema                         │
│ • databaseName                   │
│ • tableType                      │
└──────────────────────────────────┘
          ▲
          │ extends
          │
┌──────────────────────────────────┐
│ SCB_Database (Custom)            │
│ • Inherited from DataSet         │
│ • database_name (unique)         │
│ • locationUri                    │
│ • createTime                     │
└──────────────────────────────────┘
```

### Type Definition to Atlas API Conversion

```
Python Dictionary
┌───────────────────────────────────────────┐
│ {                                         │
│   "atlas_name": "SCB_Table",              │
│   "display_name": "SCB Table",            │
│   "super_types": ["DataSet"],             │
│   "attributes": [                         │
│     {                                     │
│       "name": "table_name",               │
│       "typeName": "string",               │
│       "isOptional": False,                │
│       "isUnique": True                    │
│     },                                    │
│     ...                                   │
│   ]                                       │
│ }                                         │
└───────────────────────────────────────────┘
          │
          │ type_service.create_typedef()
          │ [Validation + Transformation]
          ▼
Atlas API Format (JSON)
┌───────────────────────────────────────────┐
│ {                                         │
│   "entityDefs": [                         │
│     {                                     │
│       "name": "SCB_Table",                │
│       "typeVersion": "1.0",               │
│       "description": "SCB Table",         │
│       "displayName": "SCB Table",         │
│       "superTypes": ["DataSet"],          │
│       "category": "ENTITY",               │
│       "attributeDefs": [                  │
│         {                                 │
│           "name": "table_name",           │
│           "typeName": "string",           │
│           "cardinality": "SINGLE",        │
│           "isOptional": false,            │
│           "isUnique": true,               │
│           "isIndexable": true             │
│         },                                │
│         ...                               │
│       ]                                   │
│     }                                     │
│   ]                                       │
│ }                                         │
└───────────────────────────────────────────┘
          │
          │ Apache Atlas SDK (HTTP POST)
          ▼
Atlas Service (Database)
```

---

## Entity Lifecycle

### Creation Lifecycle

```
START: User requests entity creation
  │
  │ 1. PREPARATION PHASE
  ├─► Collect data (dict, model, or builder)
  │   └─ Source: User input, Excel, API
  │
  │ 2. VALIDATION PHASE
  ├─► Pydantic model validation
  │   ├─ Type checking
  │   ├─ Required field checking
  │   ├─ Custom validators
  │   └─ Raises: ValidationError
  │
  │ 3. TRANSFORMATION PHASE
  ├─► Builder construction (optional)
  │   ├─ Method chaining
  │   ├─ Generate qualified names
  │   └─ Build final entity dict
  │
  │ 4. PRE-SUBMISSION PHASE
  ├─► Service function processing
  │   ├─ Convert to Atlas format
  │   ├─ Handle relationships
  │   ├─ Check unique constraints (business logic)
  │   └─ Prepare request payload
  │
  │ 5. SUBMISSION PHASE
  ├─► Atlas API call
  │   ├─ POST /api/atlas/v2/entity
  │   ├─ Send JSON payload
  │   └─ Handle network/timeout errors
  │
  │ 6. ATLAS PROCESSING PHASE
  ├─► Atlas service validation
  │   ├─ Validate against type definition
  │   ├─ Validate unique constraints (DB level)
  │   ├─ Generate GUID if not provided
  │   ├─ Persist to database
  │   ├─ Update search indexes
  │   └─ Raise: Validation errors, constraint violations
  │
  │ 7. POST-SUBMISSION PHASE
  ├─► Handle response
  │   ├─ Parse response JSON
  │   ├─ Extract GUID
  │   ├─ Log creation
  │   └─ Handle errors
  │
  ▼ END: Return GUID to caller
   
Errors can occur at stages 2, 4, 5, 6, 7
└─ Each propagated as specific exception type
```

### Entity Update Lifecycle

```
START: User requests entity update
  │
  ├─► Get current entity (by GUID or qualified name)
  │
  ├─► Merge updates with current state
  │
  ├─► Validate updated entity
  │   └─ Same validation as creation
  │
  ├─► PUT /api/atlas/v2/entity
  │   └─ Send updated entity with GUID
  │
  ├─► Atlas validation
  │   └─ Same as creation
  │
  ▼ END: Return success/failure

Note: Cannot update "unique" attributes
└─ These become immutable after creation
```

### Entity Deletion Lifecycle

```
START: User requests entity deletion
  │
  ├─► Collect GUIDs to delete
  │
  ├─► Pre-deletion checks (optional)
  │   ├─ Verify entity exists
  │   ├─ Check for lineage dependencies
  │   └─ Check for references
  │
  ├─► DELETE /api/atlas/v2/entity/guid/{guid}
  │   └─ Mark for deletion
  │
  ├─► PURGE /api/atlas/v2/entity/purge/{guid}
  │   ├─ Permanent removal
  │   ├─ Remove from search indexes
  │   └─ Remove from database
  │
  ▼ END: Return success/failure
```

---

## Data Model Architecture

### Composite Data Product Model

```
CompleteDataProductModel (Pydantic BaseModel)
│
├── Basic Metadata
│   └── DataProductBasicMetadata
│       ├── data_product_name: str (required)
│       ├── description: str (optional, default="")
│       └── data_product_category: str (optional)
│
├── Business Metadata
│   └── DataProductBusinessMetadata
│       ├── business_purpose: str
│       ├── gcfo_owner_name: Optional[str]
│       └── gcfo_owner_contact: Optional[str]
│
├── Classification
│   └── DataProductClassification
│       ├── sensitivity: SensitivityEnum
│       ├── personal: bool
│       ├── geo_location_access: Optional[List[str]]
│       ├── regulatory_flags: Optional[List[str]]
│       ├── certifications: Optional[List[str]]
│       └── approval: Optional[str]
│
├── Ports (Input/Output)
│   └── DataProductPorts
│       ├── data_product_input_ports: Optional[List[str]]
│       ├── data_product_output_port: Optional[str]
│       ├── data_product_input_process: Optional[str]
│       ├── data_product_output_process: Optional[str]
│       ├── delivery_channels: Optional[List[str]]
│       ├── access_rules: Optional[str]
│       ├── data_landing_pattern: Optional[str]
│       └── data_handshake: Optional[str]
│
├── Schema Definition
│   └── DataProductSchemaField
│       ├── field_name: str
│       ├── field_type: Optional[str]
│       ├── field_description: Optional[str]
│       ├── category: Optional[str]
│       └── is_cde: Optional[bool]
│
├── Usage
│   └── DataProductUsage
│       ├── users: Optional[List[str]]
│       ├── use_cases: Optional[List[str]]
│       └── adoption_rate: Optional[float]
│
├── Lifecycle
│   └── DataProductLifecycle
│       ├── lifecycle_status: LifecycleStatusEnum
│       ├── created_date: Optional[date]
│       ├── modified_date: Optional[date]
│       └── retired_date: Optional[date]
│
└── Governance
    └── DataProductGovernanceMetadata
        ├── approval_status: Optional[str]
        ├── audit_trail: Optional[str]
        ├── compliance_checks: Optional[List[str]]
        └── sla_commitments: Optional[str]


Usage Example:
┌─────────────────────────────────────────────────┐
│ model = CompleteDataProductModel(               │
│     basic=DataProductBasicMetadata(             │
│         data_product_name="FM FX Linear Trade", │
│         data_product_category="Source-Aligned"  │
│     ),                                          │
│     business=DataProductBusinessMetadata(       │
│         business_purpose="Finance DP"           │
│     ),                                          │
│     classification=DataProductClassification( │
│         sensitivity=SensitivityEnum.INTERNAL   │
│     ),                                          │
│     ports=DataProductPorts(                     │
│         data_product_input_ports=["table1"]    │
│     ),                                          │
│     # ... more sections                         │
│ )                                               │
│                                                 │
│ # Access as dict                                │
│ data_dict = model.model_dump()                  │
│                                                 │
│ # Validate automatically on instantiation       │
│ # Raises ValidationError if invalid            │
└─────────────────────────────────────────────────┘
```

---

## Service Layer Design

### Service Function Patterns

#### Pattern 1: Simple Entity Creation

```text
def create_database_entity(
    atlas_client: AtlasClient,
    database_name: str,
    location_uri: str,
    description: Optional[str] = None
) -> str:
    """
    Workflow:
    1. Validate inputs
    2. Create entity dict
    3. Call API
    4. Return GUID
    """
    try:
        # Input validation
        if not database_name or not database_name.strip():
            raise ValueError("database_name required")
        
        # Build entity
        builder = DatabaseEntityBuilder(database_name, location_uri)
        if description:
            builder.set_description(description)
        entity = builder.build()
        
        # Create in Atlas
        response = atlas_client.entity.create(
            AtlasEntityWithExtInfo(entity)
        )
        
        guid = response.guid
        logger.info(f"Created database: {guid}")
        return guid
        
    except Exception as e:
        logger.error(f"Failed to create database: {e}")
        raise EntityCreationError(f"...") from e
```

#### Pattern 2: Model-Based Creation

```text
def create_data_product_entity(
    atlas_client: AtlasClient,
    model: CompleteDataProductModel
) -> str:
    """
    Workflow:
    1. Validate model (auto by Pydantic)
    2. Convert to entity dict
    3. Call API
    4. Return GUID
    """
    try:
        # Model is already validated (Pydantic BaseModel)
        entity_dict = convert_to_atlas_model(model.model_dump())
        
        response = atlas_client.entity.create(
            AtlasEntityWithExtInfo(entity_dict)
        )
        
        return response.guid
        
    except ValidationError as e:
        raise EntityCreationError(f"Model validation failed: {e}") from e
```

#### Pattern 3: Search Service

```text
def dsl_search(
    atlas_client: AtlasClient,
    query: Dict
) -> Dict:
    """
    Workflow:
    1. Validate query format
    2. Call search API
    3. Parse results
    4. Return formatted results
    """
    try:
        # Execute DSL search
        results = atlas_client.search.dsl(query)
        
        # Parse and format
        entities = results.get('entities', [])
        
        return {
            'count': len(entities),
            'entities': entities,
            'offset': results.get('offset', 0)
        }
        
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise SearchError(f"...") from e
```

---

## Error Handling Strategy

### Exception Hierarchy

```
Exception (Python built-in)
│
├── ValidationError (Pydantic)
│   │
│   └── Caught and wrapped by service functions
│
└── Custom Exceptions (exceptions.py)
    │
    ├── AtlasException (Base class)
    │   │
    │   ├── Connection Errors
    │   │   ├── AtlasConnectionError
    │   │   │   └── "Cannot connect to Atlas service"
    │   │   └── AtlasAuthenticationError
    │   │       └── "Authentication failed"
    │   │
    │   ├── Type Errors
    │   │   ├── TypeDefinitionError
    │   │   │   └── "Invalid type definition"
    │   │   └── TypeAlreadyExistsError
    │   │       └── "Type already exists in Atlas"
    │   │
    │   ├── Entity Errors
    │   │   ├── EntityCreationError
    │   │   │   └── "Failed to create entity"
    │   │   ├── EntityUpdateError
    │   │   │   └── "Failed to update entity"
    │   │   ├── EntityDeletionError
    │   │   │   └── "Failed to delete entity"
    │   │   └── EntityNotFoundError
    │   │       └── "Entity not found"
    │   │
    │   ├── Constraint Errors
    │   │   └── UniqueConstraintViolationError
    │   │       └── "Unique constraint violated"
    │   │
    │   └── Search Errors
    │       └── SearchError
    │           └── "Search query failed"
    │
    └── (Can be extended with domain-specific exceptions)
```

### Error Handling Pattern

```text
def service_function(...) -> ResultType:
    """
    Try-except pattern:
    1. Validate inputs
    2. Execute main logic
    3. Catch specific exceptions
    4. Log and wrap errors
    5. Raise appropriate custom exception
    6. Return result or raise
    """
    try:
        # Input validation
        _validate_inputs(...)
        
        # Main logic
        result = _do_main_operation()
        
        # Log success
        logger.info(f"Operation succeeded: ...")
        
        return result
        
    except ValidationError as e:
        logger.error(f"Validation failed: {e}")
        raise CustomError(f"Specific error message") from e
        
    except AtlasException as e:
        # Atlas-specific errors
        logger.error(f"Atlas error: {e}")
        raise  # Re-raise as-is
        
    except requests.RequestException as e:
        # Network errors
        logger.error(f"Network error: {e}")
        raise AtlasConnectionError(f"...") from e
        
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error: {e}")
        raise CustomError(f"Unexpected error: {e}") from e
```

---

## Configuration Strategy

### Environment-Based Configuration

```
atlas_settings.py
├── ATLAS_URL
│   ├── Default: "http://localhost:23000"
│   ├── Override: Environment variable "ATLAS_URL"
│   └── Use case: Different Atlas instances per environment
│
├── USERNAME
│   ├── Default: "admin"
│   ├── Override: Environment variable "ATLAS_USERNAME"
│   └── Use case: Different users per environment
│
└── PASSWORD
    ├── Default: "admin"
    ├── Override: Environment variable "ATLAS_PASSWORD"
    └── Use case: Different passwords per environment


Environment Setup Example:
┌──────────────────────────────────┐
│ Development (.env)               │
│ ATLAS_URL=http://localhost:23000 │
│ ATLAS_USERNAME=admin             │
│ ATLAS_PASSWORD=admin             │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ Staging                          │
│ ATLAS_URL=https://atlas-staging  │
│ ATLAS_USERNAME=stg_user          │
│ ATLAS_PASSWORD=stg_pass          │
└──────────────────────────────────┘

┌──────────────────────────────────┐
│ Production                       │
│ ATLAS_URL=https://atlas-prod     │
│ ATLAS_USERNAME=prod_user         │
│ ATLAS_PASSWORD=prod_pass         │
│ (Use secrets manager in prod)    │
└──────────────────────────────────┘
```

### Project Configuration

```
pyproject.toml
│
├── [project]
│   ├── name = "scb_atlas"
│   ├── version = "0.1.0"
│   ├── description = "..."
│   ├── requires-python = ">=3.13"
│   │
│   └── dependencies
│       ├── apache-atlas>=0.0.16
│       ├── openpyxl>=3.1.5
│       ├── pandas>=3.0.1
│       ├── pydantic>=2.12.5
│       ├── pytest>=9.0.2
│       └── typer>=0.24.0
│
└── [dependency-groups]
    └── dev
        └── ruff>=0.15.7


uv.lock (Lock file)
└── Exact versions of all dependencies
    └── For reproducible builds
```

---

## Testing Architecture

### Test Structure

```
tests/
│
├── conftest.py
│   ├── Shared pytest fixtures
│   ├── Mocking setup
│   ├── Test data setup
│   └── Cleanup teardown
│
├── unit/
│   │
│   ├── test_entity_builders.py
│   │   └── Test each builder class
│   │
│   ├── test_metadata_models.py
│   │   └── Test Pydantic models validation
│   │
│   ├── test_exceptions.py
│   │   └── Test exception classes
│   │
│   └── test_utilities.py
│       └── Test utility functions
│
└── integration/
    │
    ├── conftest.py
    │   ├── Real Atlas connection fixture
    │   ├── Docker container setup
    │   ├── Type creation before tests
    │   └── Cleanup after tests
    │
    ├── test_entity_services.py
    │   ├── Test entity creation end-to-end
    │   ├── Test entity updates
    │   └── Test entity deletion
    │
    ├── test_type_services.py
    │   ├── Test type creation
    │   ├── Test type deletion
    │   └── Test type retrieval
    │
    ├── test_discovery_service.py
    │   ├── Test DSL search
    │   ├── Test search filters
    │   └── Test search results
    │
    └── test_workflows.py
        ├── Test complete workflows
        ├── Test error scenarios
        └── Test data lineage
```

### Testing Patterns

#### Unit Test Pattern

```text
def test_database_builder():
    """Test DatabaseEntityBuilder"""
    builder = DatabaseEntityBuilder("test_db", "hdfs://test")
    builder.set_description("Test description")
    
    entity = builder.build()
    
    assert entity['typeName'] == 'SCB_Database'
    assert entity['attributes']['database_name'] == 'test_db'
    assert entity['attributes']['locationUri'] == 'hdfs://test'
```

#### Integration Test Pattern

- `def test_create_database_entity(atlas_client): ...`
- `guid = create_database_entity(atlas_client, "integration_test_db", "hdfs://integration")`
- `entity = atlas_client.entity.get(guid)`
- `delete_entity(atlas_client, [guid])`

---

## Summary

This architecture provides:

✅ **Modularity**: Clear separation of concerns
✅ **Type Safety**: Pydantic ensures data integrity
✅ **Extensibility**: Easy to add new entity types
✅ **Testability**: Unit and integration tests
✅ **Error Handling**: Comprehensive exception hierarchy
✅ **Configuration**: Environment-based settings
✅ **Documentation**: Self-documenting code
✅ **Performance**: Efficient API usage patterns

