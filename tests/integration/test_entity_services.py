# noinspection PyArgumentList,SqlNoDataSourceInspection
# pyright: reportCallIssue=false
"""
Integration tests for SCB Atlas entity service functions.

Tests the entity creation service functions with mock Atlas client.
These tests verify:
- Entity creation functions
- Atlas client interaction
- Entity persistence
"""

import pytest
from unittest.mock import Mock
from scb_atlas.atlas.service.entity_service import (
    create_database_from_model,
    create_column_from_model,
    create_process_from_model,
    create_table_from_model,
    _create_entity_in_atlas
)
from scb_atlas.atlas.metadata_models import (
    DatabaseModel,
    TableModel,
    #ColumnModel,
    StandardColumnModel,
    ProcessModel,
    TableTypeEnum,
)
from scb_atlas.atlas.exceptions import EntityCreationError


class TestEntityServiceFunctions:
    """Tests for entity service functions."""

    @pytest.fixture
    def mock_atlas_client(self):
        """Create a mock Atlas client."""
        client = Mock()
        client.entity = Mock()
        return client

    def test_create_database_entity_basic(self, mock_atlas_client):
        """Test basic database entity creation."""
        # Mock the entity creation response
        mock_response = Mock()
        mock_response.mutatedEntities = {'CREATE': [Mock(guid='guid-123')]}
        mock_atlas_client.entity.create_entity.return_value = mock_response

        database = DatabaseModel(
            database_name="test_db",
            location_uri="hdfs://test"
        )

        result = create_database_from_model(
            mock_atlas_client,
            database       
        )

        assert result == True
        mock_atlas_client.entity.create_entity.assert_called_once()

    def test_create_database_entity_with_description(self, mock_atlas_client):
        """Test database entity creation with description."""
        mock_response = Mock()
        mock_response.mutatedEntities = {'CREATE': [Mock(guid='guid-123')]}
        mock_atlas_client.entity.create_entity.return_value = mock_response

        database = DatabaseModel(
            database_name="test_db",
            location_uri="hdfs://test",
            description="Test database"
        )

        result = create_database_from_model(
            mock_atlas_client,
            database       
        )

        assert result == True

    def test_create_table_entity_basic(self, mock_atlas_client):
        """Test basic table entity creation."""
        mock_response = Mock()
        mock_response.mutatedEntities = {'CREATE': [Mock(guid='guid-456')]}
        mock_atlas_client.entity.create_entity.return_value = mock_response

        table = TableModel(
            table_name="test_table",
            database_name="test_db"
        )

        result = create_table_from_model(
            mock_atlas_client,
            table
        )

        assert result == True

    def test_create_table_entity_with_options(self, mock_atlas_client):
        """Test table entity creation with all options."""
        mock_response = Mock()
        mock_response.mutatedEntities = {'CREATE': [Mock(guid='guid-456')]}
        mock_atlas_client.entity.create_entity.return_value = mock_response

        table = TableModel(
            table_name="data_table",
            database_name="analytics_db",
            description="Analytics data table",
            table_type=TableTypeEnum.EXTERNAL,
        )

        result = create_table_from_model(
            mock_atlas_client,
            table
        )

        assert result == True

    def test_create_column_entity_basic(self, mock_atlas_client):
        """Test basic column entity creation."""
        mock_response = Mock()
        mock_response.mutatedEntities = {'CREATE': [Mock(guid='guid-789')]}
        mock_atlas_client.entity.create_entity.return_value = mock_response

        column = StandardColumnModel(
            field_name="id",
            data_type="bigint",
            table_name="test_db.test_table"
        )

        result = create_column_from_model(
            mock_atlas_client,
            column
        )

        assert result == True

    def test_create_column_entity_with_comment(self, mock_atlas_client):
        """Test column entity creation with comment and position."""
        mock_response = Mock()
        mock_response.mutatedEntities = {'CREATE': [Mock(guid='guid-789')]}
        mock_atlas_client.entity.create_entity.return_value = mock_response

        column = StandardColumnModel(
            field_name="amount",
            data_type="decimal(18,2)",
            table_name="test_db.test_table",
            description="Transaction amount"
        )

        result = create_column_from_model(
            mock_atlas_client,
            column
        )

        assert result == True

    def test_create_process_entity_advanced_basic(self, mock_atlas_client):
        """Test basic process entity creation."""
        mock_response = Mock()
        mock_response.mutatedEntities = {'CREATE': [Mock(guid='guid-abc')]}
        mock_atlas_client.entity.create_entity.return_value = mock_response

        process = ProcessModel(
            process_name="daily_etl",
            query_id="etl_001",
            query_text="query text"
        )

        result = create_process_from_model(
            mock_atlas_client,
            process
        )

        assert result == True

    def test_create_process_entity_advanced_with_all_params(self, mock_atlas_client):
        """Test process entity creation with all parameters."""
        mock_response = Mock()
        mock_response.mutatedEntities = {'CREATE': [Mock(guid='guid-abc')]}
        mock_atlas_client.entity.create_entity.return_value = mock_response

        process = ProcessModel(
            process_name="complex_job",
            query_id="job_001",
            query_text="query text",
            user_name="data_pipeline",
            start_time=1708953600000,
            end_time=1708957200000
        )

        result = create_process_from_model(
            mock_atlas_client,
            process
        )

        assert result == True


    def test_create_entity_in_atlas_create_operation(self, mock_atlas_client):
        """Test _create_entity_in_atlas with CREATE operation."""
        mock_response = Mock()
        mock_response.mutatedEntities = {
            'CREATE': [Mock(guid='guid-123')]
        }
        mock_atlas_client.entity.create_entity.return_value = mock_response

        entity_data = {
            'entity': {
                'typeName': 'SCB_Database',
                'attributes': {
                    'database_name': 'test_db',
                    'locationUri': 'hdfs://test',
                    'qualifiedName': 'scb:::dp:::test_db'
                }
            }
        }

        _create_entity_in_atlas(mock_atlas_client, entity_data)
        mock_atlas_client.entity.create_entity.assert_called_once()

    def test_create_entity_in_atlas_update_operation(self, mock_atlas_client):
        """Test _create_entity_in_atlas with UPDATE operation."""
        mock_response = Mock()
        mock_response.mutatedEntities = {
            'UPDATE': [Mock(guid='guid-123')]
        }
        mock_atlas_client.entity.create_entity.return_value = mock_response

        entity_data = {
            'entity': {
                'typeName': 'SCB_Database',
                'attributes': {
                    'database_name': 'existing_db',
                    'locationUri': 'hdfs://existing',
                    'qualifiedName': 'scb:::dp:::existing_db'
                }
            }
        }

        _create_entity_in_atlas(mock_atlas_client, entity_data)
        mock_atlas_client.entity.create_entity.assert_called_once()

    def test_create_entity_in_atlas_with_guid_assignments(self, mock_atlas_client):
        """Test _create_entity_in_atlas with guidAssignments response."""
        mock_response = Mock()
        mock_response.mutatedEntities = None
        mock_response.guidAssignments = {
            'temp-guid-1': 'actual-guid-123'
        }
        mock_atlas_client.entity.create_entity.return_value = mock_response

        entity_data = {
            'entity': {
                'typeName': 'SCB_Table',
                'attributes': {
                    'table_name': 'new_table',
                    'qualifiedName': 'scb:::dp:::db.table'
                }
            }
        }

        _create_entity_in_atlas(mock_atlas_client, entity_data)
        mock_atlas_client.entity.create_entity.assert_called_once()

    def test_create_entity_handles_error(self, mock_atlas_client):
        """Test entity creation error handling."""
        mock_atlas_client.entity.create_entity.side_effect = Exception("Connection failed")

        entity_data = {
            'entity': {
                'typeName': 'SCB_Database',
                'attributes': {
                    'database_name': 'test_db',
                    'locationUri': 'hdfs://test',
                    'qualifiedName': 'scb:::dp:::test_db'
                }
            }
        }

        with pytest.raises(EntityCreationError):
            _create_entity_in_atlas(mock_atlas_client, entity_data)


