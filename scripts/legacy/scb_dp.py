import typer
import sys
from apache_atlas.client.base_client import AtlasClient

from scb_atlas.atlas import (
    create_atlas_client, 
    delete_entity, 
    create_data_product_entity,
    create_dataset_entity,
    convert_to_atlas_model,
    create_process_entity,
    dsl_search
)

# TODO: Data from Excel. This will be available from Excel file.

excel_data = {
    "Data Product Name": "FM_Unified_Cashflow",
    "Description": "Unified FM Trade Cashflow - flattened stream of all known cash movements - for trade products",
    "Domain": "FM",
    "Sub-Domain": "FM Common",
    "Data Product Category": "Source-Aligned",
    "Version": "1.1",
    "Tags/Keywords": "",
    "Lifecycle Status": "Production",
    "Granularity": "Incremental",
    "Rrefresh Frequency": "Daily (T+0)",
    "Refresh Cut": "Actual",
    "Source Domain Owner": "Zhu.Zhu",
    "GCFO Owner": "Karthik.Ramamurthy",
    "Data Steward": "Manish.Patel",
    "Support Contact": "NagarjunaReddy.Konda",
    "Business Purpose": "FM Source Aligned DP - Finance Consumption View",
    "Users": "0",
    "Systems": "0",
    "Usecases": "Account,Capital,Liquidity",
    "Sensitivity": "Internal",
    "Personal": "No",
    "Data Retention": "3 Years",
    "Schema": "",
    "Source Systems": "Murex,Razr,Sabre,GPTM",
    "Data Landing Patterns": "API - FDP Staging Table",
    "Linked Domains": "CIB - Client & Counterparty,CIB - Portfolio,Instrument Static,Market Static",
    "Agreed SLA": "",
    "Data Handshake": "",
    "Completeness": "100%",
    "Refresh Rate": "Daily (T+0)",
    "Data Schema": [
        {
            "field_name": "Product Type",
            "field_type": "String",
            "field_description": "The specific type of rate derivative",
            "sample_values": "InterestRate:CrossCurrency:Basis,InterestRate:IRSwap:OIS"
        }
    ]
}


# excel_data = {
#     "Data Product Name": "FM_FX_Linear_Trade",
#     "Description": "FM Trade Data Product that covers FX Linear Trades FX Spot, FX Forward, FX NDF and FX Swap",
#     "Domain": "FM",
#     "Sub-Domain": "FX",
#     "Data Product Category": "Source-Aligned",
#     "Version": "1",
#     "Tags/Keywords": "tag-1, tag-2",
#     "Lifecycle Status": "Production",
#     "Granularity": "Trade",
#     "Rrefresh Frequency": "Daily (T+0)",
#     "Refresh Cut": "Actual",
#     "Source Domain Owner": "John Smith",
#     "GCFO Owner": "Jane Doe",
#     "Data Steward": "Jim Doe",
#     "Support Contact": "support@scb.com",
#     "Business Purpose": "",
#     "Users": "0",
#     "Systems": "1",
#     "Usecases": "Account,Capital,Liquidity",
#     "Sensitivity": "Internal",
#     "Personal": "No",
#     "Data Retention": "3 Years",
#     "Schema": "",
#     "Source Systems": "Murex,Razr,DQSL",
#     "Data Landing Patterns": "API - FDP Staging Table",
#     "Linked Domains": "CIB - Clients & Counterparty,CIB - Portfolio",
#     "Agreed SLA": "",
#     "Data Handshake": "",
#     "Completeness": "100%",
#     "Refresh Rate": "Daily (T+0)",
#     "Data Schema": [
#         {
#             "field_name": "Product Type",
#             "field_type": "string",
#             "field_description": "The specific type of rate derivative",
#             "sample_values": "InterestRate:CrossCurrency:Basis,InterestRate:IRSwap:OIS"
#         }
#     ]
# }

app = typer.Typer()

