from __future__ import annotations

from types import SimpleNamespace

import scb_dp_cli as scb_cli


def _fake_model(name: str, schema_fields: int = 0):
	return SimpleNamespace(
		basic_metadata=SimpleNamespace(data_product_name=name),
		output_port_schema=[object() for _ in range(schema_fields)],
		qualified_name=f"scb:::dp:::{name.lower()}",
	)


def test_ingest_dry_run_does_not_create_entities(monkeypatch, capsys):
	monkeypatch.setattr(scb_cli, "validate_metadata_workbook", lambda *_args, **_kwargs: True)
	monkeypatch.setattr(
		scb_cli,
		"parse_master_schema_workbook_to_data_products",
		lambda *_args, **_kwargs: [_fake_model("DP_A", 2), _fake_model("DP_B", 0)],
	)

	called = {"client": False, "typedef": False, "create": False}
	monkeypatch.setattr(scb_cli, "create_atlas_client", lambda *_args, **_kwargs: called.__setitem__("client", True))
	monkeypatch.setattr(scb_cli, "create_typedef", lambda *_args, **_kwargs: called.__setitem__("typedef", True))
	monkeypatch.setattr(
		scb_cli,
		"create_data_products_from_workbook",
		lambda *_args, **_kwargs: called.__setitem__("create", True),
	)

	rc = scb_cli.main(["ingest", "sample_data/metadata_master_schema.xlsx", "--dry-run"])
	out = capsys.readouterr().out

	assert rc == 0
	assert "Validated workbook. Parsed 2 data product(s)." in out
	assert "- DP_A (schema fields: 2)" in out
	assert "- DP_B (schema fields: 0)" in out
	assert called == {"client": False, "typedef": False, "create": False}


def test_types_create_calls_typedef(monkeypatch, capsys):
	atlas_client = object()
	calls = []

	monkeypatch.setattr(scb_cli, "create_atlas_client", lambda *_args, **_kwargs: atlas_client)
	monkeypatch.setattr(scb_cli, "create_typedef", lambda type_defs, client: calls.append((type_defs, client)))

	rc = scb_cli.main(["types", "create"])
	out = capsys.readouterr().out

	assert rc == 0
	assert calls == [(scb_cli.all_types, atlas_client)]
	assert "SCB types created." in out


def test_tests_command_runs_expected_pytest_invocation(monkeypatch):
	captured = {}

	def _fake_run(cmd, check=False):
		captured["cmd"] = cmd
		captured["check"] = check
		return SimpleNamespace(returncode=0)

	monkeypatch.setattr(scb_cli.subprocess, "run", _fake_run)

	rc = scb_cli.main(["tests", "unit"])

	assert rc == 0
	assert captured["cmd"] == [
		scb_cli.sys.executable,
		"-m",
		"pytest",
		"tests/unit/",
		"-v",
	]
	assert captured["check"] is False


def test_recreate_dry_run_prints_status_without_mutation(monkeypatch, capsys):
	model = _fake_model("DP_A", 1)
	monkeypatch.setattr(scb_cli, "parse_master_schema_workbook_to_data_products", lambda *_args, **_kwargs: [model])
	monkeypatch.setattr(scb_cli, "create_atlas_client", lambda *_args, **_kwargs: object())
	monkeypatch.setattr(
		scb_cli,
		"_find_existing_data_product_guids",
		lambda *_args, **_kwargs: {model.qualified_name: "guid-1"},
	)

	called = {"delete": False, "create": False, "typedef": False}
	monkeypatch.setattr(scb_cli, "delete_entity", lambda *_args, **_kwargs: called.__setitem__("delete", True))
	monkeypatch.setattr(
		scb_cli,
		"create_data_products_from_workbook",
		lambda *_args, **_kwargs: called.__setitem__("create", True),
	)
	monkeypatch.setattr(scb_cli, "create_typedef", lambda *_args, **_kwargs: called.__setitem__("typedef", True))

	rc = scb_cli.main(["recreate", "sample_data/metadata_master_schema.xlsx", "--dry-run"])
	out = capsys.readouterr().out

	assert rc == 0
	assert "Workbook parsed. Data products: 1" in out
	assert "(exists)" in out
	assert "Dry-run complete. No Atlas changes made." in out
	assert called == {"delete": False, "create": False, "typedef": False}

