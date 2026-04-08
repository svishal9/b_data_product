import typer

from scb_atlas.atlas import (
    create_atlas_client, 
    delete_typedef, 
    create_typedef, 
)

enum_definitions = {
    "enumDefs": [
        {
            "name":        "SCB_Domain",
            "description": "Domain of the data product",
            "category":    "ENUM",
            "typeVersion": "1.0",
            "elementDefs": [
                { "value": "FM",  "ordinal": 1 }
            ]
        },
        {
            "name":        "SCB_SubDomain",
            "description": "Sub-Domain of the data product",
            "category":    "ENUM",
            "typeVersion": "1.0",
            "elementDefs": [
                { "value": "FX",  "ordinal": 1 },
                { "value": "RATES",  "ordinal": 2 },
                { "value": "Options",  "ordinal": 3 }
            ]
        },
        {
            "name":        "SCB_DataProductCategory",
            "description": "Category of the data product",
            "category":    "ENUM",
            "typeVersion": "1.0",
            "elementDefs": [
                { "value": "Source Aligned",  "ordinal": 1 },
                { "value": "Consumer Aligned",  "ordinal": 2 }
            ]
        },
        {
            "name":        "SCB_LifeCycleStatus",
            "description": "LifeCycle Status of the data product",
            "category":    "ENUM",
            "typeVersion": "1.0",
            "elementDefs": [
                { "value": "Production",  "ordinal": 1 }
            ]
        },
        {
            "name":        "SCB_Granularity",
            "description": "Granularity of the data product",
            "category":    "ENUM",
            "typeVersion": "1.0",
            "elementDefs": [
                { "value": "Trade",  "ordinal": 1 },
                { "value": "Trade + Legs",  "ordinal": 2 }
        ]
        },
        {
            "name":        "SCB_RefreshFrequency",
            "description": "Refresh Frequency of the data product",
            "category":    "ENUM",
            "typeVersion": "1.0",
            "elementDefs": [
                { "value": "Daily (T+0)", "ordinal": 1 }
            ]
        },
        {
            "name":        "SCB_RefreshCut",
            "description": "Refresh Cut of the data product",
            "category":    "ENUM",
            "typeVersion": "1.0",
            "elementDefs": [
                { "value": "Actual", "ordinal": 1 }
            ]
        },
        {
            "name":        "SCB_GovernanceSensitivity",
            "description": "Governance Sensitivity of the data product",
            "category":    "ENUM",
            "typeVersion": "1.0",
            "elementDefs": [
                { "value": "Internal", "ordinal": 1 },
                { "value": "External", "ordinal": 2 }
            ]
        },
        {
            "name":        "SCB_GovernancePersonal",
            "description": "Governance Personal of the data product",
            "category":    "ENUM",
            "typeVersion": "1.0",
            "elementDefs": [
                { "value": "No", "ordinal": 1 },
                { "value": "Yes", "ordinal": 2 }
            ]
    }]}


app = typer.Typer()


@app.command()
def enums_create():
    client = create_atlas_client("admin", "admin")
    create_typedef(enum_definitions, client)

@app.command()
def enums_delete(enum_name: str):

    client = create_atlas_client("admin", "admin")
    delete_typedef(client, enum_name)

if __name__ == "__main__":
    app()