def _new_dataset_to_create(source_systems: list[str], found_data: list[dict]) -> list[str]:

    """
        Helper method to find out the required new dataset to be created
        in Atlas to create the lineage for a new DataProduct.
    """

    found_data_dicts = {
        found["name"]: {
            "typeName": found["type_name"],
            "attributes": {
                "name": found["name"],
                "qualifiedName": found["qualified_name"]
            }
        } for found in found_data
    }

    new_datasets_to_create: list[str] = [
        name for name in source_systems if name not in found_data_dicts
    ]

    print(f"Identified {new_datasets_to_create} as new datasets to create")
    return new_datasets_to_create


@app.command()
def entity_create():

    """
        This method creates entities in Atlas based on the provided excel data.

        It first checks if the required datasets already exist in Atlas. If not, it creates them.
        Then, it creates the Data Product, Process, and Dataset entities in Atlas.

        Args:
            None

        Returns:
            None
    """
    client:AtlasClient = create_atlas_client("admin", "admin")

    data_product = convert_to_atlas_model(excel_data=excel_data)

    # check if there are any source systems in the excel data
    source_systems_str = excel_data.get("Source Systems", "")
    source_systems: list[str] = []
    if source_systems_str:
        source_systems = [s.strip() for s in source_systems_str.split(",")]
        found_data = dsl_search(atlas_client=client, names=source_systems)
        new_dataset = _new_dataset_to_create(source_systems, found_data)
        if new_dataset:
            create_dataset_entity(client, new_dataset)

    create_data_product_entity(client, data_product, source_systems=source_systems)

    if source_systems:
        create_process_entity(
            client,
            source_systems,
            data_product.basic_metadata.data_product_name,
            domain=data_product.governance_metadata.domain,
        )

    
    # excel_data["Personal"] = "Yes"
    # excel_data["Data Product Name"] = "FM_FX_Linear_Trade2"
    # data_product2 = convert_to_atlas_model(excel_data)
    # create_data_product_entity(client, data_product2)

    # # check if there are any source systems in the excel data
    # source_systems_str = excel_data.get("Source Systems", "")
    # if source_systems_str:
    #     source_systems = [s.strip() for s in source_systems_str.split(",")]
    #     source_systems.append("FM_FX_Linear_Trade")
    #     found_data = dsl_search(atlas_client=client, names=source_systems)
    #     new_dataset = _new_dataset_to_create(source_systems, found_data)
    #     if new_dataset:
    #         create_dataset_entity(client, new_dataset)
    #     create_process_entity(
    #         client,
    #         source_systems,
    #         data_product2.basic_metadata.data_product_name,
    #         domain=data_product2.governance_metadata.domain,
    #     )

@app.command()
def entity_delete(guid: str):
    """
        Command to delete an entity based on its GUID.
    """
    client = create_atlas_client("admin", "admin")
    
    guids = [
        guid
    ]
    delete_op_response = delete_entity(client,guids)
    
    print(delete_op_response)

if __name__ == "__main__":
    # Backward-compatible wrapper: keep old entry point working via unified CLI.
    print(
        "[DEPRECATED] `scb_dp.py` is deprecated. "
        "Use `scb_dp_cli.py dp ...` (or `scb dp ...`)."
    )
    from scb_dp_cli import main as scb_main

    legacy_to_unified = {
        "entity-create": ["dp", "entity-create"],
        "entity_create": ["dp", "entity-create"],
        "entity-delete": ["dp", "entity-delete"],
        "entity_delete": ["dp", "entity-delete"],
    }

    if len(sys.argv) <= 1:
        print("Usage: python scb_dp.py [entity-create|entity-delete <guid>]")
        raise SystemExit(1)

    command = sys.argv[1]
    mapped = legacy_to_unified.get(command)
    if not mapped:
        raise SystemExit(scb_main(["dp", *sys.argv[1:]]))
    raise SystemExit(scb_main([*mapped, *sys.argv[2:]]))