class TestEntityServiceFunctionChaining:
    """Tests for creating multiple related entities."""

    @pytest.fixture
    def mock_atlas_client(self):
        """Create a mock Atlas client."""
        client = Mock()
        client.entity = Mock()
        return client

    def test_create_database_and_table(self, mock_atlas_client):
        """Test creating database followed by table."""
        mock_response = Mock()
        mock_response.mutatedEntities = {'CREATE': [Mock(guid='guid-123')]}
        mock_atlas_client.entity.create_entity.return_value = mock_response

        database = DatabaseModel(
            database_name="mydb",
            location_uri="hdfs://mydb"
        )
        # Create database
        result1 = create_database_from_model(
            mock_atlas_client,
            database
        )

        # Create table
        table = TableModel(
            table_name="mytable",
            database_name="mydb"
        )
        result2 = create_table_from_model(
            mock_atlas_client,
            table
        )

        assert result1 == True
        assert result2 == True
        assert mock_atlas_client.entity.create_entity.call_count == 2

    def test_create_table_with_multiple_columns(self, mock_atlas_client):
        """Test creating table followed by multiple columns."""
        mock_response = Mock()
        mock_response.mutatedEntities = {'CREATE': [Mock(guid='guid-auto')]}
        mock_atlas_client.entity.create_entity.return_value = mock_response

        table = TableModel(
            table_name="users",
            database_name="main_db"
        )

        # Create table
        table_result = create_table_from_model(
            mock_atlas_client,
            table
        )

        # Create columns
        columns = [
            ("user_id", "bigint", "User identifier"),
            ("name", "string", "User name"),
            ("email", "string", "User email"),
            ("created_at", "timestamp", "Creation time")
        ]

        for col_name, col_type, col_comment in columns:
            col = StandardColumnModel(
                field_name=col_name,
                data_type=col_type,
                table_name="main_db.users",
                description=col_comment,
            )
            col_result = create_column_from_model(
                mock_atlas_client,
                col
            )
            assert col_result == True

        # Should have 1 table + 4 columns = 5 create calls
        assert mock_atlas_client.entity.create_entity.call_count == 5

    def test_create_complete_data_flow(self, mock_atlas_client):
        """Test creating complete data flow: db -> tables -> columns -> process."""
        mock_response = Mock()
        mock_response.mutatedEntities = {'CREATE': [Mock(guid='guid-auto')]}
        mock_atlas_client.entity.create_entity.return_value = mock_response

        # Database

        create_database_from_model(mock_atlas_client, DatabaseModel(
                database_name="analytics_db",
                location_uri="hdfs://analytics"
        ))

        # Source table
        create_table_from_model(mock_atlas_client, TableModel(
            table_name="raw_data",
            database_name="analytics_db"
        ))
        create_column_from_model(mock_atlas_client, StandardColumnModel(
            field_name="id",
            data_type="bigint",
            table_name="analytics_db.raw_data"
        ))
        create_column_from_model(mock_atlas_client, StandardColumnModel(
            field_name="value",
            data_type="double",
            table_name="analytics_db.raw_data"
        ))
        create_column_from_model(mock_atlas_client, StandardColumnModel(
            field_name="date",
            data_type="date",
            table_name="analytics_db.raw_data"
        ))
        create_column_from_model(mock_atlas_client, StandardColumnModel(
            field_name="total",
            data_type="double",
            table_name="analytics_db.raw_data"
        ))

        # Result table
        create_table_from_model(mock_atlas_client, TableModel(
            table_name="aggregated",
            database_name="analytics_db"
        ))
        create_column_from_model(mock_atlas_client, StandardColumnModel(
            field_name="date",
            data_type="date",
            table_name="analytics_db.aggregated"
        ))
        create_column_from_model(mock_atlas_client, StandardColumnModel(
            field_name="total",
            data_type="double",
            table_name="analytics_db.aggregated"
        ))
        
        # Process
        create_process_from_model(
            mock_atlas_client,
            ProcessModel(
                process_name="daily_aggregation",
                query_id="agg_001",
                query_text="query text",
                user_name="etl_pipeline"
        ))

        # Should have: 1 db + 2 tables + 6 columns + 1 process = 8 calls
        assert mock_atlas_client.entity.create_entity.call_count == 10


