from __future__ import annotations

import json
import os
import subprocess
import sys
import textwrap
from pathlib import Path
import urllib.error
import urllib.request

import pytest


def _write_stub_package(stub_root: Path) -> None:
    """Create a child-process-only stub for scb_atlas imports used by the CLI."""
    (stub_root / "scb_atlas" / "atlas" / "service").mkdir(parents=True, exist_ok=True)
    (stub_root / "scb_atlas" / "atlas" / "atlas_type_def").mkdir(parents=True, exist_ok=True)

    (stub_root / "scb_atlas" / "__init__.py").write_text("", encoding="utf-8")
    (stub_root / "scb_atlas" / "atlas" / "__init__.py").write_text(
        textwrap.dedent(
            """
            from __future__ import annotations

            import os
            from types import SimpleNamespace


            def create_atlas_client():
                return object()


            def create_typedef(type_defs, atlas_client):
                if os.getenv("STUB_TYPEDEF_RAISE") == "1":
                    raise RuntimeError("typedef already exists")
                return True


            def delete_typedef(*args, **kwargs):
                pass


            def delete_entity(*args, **kwargs):
                pass


            def validate_metadata_workbook(file_path, strict=False):
                return os.getenv("STUB_VALIDATE_FAIL") != "1"


            def parse_master_schema_workbook_to_data_products(file_path, strict=False):
                count = int(os.getenv("STUB_MODEL_COUNT", "1"))
                models = []
                for i in range(count):
                    models.append(
                        SimpleNamespace(
                            basic_metadata=SimpleNamespace(data_product_name=f"DP_{i + 1}"),
                            output_port_schema=[object(), object()],
                        )
                    )
                return models


            def create_data_products_from_workbook(file_path, atlas_client, strict=False):
                if os.getenv("STUB_CREATED_NAMES"):
                    return [n for n in os.getenv("STUB_CREATED_NAMES", "").split(",") if n]
                return ["DP_1"]
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    (stub_root / "scb_atlas" / "atlas" / "atlas_type_def" / "__init__.py").write_text(
        "all_types = {'entityDefs': [], 'relationshipDefs': [], 'classificationDefs': [], 'structDefs': []}\n"
        "all_type_names = []\n",
        encoding="utf-8",
    )
    # Add stubs for modules imported by clean_up_atlas
    (stub_root / "scb_atlas" / "atlas" / "atlas_client.py").write_text(
        "def create_atlas_client():\n    return object()\n",
        encoding="utf-8",
    )
    (stub_root / "scb_atlas" / "atlas" / "service" / "__init__.py").write_text(
        textwrap.dedent(
            """
            def create_typedef(*args, **kwargs):
                pass

            def delete_entity(*args, **kwargs):
                pass

            def create_database_from_model(*args, **kwargs):
                pass

            def create_table_from_model(*args, **kwargs):
                pass

            def create_column_from_model(*args, **kwargs):
                pass

            def create_process_from_model(*args, **kwargs):
                pass

            def create_data_product_from_model(*args, **kwargs):
                pass
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )
    (stub_root / "scb_atlas" / "atlas" / "service" / "entity_service.py").write_text(
        "def delete_entity(*args, **kwargs):\n    pass\n",
        encoding="utf-8",
    )
    # Add stub for metadata_models with all required classes
    (stub_root / "scb_atlas" / "atlas" / "metadata_models.py").write_text(
        textwrap.dedent(
            """
            from pydantic import BaseModel
            from typing import Optional

            class DatabaseModel(BaseModel):
                pass

            class TableModel(BaseModel):
                pass

            class ColumnModel(BaseModel):
                pass

            class ProcessModel(BaseModel):
                pass

            class DataProductModel(BaseModel):
                pass
            """
        ).strip()
        + "\n",
        encoding="utf-8",
    )


def _run_cli(project_root: Path, stub_root: Path, args: list[str], extra_env: dict[str, str] | None = None):
    script = project_root / "ingest_workbook_to_atlas.py"
    env = os.environ.copy()
    env["PYTHONPATH"] = f"{stub_root}{os.pathsep}{env.get('PYTHONPATH', '')}"
    env.setdefault("ATLAS_URL", "http://localhost:23000")
    env.setdefault("ATLAS_USERNAME", "admin")
    env.setdefault("ATLAS_PASSWORD", "admin")
    if extra_env:
        env.update(extra_env)

    # Execute the target script via runpy so import resolution uses subprocess cwd/PYTHONPATH.
    runner = (
        "import json, runpy, sys; "
        "script = sys.argv[1]; "
        "argv = json.loads(sys.argv[2]); "
        "sys.argv = [script, *argv]; "
        "runpy.run_path(script, run_name='__main__')"
    )
    cmd = [sys.executable, "-c", runner, str(script), json.dumps(args)]
    return subprocess.run(cmd, cwd=stub_root, env=env, capture_output=True, text=True)


def _atlas_reachable(atlas_url: str, timeout_seconds: float = 2.0) -> bool:
    """Best-effort check to see if Atlas endpoint is reachable over HTTP."""
    try:
        with urllib.request.urlopen(atlas_url, timeout=timeout_seconds) as response:
            # Atlas may return 200 for root, but any HTTP response means endpoint is reachable.
            return response.status in {200, 401, 403}
    except urllib.error.HTTPError as exc:
        # 401/403 is expected for protected Atlas endpoints.
        return exc.code in {401, 403}
    except Exception:
        return False


def test_cli_dry_run_subprocess_contract(project_root_path, tmp_path):
    _write_stub_package(tmp_path)
    result = _run_cli(
        project_root_path,
        tmp_path,
        ["sample_data/metadata_master_schema.xlsx", "--dry-run", "--strict"],
        extra_env={"STUB_MODEL_COUNT": "2"},
    )

    assert result.returncode == 0
    assert "Validated workbook. Parsed 2 data product(s)." in result.stdout
    assert "- DP_1 (schema fields: 2)" in result.stdout
    assert "- DP_2 (schema fields: 2)" in result.stdout
    assert "Registering SCB type definitions..." not in result.stdout


def test_cli_non_dry_run_registers_types_and_creates(project_root_path, tmp_path):
    _write_stub_package(tmp_path)

    result = _run_cli(
        project_root_path,
        tmp_path,
        ["sample_data/metadata_master_schema.xlsx"],
        extra_env={"STUB_CREATED_NAMES": "FM_Unified_Cashflow"},
    )

    assert result.returncode == 0
    assert "Validated workbook. Parsed 1 data product(s)." in result.stdout
    assert "Registering SCB type definitions..." in result.stdout
    assert "Type definitions ready." in result.stdout
    assert "Created 1 data product entity(ies):" in result.stdout
    assert "- FM_Unified_Cashflow" in result.stdout


def test_cli_continues_when_typedef_registration_raises(project_root_path, tmp_path):
    _write_stub_package(tmp_path)

    result = _run_cli(
        project_root_path,
        tmp_path,
        ["sample_data/metadata_example.xlsx"],
        extra_env={"STUB_TYPEDEF_RAISE": "1", "STUB_CREATED_NAMES": "DP_X"},
    )

    assert result.returncode == 0
    assert "Registering SCB type definitions..." in result.stdout
    assert "Note: Type registration returned: typedef already exists" in result.stdout
    assert "Created 1 data product entity(ies):" in result.stdout
    assert "- DP_X" in result.stdout


def test_cli_validation_failure_returns_1_and_stops(project_root_path, tmp_path):
    _write_stub_package(tmp_path)

    result = _run_cli(
        project_root_path,
        tmp_path,
        ["sample_data/metadata_example.xlsx"],
        extra_env={"STUB_VALIDATE_FAIL": "1"},
    )

    assert result.returncode == 1
    assert "Workbook validation failed." in result.stdout
    assert "Registering SCB type definitions..." not in result.stdout
    assert "Created" not in result.stdout


@pytest.mark.slow
def test_cli_real_environment_end_to_end_output_contract(project_root_path):
    """Run the real CLI against an actual Atlas endpoint and assert output contract."""
    if os.getenv("RUN_REAL_ATLAS_TEST") != "1":
        pytest.skip("Set RUN_REAL_ATLAS_TEST=1 to run real Atlas integration test.")

    atlas_url = os.getenv("ATLAS_URL", "http://localhost:23000")
    if not _atlas_reachable(atlas_url):
        pytest.skip(f"Atlas endpoint is not reachable at {atlas_url}")

    script = project_root_path / "ingest_workbook_to_atlas.py"
    cmd = [sys.executable, str(script), "sample_data/metadata_example.xlsx"]
    result = subprocess.run(cmd, cwd=project_root_path, capture_output=True, text=True)

    assert result.returncode == 0, result.stderr
    assert "Validated workbook. Parsed" in result.stdout
    assert "Registering SCB type definitions..." in result.stdout
    # Depending on environment state, typedef registration may either create or report existing types.
    assert (
        "Type definitions ready." in result.stdout
        or "Note: Type registration returned:" in result.stdout
    )
    assert "Created " in result.stdout
    assert " data product entity(ies):" in result.stdout
    assert "- FM_Unified_Cashflow" in result.stdout

