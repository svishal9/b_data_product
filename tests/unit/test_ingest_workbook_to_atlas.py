from __future__ import annotations

import argparse
from pathlib import Path
from types import SimpleNamespace

import ingest_workbook_to_atlas as ingest


def _fake_model(name: str, schema_fields: int = 0):
    return SimpleNamespace(
        basic_metadata=SimpleNamespace(data_product_name=name),
        output_port_schema=[object() for _ in range(schema_fields)],
    )


def test_parse_args_parses_required_and_flags(monkeypatch):
    monkeypatch.setattr(
        "sys.argv",
        [
            "ingest_workbook_to_atlas.py",
            "sample_data/metadata_example.xlsx",
            "--dry-run",
            "--strict",
        ],
    )

    args = ingest.parse_args()

    assert args.workbook == Path("sample_data/metadata_example.xlsx")
    assert args.dry_run is True
    assert args.strict is True


def test_main_returns_1_when_validation_fails(monkeypatch, capsys):
    args = argparse.Namespace(workbook=Path("sample_data/metadata_example.xlsx"), dry_run=False, strict=False)
    monkeypatch.setattr(ingest, "parse_args", lambda: args)
    monkeypatch.setattr(ingest, "validate_metadata_workbook", lambda *_args, **_kwargs: False)

    called = {"parse": False}

    def _parse(*_args, **_kwargs):
        called["parse"] = True
        return []

    monkeypatch.setattr(ingest, "parse_master_schema_workbook_to_data_products", _parse)

    rc = ingest.main()
    out = capsys.readouterr().out

    assert rc == 1
    assert "Workbook validation failed." in out
    assert called["parse"] is False


def test_main_dry_run_prints_models_and_skips_creation(monkeypatch, capsys):
    args = argparse.Namespace(workbook=Path("sample_data/metadata_master_schema.xlsx"), dry_run=True, strict=True)
    monkeypatch.setattr(ingest, "parse_args", lambda: args)
    monkeypatch.setattr(ingest, "validate_metadata_workbook", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(
        ingest,
        "parse_master_schema_workbook_to_data_products",
        lambda *_args, **_kwargs: [_fake_model("DP_A", 2), _fake_model("DP_B", 0)],
    )

    called = {"client": False, "typedef": False, "create": False}

    monkeypatch.setattr(ingest, "create_atlas_client", lambda: called.__setitem__("client", True))
    monkeypatch.setattr(ingest, "create_typedef", lambda *_args, **_kwargs: called.__setitem__("typedef", True))
    monkeypatch.setattr(
        ingest,
        "create_data_products_from_workbook",
        lambda *_args, **_kwargs: called.__setitem__("create", True),
    )

    rc = ingest.main()
    out = capsys.readouterr().out

    assert rc == 0
    assert "Validated workbook. Parsed 2 data product(s)." in out
    assert "- DP_A (schema fields: 2)" in out
    assert "- DP_B (schema fields: 0)" in out
    assert called == {"client": False, "typedef": False, "create": False}
    

def test_main_registers_types_then_creates_entities(monkeypatch, capsys):
    args = argparse.Namespace(workbook=Path("sample_data/metadata_example.xlsx"), dry_run=False, strict=True)
    monkeypatch.setattr(ingest, "parse_args", lambda: args)
    monkeypatch.setattr(ingest, "validate_metadata_workbook", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(ingest, "parse_master_schema_workbook_to_data_products", lambda *_args, **_kwargs: [_fake_model("DP_A", 1)])

    atlas_client = object()
    monkeypatch.setattr(ingest, "create_atlas_client", lambda: atlas_client)

    calls: list[tuple] = []

    def _typedef(type_defs, client):
        calls.append(("typedef", type_defs, client))

    def _create(workbook, client, strict=False):
        calls.append(("create", workbook, client, strict))
        return ["DP_A"]

    monkeypatch.setattr(ingest, "create_typedef", _typedef)
    monkeypatch.setattr(ingest, "create_data_products_from_workbook", _create)

    rc = ingest.main()
    out = capsys.readouterr().out

    assert rc == 0
    assert calls[0] == ("typedef", ingest.all_types, atlas_client)
    assert calls[1] == ("create", args.workbook, atlas_client, True)
    assert "Registering SCB type definitions..." in out
    assert "Type definitions ready." in out
    assert "Created 1 data product entity(ies):" in out
    assert "- DP_A" in out


def test_main_continues_when_type_registration_raises(monkeypatch, capsys):
    args = argparse.Namespace(workbook=Path("sample_data/metadata_example.xlsx"), dry_run=False, strict=False)
    monkeypatch.setattr(ingest, "parse_args", lambda: args)
    monkeypatch.setattr(ingest, "validate_metadata_workbook", lambda *_args, **_kwargs: True)
    monkeypatch.setattr(ingest, "parse_master_schema_workbook_to_data_products", lambda *_args, **_kwargs: [_fake_model("DP_A", 1)])

    atlas_client = object()
    monkeypatch.setattr(ingest, "create_atlas_client", lambda: atlas_client)

    def _typedef(*_args, **_kwargs):
        raise RuntimeError("typedef already exists")

    create_called = {"value": False}

    def _create(*_args, **_kwargs):
        create_called["value"] = True
        return ["DP_A"]

    monkeypatch.setattr(ingest, "create_typedef", _typedef)
    monkeypatch.setattr(ingest, "create_data_products_from_workbook", _create)

    rc = ingest.main()
    out = capsys.readouterr().out

    assert rc == 0
    assert "Note: Type registration returned: typedef already exists" in out
    assert create_called["value"] is True

