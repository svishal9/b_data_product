
import typer
import sys
from apache_atlas.client.base_client import AtlasClient

from scb_atlas.atlas import (
    create_atlas_client, 
    dsl_search,
    process_search,
    delete_entity
)

app = typer.Typer()


@app.command()
def catalog_search():
    client:AtlasClient = create_atlas_client("admin", "admin")

    response = dsl_search(client, ['FM_FX_Linear_Trade', 'FM_FX_Linear_Trade2'])
    print(response)

@app.command()
def process_find():
    client: AtlasClient = create_atlas_client("admin", "admin")
    response = process_search(client, "Process")

    process_guids = [process["guid"] for process in response]
    delete_entity(client, process_guids)

    response = process_search(client, "DataSet")
    dataset_guids = [dataset["guid"] for dataset in response]
    delete_entity(client, dataset_guids)

    response = process_search(client, "SCB_DataProduct")
    dataproduct_guids = [dataset["guid"] for dataset in response]
    delete_entity(client, dataproduct_guids)


if __name__ == "__main__":
    # Backward-compatible wrapper: keep old entry point working via unified CLI.
    print(
        "[DEPRECATED] `scb_dp_search.py` is deprecated. "
        "Use `scb_dp_cli.py dp ...` (or `scb dp ...`)."
    )
    from scb_dp_cli import main as scb_main

    legacy_to_unified = {
        "catalog-search": ["dp", "catalog-search"],
        "catalog_search": ["dp", "catalog-search"],
        "process-find": ["dp", "process-find"],
        "process_find": ["dp", "process-find"],
    }

    if len(sys.argv) <= 1:
        print("Usage: python scb_dp_search.py [catalog-search|process-find]")
        raise SystemExit(1)

    command = sys.argv[1]
    mapped = legacy_to_unified.get(command)
    if not mapped:
        raise SystemExit(scb_main(["dp", *sys.argv[1:]]))
    raise SystemExit(scb_main([*mapped, *sys.argv[2:]]))
