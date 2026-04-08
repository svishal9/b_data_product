"""
Pytest configuration for SCB Atlas tests.
Configures test discovery, fixtures, and settings.
"""

import pytest
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def pytest_configure(config):
    """Configure pytest with custom markers."""
    config.addinivalue_line(
        "markers", "unit: mark test as a unit test"
    )
    config.addinivalue_line(
        "markers", "integration: mark test as an integration test"
    )
    config.addinivalue_line(
        "markers", "slow: mark test as slow running"
    )


def pytest_collection_modifyitems(config, items):
    """Modify test collection to auto-mark tests."""
    for item in items:
        # Mark tests based on their location
        if "unit" in str(item.fspath):
            item.add_marker(pytest.mark.unit)
        elif "integration" in str(item.fspath):
            item.add_marker(pytest.mark.integration)


@pytest.fixture(scope="session")
def project_root_path():
    """Return the project root path."""
    return Path(__file__).parent.parent


@pytest.fixture(scope="session")
def test_data_path(project_root_path):
    """Return the path to test data files."""
    return project_root_path / "tests" / "data"


@pytest.fixture
def sample_database_name():
    """Return a sample database name for testing."""
    return "test_database"


@pytest.fixture
def sample_table_name():
    """Return a sample table name for testing."""
    return "test_table"


@pytest.fixture
def sample_column_names():
    """Return sample column names for testing."""
    return ["id", "name", "email", "created_at"]


@pytest.fixture
def sample_process_name():
    """Return a sample process name for testing."""
    return "test_process"

