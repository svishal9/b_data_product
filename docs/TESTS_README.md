# SCB Atlas Entity Types - Test Suite

## Overview

Comprehensive test suite for the SCB Atlas entity types functionality. Tests cover:
- Entity builders (Database, Table, Column, Process)
- Entity service functions
- Type definitions
- Integration with Atlas client
- Error handling and edge cases

## Test Structure

```
tests/
├── conftest.py                 # Pytest configuration and fixtures
├── unit/                       # Unit tests
│   ├── test_entity_builders.py # Tests for entity builders
│   └── test_atlas_types.py     # Tests for type definitions
├── integration/                # Integration tests
│   ├── test_entity_services.py # Tests for service functions
│   └── conftest.py             # Integration test fixtures
└── data/                       # Test data files
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test Suite
```bash
# Unit tests only
pytest tests/unit/ -v

# Integration tests only
pytest tests/integration/ -v

# Entity builders tests
pytest tests/unit/test_entity_builders.py -v

# Type definitions tests
pytest tests/unit/test_atlas_types.py -v

# Service functions tests
pytest tests/integration/test_entity_services.py -v
```

### Run Tests with Markers
```bash
# Run only unit tests
pytest -m unit

# Run only integration tests
pytest -m integration

# Run only slow tests
pytest -m slow
```

### Run with Coverage
```bash
pytest --cov=scb_atlas --cov-report=html
```

### Run in Verbose Mode
```bash
pytest -v
```

### Run Specific Test Function
```bash
pytest tests/unit/test_entity_builders.py::TestDatabaseEntityBuilder::test_database_builder_basic_creation -v
```

## Test Statistics

### Unit Tests
- **test_entity_builders.py**: ~50 test cases
  - DatabaseEntityBuilder: 7 tests
  - TableEntityBuilder: 8 tests
  - ColumnEntityBuilder: 8 tests
  - ProcessEntityBuilder: 9 tests
  - Entity structures: 3 tests
  - Qualified name generation: 3 tests
  - Edge cases: 5 tests

- **test_atlas_types.py**: ~40 test cases
  - Type definitions: 3 tests
  - Database entity: 4 tests
  - Table entity: 5 tests
  - Column entity: 5 tests
  - Process entity: 5 tests
  - DataProduct entity: 2 tests
  - Metadata: 3 tests
  - Enums: 3 tests
  - Structs: 3 tests
  - Classifications: 2 tests
  - Consistency: 4 tests
  - Attribute validation: 3 tests

### Integration Tests
- **test_entity_services.py**: ~35 test cases
  - Basic service functions: 6 tests
  - Entity creation: 9 tests
  - Error handling: 1 test
  - Chaining: 3 tests
  - Parameter validation: 3 tests
  - Builder integration: 3 tests

**Total: ~125 test cases**

## Test Categories

### Unit Tests

#### Entity Builders
- Basic entity creation
- Builder method chaining (fluent API)
- Attribute setting and validation
- Qualified name generation
- Optional vs required attributes
- Edge cases (empty strings, special characters, unicode)
- Independent builder instances

#### Type Definitions
- Structure validation
- Required fields presence
- Attribute type correctness
- Cardinality specification
- Index information
- Uniqueness constraints
- Consistency checks
- No duplicate names

### Integration Tests

#### Entity Service Functions
- Database entity creation
- Table entity creation
- Column entity creation
- Process entity creation
- Error handling
- Multiple related entity creation
- Builder output compatibility

#### Service Function Chaining
- Creating complete data flows
- Entity relationships
- Multiple entity types in sequence

#### Parameter Validation
- Optional parameters handling
- None value handling
- Empty string handling

## Test Fixtures

Global fixtures (tests/conftest.py):
- `project_root_path` - Project root directory
- `test_data_path` - Test data directory
- `sample_database_name` - "test_database"
- `sample_table_name` - "test_table"
- `sample_column_names` - ["id", "name", "email", "created_at"]
- `sample_process_name` - "test_process"

Mock fixtures (tests/integration/):
- `mock_atlas_client` - Mock Atlas client instance

## Testing Best Practices

1. **Isolation**: Each test is independent and doesn't depend on others
2. **Clarity**: Test names clearly describe what is being tested
3. **Coverage**: Tests cover happy path, edge cases, and error conditions
4. **Mocking**: Integration tests use mocks to avoid external dependencies
5. **Fixtures**: Common test data provided via fixtures
6. **Markers**: Tests marked for easy filtering and running

## Example Test Run Output

```
tests/unit/test_entity_builders.py::TestDatabaseEntityBuilder::test_database_builder_basic_creation PASSED
tests/unit/test_entity_builders.py::TestDatabaseEntityBuilder::test_database_builder_with_description PASSED
tests/unit/test_entity_builders.py::TestDatabaseEntityBuilder::test_database_builder_fluent_api PASSED
...
tests/integration/test_entity_services.py::TestEntityServiceFunctions::test_create_database_entity_basic PASSED
tests/integration/test_entity_services.py::TestEntityServiceFunctions::test_create_table_entity_basic PASSED
...

====== 125 passed in 2.45s ======
```

## CI/CD Integration

### GitHub Actions Example
```yaml
- name: Run Tests
  run: pytest --cov=scb_atlas --cov-report=xml

- name: Upload Coverage
  uses: codecov/codecov-action@v3
```

## Adding New Tests

1. **Unit Test Template**
```text
def test_something(self):
    """Test description."""
    # Arrange
    builder = DatabaseEntityBuilder("test", "hdfs://test")
    
    # Act
    entity = builder.build()
    
    # Assert
    assert entity['entity']['typeName'] == 'SCB_Database'
```

2. **Integration Test Template**
```text
def test_service_function(self, mock_atlas_client):
    """Test description."""
    mock_response = Mock()
    mock_response.mutatedEntities = {'CREATE': [Mock(guid='guid-123')]}
    mock_atlas_client.entity.create_entity.return_value = mock_response
    
    result = create_database_entity(mock_atlas_client, "test", "hdfs://test")
    
    assert result == True
```

## Troubleshooting

### Tests Won't Run
```bash
# Install test dependencies
uv sync

# Ensure pytest is available
python -m pytest --version
```

### Import Errors
```bash
# Make sure you're in project root
cd /Users/vishal/IdeaProjects/scb-data-product

# Run pytest from project root
pytest tests/
```

### Mock Issues
```text
# For mock issues, check that Mock objects are properly configured
from unittest.mock import Mock, MagicMock, patch
```

## Test Coverage Goals

- **Overall**: 80%+ coverage
- **Core modules**: 90%+ coverage
  - entity_builders.py
  - entity_service.py
  - atlas_types.py

Current coverage can be checked with:
```bash
pytest --cov=scb_atlas --cov-report=term-missing
```

## Related Documentation

- **ENTITY_TYPES.md** - Entity type API reference
- **IMPLEMENTATION_SUMMARY.md** - Implementation details
- **scb_example_entities.py** - Working examples
- **pytest documentation** - https://docs.pytest.org/

## Support

For questions about the test suite:
1. Check test file docstrings and comments
2. Review pytest documentation
3. Look at similar test patterns in existing tests
4. Check conftest.py for available fixtures

