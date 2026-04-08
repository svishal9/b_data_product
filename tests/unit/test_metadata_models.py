# noinspection PyArgumentList,SqlNoDataSourceInspection
#!/usr/bin/env python3
# pyright: reportCallIssue=false
"""
Test suite for Pydantic entity models.

Tests validation and conversion to Atlas entities.
"""

from datetime import datetime

import pytest
from pydantic import ValidationError

from scb_atlas.atlas.metadata_models import (
    DatabaseModel,
    TableModel,
    StandardColumnModel,
    ProcessModel,
    CompleteDataProductModel,
    DataProductBasicMetadata,
    DataProductGovernanceMetadata,
    DataProductPorts,
    # DataProductSchemaField,
    TableTypeEnum,
    PIIEnum,
    LifecycleStatusEnum,
)


class TestDatabaseModel:
    """Tests for DatabaseModel."""
    
    def test_create_database_with_required_fields(self):
        """Test creating database with required fields."""
        db = DatabaseModel(
            database_name="finance_db",
            location_uri="hdfs://data/finance"
        )
        assert db.database_name == "finance_db"
        assert db.location_uri == "hdfs://data/finance"
        assert db.qualified_name == "scb:::dp:::finance_db"
    
    def test_create_database_with_all_fields(self):
        """Test creating database with all fields."""
        db = DatabaseModel(
            database_name="finance_db",
            location_uri="hdfs://data/finance",
            create_time=datetime(2026, 3, 24, 0, 0, 0),
            description="Finance database"
        )
        assert db.description == "Finance database"
        assert db.create_time == datetime(2026, 3, 24, 0, 0, 0)
    
    def test_database_missing_required_field(self):
        """Test that missing required field raises ValidationError."""
        with pytest.raises(ValidationError):
            DatabaseModel(location_uri="hdfs://data/finance")
    
    def test_database_to_atlas_entity(self):
        """Test conversion to Atlas entity."""
        db = DatabaseModel(
            database_name="finance_db",
            location_uri="hdfs://data/finance",
            description="Finance database"
        )
        entity = db.to_atlas_entity()
        
        assert entity["typeName"] == "SCB_Database"
        assert entity["attributes"]["database_name"] == "finance_db"
        assert entity["attributes"]["locationUri"] == "hdfs://data/finance"
        assert entity["attributes"]["description"] == "Finance database"


class TestTableModel:
    """Tests for TableModel."""
    
    def test_create_table_with_required_fields(self):
        """Test creating table with required fields."""
        table = TableModel(table_name="trades")
        assert table.table_name == "trades"
        assert table.qualified_name == "scb:::dp:::trades"
    
    def test_create_table_with_database_name(self):
        """Test creating table with database name."""
        table = TableModel(
            table_name="trades",
            database_name="finance_db"
        )
        assert table.qualified_name == "scb:::dp:::finance_db.trades"
    
    def test_create_table_with_enum(self):
        """Test creating table with table type enum."""
        table = TableModel(
            table_name="trades",
            table_type=TableTypeEnum.EXTERNAL
        )
        entity = table.to_atlas_entity()
        assert entity["attributes"]["tableType"] == "EXTERNAL"
    
    def test_table_to_atlas_entity(self):
        """Test conversion to Atlas entity."""
        table = TableModel(
            table_name="trades",
            database_name="finance_db",
            description="Trade data",
            table_type=TableTypeEnum.EXTERNAL
        )
        entity = table.to_atlas_entity()
        
        assert entity["typeName"] == "SCB_Table"
        assert entity["attributes"]["table_name"] == "trades"
        assert entity["attributes"]["tableType"] == "EXTERNAL"


class TestColumnModel:
    """Tests for ColumnModel."""
    
    def test_create_column_with_required_fields(self):
        """Test creating column with required fields."""
        col = StandardColumnModel(
            field_name="trade_id",
            data_type="string"
        )
        assert col.field_name == "trade_id"
        assert col.data_type == "string"
    
    def test_create_column_with_full_qualified_name(self):
        """Test creating column with full qualified name."""
        col = StandardColumnModel(
            field_name="trade_id",
            data_type="string",
            table_name="trades",
            database_name="finance_db"
        )
        assert col.qualified_name == "scb:::dp:::finance_db.trades.trade_id"
    
    
    def test_column_to_atlas_entity(self):
        """Test conversion to Atlas entity."""
        col = StandardColumnModel(
            field_name="trade_id",
            data_type="string",
            description="Unique trade identifier",
        )
        entity = col.to_atlas_entity()
        
        assert entity["typeName"] == "SCB_Column"
        assert entity["attributes"]["field_name"] == "trade_id"
        assert entity["attributes"]["data_type"] == "string"
        assert entity["attributes"]["description"] == "Unique trade identifier"


