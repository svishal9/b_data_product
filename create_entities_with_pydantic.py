#!/usr/bin/env python3
"""
Example script showing how to use Pydantic models for creating Atlas entities.

This demonstrates the recommended approach using Pydantic models defined in metadata_models.
"""
from typing import Any, cast
import sys
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from scb_atlas.atlas.atlas_client import create_atlas_client
from scb_atlas.atlas.service import create_typedef
from scb_atlas.atlas.atlas_type_def import all_types
from scb_atlas.atlas.service import (
    create_database_from_model,
    create_table_from_model,
    create_column_from_model,
    create_process_from_model,
    create_data_product_from_model,
)
from scb_atlas.atlas.metadata_models import (
    DatabaseModel,
    TableModel,
    ColumnModel,
    ProcessModel,
    CompleteDataProductModel,
    DataProductBasicMetadata,
    DataProductBusinessMetadata,
    DataProductClassification,
    DataProductPorts,
    DataProductUsage,
    DataProductLifecycle,
    DataProductGovernanceMetadata,
    LifecycleStatusEnum,
    RefreshCutEnum,
    RefreshFrequencyEnum,
    SensitivityEnum,
)


def print_header(title):
    """Print formatted header."""
    print("\n" + "="*80)
    print(f"▶ {title}")
    print("="*80 + "\n")


