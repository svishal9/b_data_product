## Atlas Client for SCB Data Product Solution

A Python client for interacting with Apache Atlas API to create Data Products in Apache Atlas. This project provides a complete framework for ingesting Data Product metadata from Excel workbooks, automatically creating related database, table, and column entities, and establishing proper data lineage.

---

## Quick Start

### 1. Start Apache Atlas

Run the `docker-compose.yml` from the `apache-atlas` directory:

```shell
$ docker compose up -d
```

It may take a few minutes for Apache-Atlas to start. Once started you can access the Atlas UI at `http://localhost:23000`

**Note:** Docker compose in this repository starts Atlas on port 23000, instead of the usual 21000.

### 2. Installation

1. Install uv for managing packages - follow [installation steps](https://docs.astral.sh/uv/getting-started/installation/)

2. Run:
```shell
$ uv sync
```

### 3. Prepare Atlas (ENUMs, Structures, Data Product Types)

```shell
$ ./scripts/prepare_atlas.sh
```

### 4. Create Sample Data Products

Option 1: Insert sample data products:
```shell
$ ./scripts/create_sample_data_products.sh
```

Option 2: Ingest from Excel workbook:
```shell
$ uv run python recreate_data_products_from_workbook.py sample_data/metadata_example.xlsx
```

### 5. Unified CLI (single entry point)

All core workflows can now be executed from one file/command:

```shell
$ uv run python scb_dp_cli.py --help
# or after install
$ scb --help
```

Common examples:

```shell
# Ingest workbook (create entities + lineage)
$ uv run python scb_dp_cli.py ingest sample_data/metadata_example.xlsx

# Recreate workbook entities (delete existing SCB_DataProduct by qualifiedName, then create)
$ uv run python scb_dp_cli.py recreate sample_data/metadata_example.xlsx

# Strict dry-run validation only
$ uv run python scb_dp_cli.py ingest sample_data/metadata_example.xlsx --dry-run --strict

# Manage types
$ uv run python scb_dp_cli.py types create
$ uv run python scb_dp_cli.py types clean

# Cleanup all SCB entities/types
$ uv run python scb_dp_cli.py cleanup

# Create sample entities using Pydantic models
$ uv run python scb_dp_cli.py sample-entities

# Run tests
$ uv run python scb_dp_cli.py tests unit
$ uv run python scb_dp_cli.py tests integration
```

Migrating from old script commands? See [`LEGACY_COMMAND_MIGRATION.md`](./docs/LEGACY_COMMAND_MIGRATION.md).

---

## 📚 Documentation

All project documentation is organized in the `docs/` folder. Start with [`ARCHITECTURE_DOCUMENTATION_INDEX.md`](./docs/ARCHITECTURE_DOCUMENTATION_INDEX.md), then browse the documents below:

### 📋 Latest Updates
- **[RECENT_UPDATES.md](./docs/RECENT_UPDATES.md)** - Latest improvements, documentation reorganization, and code cleanup
- **[DOCUMENTATION_VERIFICATION.md](./docs/DOCUMENTATION_VERIFICATION.md)** - Comprehensive verification report
- **[DOCUMENTATION_CLEANUP_REPORT.md](./docs/DOCUMENTATION_CLEANUP_REPORT.md)** - Cleanup report for code examples and unused references
- **[ANCHOR_LINKS_FIXED.md](./docs/ANCHOR_LINKS_FIXED.md)** - Documentation anchor link fixes
- **[LEGACY_COMMAND_MIGRATION.md](./docs/LEGACY_COMMAND_MIGRATION.md)** - Mapping from legacy script commands to unified `scb` CLI commands

### Getting Started
- **[ATLAS_SETUP_GUIDE.md](./docs/ATLAS_SETUP_GUIDE.md)** - Detailed guide for setting up Apache Atlas in Kubernetes
- **[QUICK_START_ENTITIES.md](./docs/QUICK_START_ENTITIES.md)** - Quick start for creating entities
- **[CREATE_ENTITIES_QUICK_START.md](./docs/CREATE_ENTITIES_QUICK_START.md)** - Fast track to creating entities with Pydantic

### Workbook-to-Atlas Framework
- **[WORKBOOK_FRAMEWORK_README.md](./docs/WORKBOOK_FRAMEWORK_README.md)** - Framework overview for ingesting Data Products from Excel workbooks
- **[MIGRATION_GUIDE.md](./docs/MIGRATION_GUIDE.md)** - Guide for migrating existing data products

### Pydantic Models
- **[PYDANTIC_MODELS_GUIDE.md](./docs/PYDANTIC_MODELS_GUIDE.md)** - Comprehensive guide to Pydantic models
- **[PYDANTIC_MODELS_INDEX.md](./docs/PYDANTIC_MODELS_INDEX.md)** - Index of all Pydantic models
- **[PYDANTIC_QUICK_REFERENCE.md](./docs/PYDANTIC_QUICK_REFERENCE.md)** - Quick reference for Pydantic models
- **[PYDANTIC_INTEGRATION_SUMMARY.md](./docs/PYDANTIC_INTEGRATION_SUMMARY.md)** - Integration summary with Pydantic

### Architecture & Design
- **[PROJECT_ARCHITECTURE.md](./docs/PROJECT_ARCHITECTURE.md)** - High-level project architecture
- **[ARCHITECTURE_DEEP_DIVE.md](./docs/ARCHITECTURE_DEEP_DIVE.md)** - Deep dive into architecture details
- **[ARCHITECTURE_QUICK_REFERENCE.md](./docs/ARCHITECTURE_QUICK_REFERENCE.md)** - Quick reference for architecture
- **[ARCHITECTURE_VISUAL_SUMMARY.md](./docs/ARCHITECTURE_VISUAL_SUMMARY.md)** - Visual architecture summary
- **[ARCHITECTURE_DOCUMENTATION_INDEX.md](./docs/ARCHITECTURE_DOCUMENTATION_INDEX.md)** - Architecture documentation index
- **[COMPONENT_INTERACTION_DIAGRAM.md](./docs/COMPONENT_INTERACTION_DIAGRAM.md)** - Component interaction diagrams
- **[ARCHITECTURE_GENERATION_SUMMARY.md](./docs/ARCHITECTURE_GENERATION_SUMMARY.md)** - Summary of architecture generation

### Entity Types & Definitions
- **[ENTITY_TYPES.md](./docs/ENTITY_TYPES.md)** - Entity types and definitions
- **[IMPLEMENTATION_SUMMARY.md](./docs/IMPLEMENTATION_SUMMARY.md)** - Implementation summary
- **[IMPLEMENTATION_CHECKLIST.md](./docs/IMPLEMENTATION_CHECKLIST.md)** - Implementation checklist

### Testing
- **[TESTS_README.md](./docs/TESTS_README.md)** - Testing guide and overview
- **[TEST_EXECUTION_REPORT.md](./docs/TEST_EXECUTION_REPORT.md)** - Test execution report
- **[TEST_FILES_REFERENCE.md](./docs/TEST_FILES_REFERENCE.md)** - Reference for test files
- **[TEST_COMPLETION_CHECKLIST.md](./docs/TEST_COMPLETION_CHECKLIST.md)** - Test completion checklist
- **[TEST_SUITE_SUMMARY.md](./docs/TEST_SUITE_SUMMARY.md)** - Test suite summary

### Troubleshooting & Fixes
- **[TROUBLESHOOTING_ENTITIES.md](./docs/TROUBLESHOOTING_ENTITIES.md)** - Troubleshooting guide for entity creation
- **[FIXES_APPLIED.md](./docs/FIXES_APPLIED.md)** - Summary of fixes applied to the project
- **[DOCUMENTATION_CHECKLIST.md](./docs/DOCUMENTATION_CHECKLIST.md)** - Documentation checklist

### Reference
- **[CLAUDE.md](./docs/CLAUDE.md)** - AI assistant context and guidelines

---

## Project Structure

```
scb-data-product/
├── docs/                          # 📚 All documentation
├── scb_atlas/                     # Main Python package
│   └── atlas/                     # Atlas client and entity management
│       ├── service/               # Entity creation services
│       ├── metadata_models/       # Pydantic metadata models
│       └── atlas_type_def/        # Type definitions
├── tests/                         # Unit and integration tests
├── sample_data/                   # Sample data files
├── apache-atlas/                  # Kubernetes/Docker manifests for Atlas
├── scripts/                       # Setup and utility scripts
├── pyproject.toml                 # Project configuration
└── recreate_data_products_from_workbook.py  # Main CLI for workbook ingestion
```

---

## Key Features

✅ **Excel Workbook to Atlas Ingestion** - Automatically parse Excel workbooks and create Atlas entities  
✅ **Automatic Lineage Creation** - Creates input/output port tables with proper relationships  
✅ **Schema Visualization** - Defines columns for output-port tables from workbook schema  
✅ **Enum Normalization** - Maps user-friendly values to Atlas enum constants  
✅ **Idempotent Operations** - Safe to re-run; automatically deletes existing entities before recreating  
✅ **Pydantic Models** - Type-safe metadata models with validation  
✅ **Comprehensive Tests** - Unit and integration tests with mocked Atlas services  

---

## Support

For issues and troubleshooting, refer to:
- **[TROUBLESHOOTING_ENTITIES.md](./docs/TROUBLESHOOTING_ENTITIES.md)** - Entity creation troubleshooting
- **[ATLAS_SETUP_GUIDE.md](./docs/ATLAS_SETUP_GUIDE.md)** - Atlas setup issues