class TestProcessModel:
    """Tests for ProcessModel."""
    
    def test_create_process_with_required_fields(self):
        """Test creating process with required fields."""
        proc = ProcessModel(
            process_name="daily_aggregation",
            query_id="proc_001",
            query_text="query text"
        )
        assert proc.process_name == "daily_aggregation"
        assert proc.query_id == "proc_001"
    
    def test_process_qualified_name(self):
        """Test process qualified name generation."""
        proc = ProcessModel(
            process_name="daily_aggregation",
            query_id="proc_001",
            query_text="query text"
        )
        assert proc.qualified_name == "scb:::dp:::proc_proc_001"
    
    def test_process_to_atlas_entity(self):
        """Test conversion to Atlas entity."""
        proc = ProcessModel(
            process_name="daily_aggregation",
            query_id="proc_001",
            query_text="query text",
            user_name="data_pipeline"
        )
        entity = proc.to_atlas_entity()
        
        assert entity["typeName"] == "SCB_Process"
        assert entity["attributes"]["process_name"] == "daily_aggregation"
        assert entity["attributes"]["queryId"] == "proc_001"
        assert entity["attributes"]["userName"] == "data_pipeline"


class TestCompleteDataProductModel:
    """Tests for CompleteDataProductModel."""
    
    def test_create_data_product_minimal(self):
        """Test creating data product with minimal fields."""
        dp = CompleteDataProductModel(
            basic_metadata=DataProductBasicMetadata(
                data_product_name="Finance DP"
            ),
            governance_metadata=DataProductGovernanceMetadata(
                domain="FM"
            )
        )
        assert dp.basic_metadata.data_product_name == "Finance DP"
        assert dp.governance_metadata.domain == "FM"
        assert dp.qualified_name == "scb:::dp:::finance_dp"
    
    def test_data_product_to_atlas_entity(self):
        """Test conversion to Atlas entity."""
        dp = CompleteDataProductModel(
            basic_metadata=DataProductBasicMetadata(
                data_product_name="Finance DP",
                description="Finance data product",
                data_product_category="Source-Aligned"
            ),
            governance_metadata=DataProductGovernanceMetadata(
                domain="FM",
                sub_domain="FX"
            )
        )
        entity = dp.to_atlas_entity()
        
        assert entity["typeName"] == "SCB_DataProduct"
        assert entity["attributes"]["data_product_name"] == "Finance DP"
        assert entity["attributes"]["description"] == "Finance data product"

    def test_data_product_ports_are_emitted_as_array(self):
        """Atlas expects data_access as array<SCB_DataAccess>."""
        dp = CompleteDataProductModel(
            basic_metadata=DataProductBasicMetadata(
                data_product_name="Finance DP",
            ),
            governance_metadata=DataProductGovernanceMetadata(
                domain="FM",
            ),
            ports=DataProductPorts(
                data_landing_pattern="API - FDP Staging Table",
                data_handshake="http://example/handshake",
            ),
        )

        entity = dp.to_atlas_entity()
        data_access = entity["attributes"].get("data_access")

        assert isinstance(data_access, list)
        assert len(data_access) == 1
        assert data_access[0]["typeName"] == "SCB_DataAccess"
        assert data_access[0]["attributes"]["data_landing_pattern"] == "API - FDP Staging Table"


def test_lifecycle_status_enum():
    """Test lifecycle status enum values."""
    assert LifecycleStatusEnum.IDEATE_PROPOSE.value == "Ideate & Propose"
    assert LifecycleStatusEnum.PUBLISH_CONSUME.value == "Publish & Consume"
    assert LifecycleStatusEnum.MONITOR_MAINTAIN.value == "Monitor & Maintain"


def test_table_type_enum():
    """Test table type enum values."""
    assert TableTypeEnum.MANAGED.value == "MANAGED"
    assert TableTypeEnum.EXTERNAL.value == "EXTERNAL"


def test_pii_enum():
    """Test PII enum values."""
    assert PIIEnum.YES.value == "True"
    assert PIIEnum.NO.value == "False"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

