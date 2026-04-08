import typer
import sys

from scb_atlas.atlas import (
    create_atlas_client, 
    delete_typedef, 
    create_typedef,
)

from scb_atlas.atlas.atlas_type_def import all_types, all_type_names

app = typer.Typer()


@app.command()
def type_create():
    client = create_atlas_client("admin", "admin")
    create_typedef(all_types, client)

@app.command()
def type_delete(type_name: str):

    client = create_atlas_client("admin", "admin")
    delete_typedef(client, type_name)

@app.command()
def type_clean():

    client = create_atlas_client("admin", "admin")

    for type_name in all_type_names:
        try:
            delete_typedef(client, type_name)
            print(f"Deleted type {type_name}")
        except Exception as e:
            print(f"")

if __name__ == "__main__":
    # Backward-compatible wrapper: keep old entry point working via unified CLI.
    print(
        "[DEPRECATED] `scb_types.py` is deprecated. "
        "Use `scb_dp_cli.py types ...` (or `scb types ...`)."
    )
    from scb_dp_cli import main as scb_main

    legacy_to_unified = {
        "type-create": ["types", "create"],
        "type_create": ["types", "create"],
        "type-delete": ["types", "delete"],
        "type_delete": ["types", "delete"],
        "type-clean": ["types", "clean"],
        "type_clean": ["types", "clean"],
    }

    if len(sys.argv) <= 1:
        print("Usage: python scb_types.py [type-create|type-delete <name>|type-clean]")
        raise SystemExit(1)

    command = sys.argv[1]
    mapped = legacy_to_unified.get(command)
    if not mapped:
        raise SystemExit(scb_main(["types", *sys.argv[1:]]))
    raise SystemExit(scb_main([*mapped, *sys.argv[2:]]))
