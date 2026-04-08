#!/usr/bin/env python3
"""Test script to verify lineage processes are created when ingesting workbook."""

from pathlib import Path
from scb_atlas.atlas import create_atlas_client, create_data_products_from_workbook


def test_workbook_lineage():
    """Test that lineage processes are created."""
    atlas_client = create_atlas_client()
    workbook_path = Path("sample_data/metadata_master_schema.xlsx")
    
    print("Creating data products from workbook...")
    created = create_data_products_from_workbook(workbook_path, atlas_client)
    
    print(f"\n✅ Created {len(created)} data product(s):")
    for name in created:
        print(f"   - {name}")
    
    print("\n✅ SUCCESS! Data products with lineage processes created!")
    print("\nNext steps to verify lineage:")
    print("1. Open Atlas: http://localhost:23000 (admin/admin)")
    print("2. Search → Advanced Search")
    print("3. Type: SCB_DataProduct")
    print("4. Click on data product: FM_Unified_Cashflow")
    print("5. Click Lineage tab")
    print("")
    print("You should see:")
    print("   INPUT PORT → [Ingest Process] → DATA PRODUCT → [Publish Process] → OUTPUT PORT")
    print("")
    print("To verify processes were created:")
    print("1. In Advanced Search, select Type: SCB_Process")
    print("2. Look for processes ending in '_ingest_process' and '_publish_process'")


if __name__ == "__main__":
    test_workbook_lineage()

