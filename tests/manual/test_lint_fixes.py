#!/usr/bin/env python
"""Test script to verify all lint fixes are working correctly."""

from scb_atlas.atlas.entity_builders import (
    convert_to_atlas_model,
    DatabaseEntityBuilder,
    TableEntityBuilder,
    ColumnEntityBuilder,
    ProcessEntityBuilder,
)

def test_builders():
    """Test entity builders work without type errors."""
    print("Testing DatabaseEntityBuilder...")
    db = DatabaseEntityBuilder("test_db", "hdfs://test")
    db_entity = db.build()
    assert db_entity['entity']['typeName'] == 'SCB_Database'
    assert 'createTime' in db_entity['entity']['attributes']
    assert isinstance(db_entity['entity']['attributes']['createTime'], str)
    print("  ✓ DatabaseEntityBuilder works correctly")
    
    print("Testing TableEntityBuilder...")
    tbl = TableEntityBuilder("test_table", "test_db")
    tbl_entity = tbl.build()
    assert tbl_entity['entity']['typeName'] == 'SCB_Table'
    assert 'createTime' in tbl_entity['entity']['attributes']
    assert isinstance(tbl_entity['entity']['attributes']['createTime'], str)
    print("  ✓ TableEntityBuilder works correctly")
    
    print("Testing ColumnEntityBuilder...")
    col = ColumnEntityBuilder("test_col", "string", "test_table")
    col.set_position(1)
    col_entity = col.build()
    assert col_entity['entity']['typeName'] == 'SCB_Column'
    assert col_entity['entity']['attributes']['position'] == 1
    print("  ✓ ColumnEntityBuilder works correctly")
    
    print("Testing ProcessEntityBuilder...")
    proc = ProcessEntityBuilder("test_process", "query_1", "sample lineage query")
    proc.add_input_entity("SCB_Table", "source_table")
    proc.add_output_entity("SCB_Table", "output_table")
    proc_entity = proc.build()
    assert proc_entity['entity']['typeName'] == 'SCB_Process'
    assert 'inputs' in proc_entity['entity']['attributes']
    assert isinstance(proc_entity['entity']['attributes']['inputs'], list)
    assert len(proc_entity['entity']['attributes']['inputs']) == 1
    assert 'outputs' in proc_entity['entity']['attributes']
    assert isinstance(proc_entity['entity']['attributes']['outputs'], list)
    assert len(proc_entity['entity']['attributes']['outputs']) == 1
    print("  ✓ ProcessEntityBuilder works correctly")

def test_convert_to_atlas_model():
    """Test convert_to_atlas_model function."""
    print("Testing convert_to_atlas_model...")
    test_data = {
        "Data Product Name": "Finance DP",
        "Description": "Test Data Product",
        "Business Purpose": "Financial Analytics",
        "GCFO Owner": "John Doe",
        "Support Contact": "support@company.com",
        "Sensitivity": "Internal",
        "Personal": "No",
        "Lifecycle Status": "Production",
        "Domain": "Finance",
        "Sub-Domain": "Trading",
        "Data Steward": "Jane Smith",
        "Source Domain Owner": "Bob Wilson",
        "Version": "1.0",
        "Refresh Frequency": "Daily (T+0)",
        "Data Retention": "3 years",
        "Users": "2500",
        "Systems": "5",
        "Usecases": "Accounting,Capital,Liquidity",
    }
    
    result = convert_to_atlas_model(test_data)
    assert result.basic_metadata.data_product_name == "Finance DP"
    assert result.governance_metadata.domain == "Finance"
    assert result.lifecycle is not None
    assert result.lifecycle.environment == "Production"
    assert result.lifecycle.lifecycle_status.value == "Publish & Consume"
    print("  ✓ convert_to_atlas_model works correctly")

if __name__ == "__main__":
    print("Running lint fix tests...\n")
    test_builders()
    print()
    test_convert_to_atlas_model()
    print("\n✅ All tests passed!")