def main():
    """Create sample entities using Pydantic models."""
    
    print_header("SCB Atlas - Entity Creation Using Pydantic Models")
    
    # Connect to Atlas
    print_header("Step 1: Connecting to Atlas")
    atlas_client = create_atlas_client()
    print("✅ Connected to Atlas successfully!")
    
    # Create types (if not already present)
    print_header("Step 2: Creating Type Definitions")
    try:
        result = create_typedef(all_types, atlas_client)
        print("✅ Type definitions ready!")
    except Exception as e:
        print(f"⚠️  Type creation info: {e}")
    
    # Create Database using Pydantic model
    print_header("Step 3: Creating Database")
    database_model = DatabaseModel(
        database_name="finance_db",
        location_uri="hdfs://data/finance",
        create_time=datetime(2026, 3, 24, 0, 0).astimezone(None),
        description="Finance database containing trading and transaction data"
    )
    
    create_database_from_model(atlas_client, database_model)
    print(f"✅ Database created: {database_model.database_name}")
    print(f"   Qualified Name: {database_model.qualified_name}")
    
    # Create Table using Pydantic model
    print_header("Step 4: Creating Tables")
    tables_data = [
        {
            "table_name": "trades",
            "database_name": "finance_db",
            "description": "FX and derivatives trading transactions",
            "table_type": "EXTERNAL",
            "create_time": datetime(2026, 3, 24).astimezone(),
        },
        {
            "table_name": "transactions",
            "database_name": "finance_db",
            "description": "Financial transactions",
            "table_type": "MANAGED",
            "create_time": datetime(2026, 3, 24).astimezone(),
        },
        {
            "table_name": "daily_summary",
            "database_name": "finance_db",
            "description": "Daily trade summaries",
            "create_time": datetime(2026, 3, 24).astimezone(),
        },
    ]
    
    for table_data in tables_data:
        table_model = TableModel(**table_data)
        create_table_from_model(
            atlas_client,
            table_model,
            database_qualified_name=database_model.qualified_name
        )
        print(f"✅ Table created: {table_model.table_name}")
        print(f"   Qualified Name: {table_model.qualified_name}")
    
    # Create Columns using Pydantic model
    print_header("Step 5: Creating Columns")
    columns_data = [
        {
            "column_name": "trade_id",
            "data_type": "string",
            "description": "Unique trade identifier",
            "table_name": "trades",
            "database_name": "finance_db",
            "position": 1,
        },
        {
            "column_name": "trade_date",
            "data_type": "date",
            "description": "Date of the trade",
            "table_name": "trades",
            "database_name": "finance_db",
            "position": 2,
        },
        {
            "column_name": "amount",
            "data_type": "decimal(18,2)",
            "description": "Trade amount",
            "table_name": "trades",
            "database_name": "finance_db",
            "position": 3,
        },
    ]
    
    for col_data in columns_data:
        column_model = ColumnModel(**col_data)
        table_qname = f"scb:::dp:::finance_db.trades"
        create_column_from_model(
            atlas_client,
            column_model,
            table_qualified_name=table_qname
        )
        print(f"✅ Column created: {column_model.column_name} ({column_model.data_type})")
        print(f"   Qualified Name: {column_model.qualified_name}")
    
    # Create Process using Pydantic model
    print_header("Step 6: Creating Process")
    process_model = ProcessModel(
        process_name="daily_trade_aggregation",
        query_id="proc_daily_agg_001",
        query_text="Daily aggregation from finance_db.trades to finance_db.daily_summary",
        user_name="data_pipeline",
        start_time=1774338243657,
        end_time=1774341843657,
    )
    
    create_process_from_model(
        atlas_client,
        process_model,
        input_refs=[("SCB_Table", "scb:::dp:::finance_db.trades")],
        output_refs=[("SCB_Table", "scb:::dp:::finance_db.daily_summary")],
    )
    print(f"✅ Process created: {process_model.process_name}")
    print(f"   Query ID: {process_model.query_id}")
    
    # Create Data Product using Pydantic model
    print_header("Step 7: Creating Data Product")
    
    dp_model = CompleteDataProductModel(
        basic_metadata=DataProductBasicMetadata(
            data_product_name="Finance Trading Data Product",
            description="Comprehensive data product for trading and transaction data",
            data_product_category="Source-Aligned"
        ),
        business_metadata=DataProductBusinessMetadata(
            business_purpose="Source Aligned DP Finance",
            gcfo_owner_name="Jane Smith",
            gcfo_owner_contact="jane.smith@company.com"
        ),
        classification=DataProductClassification(
            sensitivity=SensitivityEnum.SENSITITY_INTERNAL,
            personal=False,
            geo_location_access=["EU", "Singapore", "UK"],
            regulatory_flags=["BCBS239", "MAS TRM"],
            certifications=["Attested by GCFO"],
            approval="Approved for Enterprise Use"
        ),
        ports=DataProductPorts(
            data_product_input_ports=["scb:::dp:::finance_db.trades", "scb:::dp:::finance_db.transactions"],
            data_product_output_port="scb:::dp:::finance_db.daily_summary",
            delivery_channels=["REST API", "PowerBI"],
            data_landing_pattern="API - FDP Staging Table",
            data_handshake="http://example.com/api/handshake"
        ),
        usage=DataProductUsage(
            users=["Finance Analysts", "Risk Team"],
            systems=5,
            usecases=["Accounting", "Capital", "Liquidity"]
        ),
        lifecycle=DataProductLifecycle(
            version="1.0",
            environment="Production",
            lifecycle_status=LifecycleStatusEnum.PUBLISH_CONSUME,
            delivery_date=datetime(2026, 2, 1, 0, 0, 0)
        ),
        governance_metadata=DataProductGovernanceMetadata(
            domain="FM",
            sub_domain="FX",
            refresh_frequency="Daily (T+0)",
            refresh_cut=RefreshCutEnum.ACTUAL_CUT,
            last_refreshed=datetime(2026, 3, 24, 12, 0, 0,0),
            data_product_owner="John Doe",
            data_product_owner_contact_information="john.doe@company.com",
            domain_owner="FM Domain Owner",
            domain_owner_contact_information="fm-owners@company.com",
            data_steward="Alice Johnson",
            data_steward_contact_information="alice.johnson@company.com",
            support_contact="Support Team",
            support_contact_information="support@company.com",
            data_retention="3 years",
            sla=cast(Any, ["99.9% availability"]),
            communication_channel=["Slack: #data-products", "Teams: #data-products"],
            data_quality_score="95%",
            resolution_sla="<4 hours",
            completeness="99%",
        )
   
    )
    
    create_data_product_from_model(
        atlas_client,
        dp_model,
        input_port_qualified_names=["scb:::dp:::finance_db.trades", "scb:::dp:::finance_db.transactions"],
        output_port_qualified_name="scb:::dp:::finance_db.daily_summary"
    )
    print(f"✅ Data Product created: {dp_model.basic_metadata.data_product_name}")
    print(f"   Qualified Name: {dp_model.qualified_name}")
    
    print_header("Setup Complete!")
    print("✅ All entities created successfully using Pydantic models!")
    print("\n📊 Created Entities Summary:")
    print("  - Database: finance_db")
    print("  - Tables: trades, transactions, daily_summary")
    print("  - Columns: trade_id, trade_date, amount")
    print("  - Process: daily_trade_aggregation")
    print("  - Data Product: Finance Trading Data Product")
    print("\n🌐 Access Atlas UI at: http://localhost:23000")
    print("   Username: admin")
    print("   Password: admin")


if __name__ == "__main__":
    # Backward-compatible wrapper: keep old entry point working via unified CLI.
    print(
        "[DEPRECATED] `create_entities_with_pydantic.py` is deprecated. "
        "Use `scb_dp_cli.py sample-entities` (or `scb sample-entities`)."
    )
    from scb_dp_cli import main as scb_main

    raise SystemExit(scb_main(["sample-entities", *sys.argv[1:]]))
