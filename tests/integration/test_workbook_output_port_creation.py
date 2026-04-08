from pathlib import Path

from unittest import TestCase
from scb_atlas.atlas.read_data_product import (
    _derive_output_port_table_name,
    create_data_products_from_workbook,
    parse_master_schema_workbook_to_data_products
)


def test_derive_output_port_table_name_from_model(sample_master_workbook_data_path):
    workbook = Path(sample_master_workbook_data_path)
    model = parse_master_schema_workbook_to_data_products(workbook)[1]

    table_name = _derive_output_port_table_name(model)

    assert table_name.endswith("_output_port")
    assert "fm_unified_cashflow" in table_name


def test_create_data_products_creates_output_table_and_columns(monkeypatch, sample_master_workbook_data_path):
    workbook = Path(sample_master_workbook_data_path)

    calls = {
        "database": [],
        "table": [],
        "column": [],
        "dp": [],
    }

    def fake_create_database(client, database_model):
        calls["database"].append(database_model)
        return True

    def fake_create_table(client, table_model, database_qualified_name=None):
        calls["table"].append((table_model, database_qualified_name))
        return True

    def fake_create_column(client, column_model, table_qualified_name=None):
        calls["column"].append((column_model, table_qualified_name))
        return True

    def fake_create_dp(client, model, input_port_qualified_names=None, output_port_qualified_name=None):
        calls["dp"].append((model, input_port_qualified_names, output_port_qualified_name))
        return True

    monkeypatch.setattr("scb_atlas.atlas.read_data_product.create_database_from_model", fake_create_database)
    monkeypatch.setattr("scb_atlas.atlas.read_data_product.create_table_from_model", fake_create_table)
    monkeypatch.setattr("scb_atlas.atlas.read_data_product.create_column_from_model", fake_create_column)
    monkeypatch.setattr("scb_atlas.atlas.read_data_product.create_data_product_from_model", fake_create_dp)
    monkeypatch.setattr("scb_atlas.atlas.read_data_product._create_lineage_processes", lambda *args, ** kwargs: True)

    created = create_data_products_from_workbook(workbook, atlas_client=object())

    TestCase.assertListEqual(TestCase(), created, ["FM_FX_Linear_Trade", "FM_Unified_Cashflow"])
    assert len(calls["database"]) == 4
    assert len(calls["table"]) == 9
    assert len(calls["column"]) == 6
    assert len(calls["dp"]) == 2

    output_table_model = calls["table"][-1][0]
    _, input_port_qns, output_port_qn = calls["dp"][1]
    assert output_port_qn == output_table_model.qualified_name
    assert isinstance(input_port_qns, list)
    assert len(input_port_qns) == 4

    first_column_model, first_table_qn = calls["column"][4]
    assert first_table_qn == output_table_model.qualified_name
    assert first_column_model.table_name == output_table_model.table_name


def test_create_data_products_without_input_ports(monkeypatch, sample_master_workbook_data_path):
    workbook = Path(sample_master_workbook_data_path)
    model = parse_master_schema_workbook_to_data_products(workbook)[0]
    model = model.model_copy(
        update={"ports": model.ports.model_copy(update={"data_product_input_ports": None})}
    )

    monkeypatch.setattr(
        "scb_atlas.atlas.read_data_product.parse_master_schema_workbook_to_data_products",
        lambda *_args, **_kwargs: [model],
    )

    calls = {"dp": []}

    monkeypatch.setattr("scb_atlas.atlas.read_data_product.create_database_from_model", lambda *_args, **_kwargs: True)
    monkeypatch.setattr("scb_atlas.atlas.read_data_product.create_table_from_model", lambda *_args, **_kwargs: True)
    monkeypatch.setattr("scb_atlas.atlas.read_data_product.create_column_from_model", lambda *_args, **_kwargs: True)
    monkeypatch.setattr("scb_atlas.atlas.read_data_product._create_lineage_processes", lambda *args, ** kwargs: True)

    def fake_create_dp(client, model, input_port_qualified_names=None, output_port_qualified_name=None):
        calls["dp"].append((input_port_qualified_names, output_port_qualified_name))
        return True

    monkeypatch.setattr("scb_atlas.atlas.read_data_product.create_data_product_from_model", fake_create_dp)

    create_data_products_from_workbook(workbook, atlas_client=object())

    assert len(calls["dp"]) == 1
    input_qns, output_qn = calls["dp"][0]
    assert input_qns is None
    assert output_qn is not None




