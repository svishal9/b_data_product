from pathlib import Path
from unittest import TestCase
from unittest.mock import Mock, patch

import pandas as pd


from scb_atlas.atlas.metadata_models import SensitivityEnum

from scb_atlas.atlas.read_data_product import (
    create_data_products_from_workbook,
    parse_master_schema_workbook_to_data_products,
    validate_metadata_workbook,
)


def test_validate_metadata_workbook(sample_master_workbook_data_path: Path):
    assert validate_metadata_workbook(sample_master_workbook_data_path) is True
    assert validate_metadata_workbook(sample_master_workbook_data_path, strict=True) is True


def test_parse_workbook_maps_to_pydantic_models(sample_master_workbook_data_path: Path):
    #models = parse_workbook_to_data_products(sample_master_workbook_data_path)
    models = parse_master_schema_workbook_to_data_products(sample_master_workbook_data_path)

    assert len(models) >= 1
    model = models[1]
    assert model.basic_metadata.data_product_name == "FM_Unified_Cashflow"
    assert model.basic_metadata.data_product_category == "Source-Aligned"
    assert model.basic_metadata.granularity == "Incremental"
    assert model.governance_metadata.domain == "FM"
    assert model.governance_metadata.refresh_frequency == "Daily (T+0)"
    assert model.classification is not None
    assert model.classification.sensitivity == SensitivityEnum.SENSITITY_INTERNAL
    assert model.output_port_schema is not None
    assert len(model.output_port_schema) > 0
    assert model.output_port_schema[0].field_name == "cashflow_id"


@patch("scb_atlas.atlas.read_data_product.create_data_product_from_model")
@patch("scb_atlas.atlas.read_data_product._ensure_port_database")
@patch("scb_atlas.atlas.read_data_product._create_input_port_assets")
@patch("scb_atlas.atlas.read_data_product._create_output_port_assets")
@patch("scb_atlas.atlas.read_data_product._create_lineage_processes")
def test_create_data_products_from_workbook_creates_entities(
    mocked_create_lineage_process,
    mocked_create_output_port_assets, 
    mocked_create_input_port_assets, 
    mocked_ensure_port_database, 
    mocked_create, 
    sample_master_workbook_data_path: Path
):
    
    atlas_client = Mock()
    mocked_create_lineage_process.return_value = "Done"
    mocked_create_output_port_assets.return_value = "some-output-port-guid"
    mocked_create_input_port_assets.return_value = None
    mocked_ensure_port_database.return_value = True
    mocked_create.return_value = True

    created = create_data_products_from_workbook(sample_master_workbook_data_path, atlas_client)

    assert len(created) >= 1
    assert "FM_Unified_Cashflow" in created
    mocked_create.call_count == len(created)


@patch("scb_atlas.atlas.read_data_product.create_data_product_from_model")
@patch("scb_atlas.atlas.read_data_product._ensure_port_database")
@patch("scb_atlas.atlas.read_data_product._create_input_port_assets")
@patch("scb_atlas.atlas.read_data_product._create_output_port_assets")
@patch("scb_atlas.atlas.read_data_product._create_lineage_processes")
def test_create_data_products_from_workbook_strict_creates_entities(
    mocked_create_lineage_process,
    mocked_create_output_port_assets, 
    mocked_create_input_port_assets, 
    mocked_ensure_port_database, 
    mocked_create, 
    sample_master_workbook_data_path: Path
):
    atlas_client = Mock()
    mocked_create_lineage_process.return_value = "Done"
    mocked_create_output_port_assets.return_value = "some-output-port-guid"
    mocked_create_input_port_assets.return_value = None
    mocked_ensure_port_database.return_value = True
    mocked_create.return_value = True

    created = create_data_products_from_workbook(sample_master_workbook_data_path, atlas_client, strict=True)

    assert len(created) >= 1
    mocked_create.call_count == len(created)


def test_validate_metadata_workbook_rejects_missing_data_product_sheet(tmp_path: Path):
    file_path = tmp_path / "invalid.xlsx"
    print(tmp_path)
    pd.DataFrame({"a": [1]}).to_excel(file_path, sheet_name="Wrong Sheet", index=False)

    try:
        validate_metadata_workbook(file_path)
        assert False, "Expected ValueError for missing Data Product sheet"
    except ValueError as exc:
        assert "Data Product" in str(exc)


def test_validate_metadata_workbook_strict_rejects_missing_product_sheet(tmp_path: Path):
    workbook = tmp_path / "missing_product_sheet.xlsx"
    rows = [
        [None, "Data Product Name", "Description", "Domain", "Sub-Domain", "Data Product Category"],
        [None, "DP_ONE", "desc", "FM", "FX", "Source Aligned"],
    ]
    schema_row = [
        [None, "Data Product", "ID", "Category", "Attribute Name", "Source of Attribute", "Column Name", "Data Type"],
        [None, "Wrong DP", "1", "Some Category", "Some Identifier", "m", "some-id", "string"],
    ]
    with pd.ExcelWriter(workbook) as writer:
        pd.DataFrame(rows).to_excel(writer, sheet_name="Data Product", index=False, header=False)
        pd.DataFrame(schema_row).to_excel(writer, sheet_name="Master Schema", index=False, header=False)
    try:
        validate_metadata_workbook(workbook, strict=True)
        assert False, "Expected strict mode to fail when per-product sheet is missing"
    except ValueError as exc:
        assert "Missing schema definition for data product 'DP_ONE'" in str(exc)


def test_validate_metadata_workbook_strict_rejects_schema_header_mismatch(tmp_path: Path):
    workbook = tmp_path / "bad_schema_header.xlsx"
    rows = [
        [None, "Data Product Name", "Description", "Domain", "Sub-Domain", "Data Product Category"],
        [None, "DP_ONE", "desc", "FM", "FX", "Source Aligned"],
    ]
    # Missing required schema headers 'Field Name' and 'Data Type'.
    bad_schema_rows = [[None, "Category", "Col", "TypeX"], [None, "X", "id", "string"]]
    with pd.ExcelWriter(workbook) as writer:
        pd.DataFrame(rows).to_excel(writer, sheet_name="Data Product", index=False, header=False)
        pd.DataFrame(bad_schema_rows).to_excel(writer, sheet_name="Master Schema", index=False, header=False)

    try:
        parse_master_schema_workbook_to_data_products(workbook, strict=True)
        assert False, "Expected strict mode to fail when schema header is missing"
    except ValueError as exc:
        assert "must contain a header row" in str(exc)

def test_read_master_schema_worksheet_from_workbook(sample_master_workbook_data_path: Path):
    
    products = parse_master_schema_workbook_to_data_products(sample_master_workbook_data_path)
    assert products is not None
    assert len(products) == 2
    
    assert products[0].basic_metadata.data_product_name == "FM_FX_Linear_Trade"
    assert products[1].basic_metadata.data_product_name == "FM_Unified_Cashflow"