class TestEntityServiceParameterValidation:
    """Tests for parameter validation in service functions."""

    @pytest.fixture
    def mock_atlas_client(self):
        """Create a mock Atlas client."""
        client = Mock()
        client.entity = Mock()
        client.entity.create_entity.return_value = Mock(
            mutatedEntities={'CREATE': [Mock(guid='guid-123')]}
        )
        return client

    def test_database_entity_with_empty_strings(self, mock_atlas_client):
        """Test database entity rejects empty required database name."""
        with pytest.raises(ValueError, match="name must be a non-empty string"):
            create_database_from_model(
                mock_atlas_client,
                DatabaseModel(database_name="", location_uri="")
            )

        mock_atlas_client.entity.create_entity.assert_not_called()

    def test_table_entity_optional_parameters_none(self, mock_atlas_client):
        """Test table entity with None optional parameters."""
        result = create_table_from_model(
            mock_atlas_client,
            TableModel(
                table_name="test_table",
                database_name=None,
                table_type=None,
                description=None
            )
        )
        assert result == True

    def test_column_entity_optional_parameters_none(self, mock_atlas_client):
        """Test column entity with None optional parameters."""
        result = create_column_from_model(
            mock_atlas_client,
            StandardColumnModel(
                field_name="col",
                data_type="int",
                table_name=None,
                description=None,
            )
        )
        assert result == True

    def test_process_entity_optional_timestamps_none(self, mock_atlas_client):
        """Test process entity with None timestamps."""
        result = create_process_from_model(
            mock_atlas_client,
            ProcessModel(
                process_name="proc",
                query_id="proc_001",
                query_text="SELECT 1",
                user_name=None,
                start_time=None,
                end_time=None
            ))
        assert result == True


class TestBuilderIntegration:
    """Tests for builder integration with service functions."""

    @pytest.fixture
    def mock_atlas_client(self):
        """Create a mock Atlas client."""
        client = Mock()
        client.entity = Mock()
        client.entity.create_entity.return_value = Mock(
            mutatedEntities={'CREATE': [Mock(guid='guid-123')]}
        )
        return client

    def test_builder_output_compatible_with_service(self, mock_atlas_client):
        """Test that builder output works with service functions."""
        from scb_atlas.atlas.entity_builders import DatabaseEntityBuilder

        # Create entity using builder
        builder = DatabaseEntityBuilder("test_db", "hdfs://test")
        builder.set_description("Test database")
        entity = builder.build()

        # Use with service function
        _create_entity_in_atlas(mock_atlas_client, entity)
        mock_atlas_client.entity.create_entity.assert_called_once()

    def test_multiple_builders_generate_unique_qualified_names(self):
        """Test that different builders generate unique qualified names."""
        from scb_atlas.atlas.entity_builders import (
            DatabaseEntityBuilder,
            TableEntityBuilder,
            ColumnEntityBuilder,
            ProcessEntityBuilder
        )

        db_entity = DatabaseEntityBuilder("db1", "hdfs://db1").build()
        tbl_entity = TableEntityBuilder("tbl1", "db1").build()
        col_entity = ColumnEntityBuilder("col1", "string", "db1.tbl1").build()
        proc_entity = ProcessEntityBuilder("proc1", "proc_001", "SELECT 1").build()

        qnames = [
            db_entity['entity']['attributes']['qualifiedName'],
            tbl_entity['entity']['attributes']['qualifiedName'],
            col_entity['entity']['attributes']['qualifiedName'],
            proc_entity['entity']['attributes']['qualifiedName']
        ]

        # All should be unique
        assert len(set(qnames)) == 4


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

