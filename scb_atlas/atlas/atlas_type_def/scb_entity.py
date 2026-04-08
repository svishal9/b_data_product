from .base import BaseEntityCategory

scb_database = BaseEntityCategory(
    atlas_name="SCB_Database",
    display_name="SCB Database",
    super_types=["DataSet"],
    attributes=[
        { "name": "database_name", "displayName": "Database Name", "typeName": "string", "cardinality": "SINGLE", "isOptional": False, "isUnique": True, "isIndexable": True },
        { "name": "locationUri", "displayName": "Location URI", "typeName": "string", "cardinality": "SINGLE", "isOptional": False, "isUnique": False, "isIndexable": True },
        { "name": "createTime", "displayName": "Create Time", "typeName": "date", "cardinality": "SINGLE", "isOptional": False, "isUnique": False, "isIndexable": True }
    ]
)

scb_table = BaseEntityCategory(
    atlas_name="SCB_Table",
    display_name="SCB Table",
    super_types= ["DataSet"],
    attributes=[
            { "name": "table_name", "displayName": "Table Name", "typeName": "string", "cardinality": "SINGLE", "isOptional": False, "isUnique": True, "isIndexable": True },
            { "name": "createTime", "displayName": "Create Time", "typeName": "date", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
            { "name": "tableType", "displayName": "Table Type", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
            { "name": "temporary", "displayName": "Temporary", "typeName": "boolean", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
            { "name": "serde1", "displayName": "SERDE 1", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
            { "name": "serde2", "displayName": "SERDE 2", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False }
        ]
)

scb_column = BaseEntityCategory(
    atlas_name="SCB_Column",
    display_name="SCB Column",
    super_types=["DataSet"],
    attributes=[
        { "name": "column_name", "displayName": "Column Name", "typeName": "string", "cardinality": "SINGLE", "isOptional": False, "isUnique": False, "isIndexable": True },
        { "name": "dataType", "displayName": "Data Type", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "comment", "displayName": "Comment", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "position", "displayName": "Position", "typeName": "int", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False }
    ]
)

scb_standard_column = BaseEntityCategory(
    atlas_name="SCB_StandardColumn",
    display_name="SCB Standard Column",
    super_types=["DataSet"],
    attributes=[
        { "name": "field_name", "displayName": "Field Name", "typeName": "string", "cardinality": "SINGLE", "isOptional": False, "isUnique": True, "isIndexable": True },
        { "name": "data_type", "displayName": "Data Type", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "category", "displayName": "Category", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "attribute_name", "displayName": "Attribute Name", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "source_of_attribute", "displayName": "Source of Attribute", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "direct_derived", "displayName": "Direct Derived", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "field_type", "displayName": "Field Type", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "current_source_attribute", "displayName": "Current Source Attribute", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "subledger_ds", "displayName": "Subledger DS", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "fdp_attribute", "displayName": "FDP Attribute", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "derivation_logic", "displayName": "Derivation Logic", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "is_cde", "displayName": "Is CDE", "typeName": "boolean", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "product_zone", "displayName": "Product Zone", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "pii", "displayName": "PII", "typeName": "boolean", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "sample_value_1", "displayName": "Sample Value 1", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "sample_value_2", "displayName": "Sample Value 2", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "mdm_link", "displayName": "Link to MDM", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True }
    ]
)


scb_process = BaseEntityCategory(
    atlas_name="SCB_Process",
    display_name="SCB Process",
    super_types=["Process"],
    attributes=[
        { "name": "process_name", "displayName": "Process Name", "typeName": "string", "cardinality": "SINGLE", "isOptional": False, "isUnique": True, "isIndexable": True },
        { "name": "userName", "displayName": "User Name", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "startTime", "displayName": "Start Time", "typeName": "long", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "endTime", "displayName": "End Time", "typeName": "long", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": True },
        { "name": "queryText", "displayName": "Query Text", "typeName": "string", "cardinality": "SINGLE", "isOptional": False, "isUnique": False, "isIndexable": True },
        { "name": "queryId", "displayName": "Query ID", "typeName": "string", "cardinality": "SINGLE", "isOptional": False, "isUnique": True, "isIndexable": True }
    ]
)


scb_source_aligned_data_product = BaseEntityCategory(
    atlas_name="SCB_SourceAlignedDataProduct",
    display_name="SCB Source Aligned Data Product",
    super_types=["DataSet"],
    attributes=[
        { "name": "data_product_name", "displayName": "Data Product Name", "typeName": "string", "cardinality": "SINGLE", "isOptional": False, "isUnique": True, "isIndexable": True },
        { "name": "data_product_category", "displayName": "Data Product Category", "typeName": "SCB_DataProductCategory",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "tags", "displayName": "Tags", "typeName": "array<string>", "cardinality": "LIST", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "granularity", "displayName": "Granularity", "typeName": "SCB_Granularity",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "business_domain", "displayName": "Business Domain", "typeName": "SCB_BusinessDomain", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "business_metadata", "display_name": "Business Data", "typeName": "SCB_BusinessInfo", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False},
        { "name": "flags", "display_name": "Flags", "typeName": "SCB_Flags", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False},
        { "name": "data_access", "display_name": "Data Access", "typeName": "SCB_DataAccess", "typeName": "array<SCB_DataAccess>", "cardinality": "LIST", "isOptional": True, "isUnique": False, "isIndexable": False},
        { "name": "uses", "display_name": "Current Usage", "typeName": "SCB_Adoption", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False},
        { "name": "lifecycle", "display_name": "Lifecycle", "typeName": "SCB_Lifecycle", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False},
        { "name": "freshness", "display_name": "Freshness", "typeName": "SCB_Freshness", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False},
        { "name": "support_team", "display_name": "Support Team", "typeName": "SCB_SupportTeam", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False},
        { "name": "sla", "display_name": "SLA", "typeName": "SCB_Sla", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False},
    ]
)

scb_data_product = BaseEntityCategory(
    atlas_name="SCB_DataProduct",
    display_name="SCB Source Aligned Data Product",
    super_types=["DataSet"],
    attributes=[
        { "name": "data_product_name", "displayName": "Data Product Name", "typeName": "string", "cardinality": "SINGLE", "isOptional": False, "isUnique": True, "isIndexable": True },
        { "name": "data_product_category", "displayName": "Data Product Category", "typeName": "SCB_DataProductCategory",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "tags", "displayName": "Tags", "typeName": "array<string>", "cardinality": "LIST", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "granularity", "displayName": "Granularity", "typeName": "SCB_Granularity",   "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "business_domain", "displayName": "Business Domain", "typeName": "SCB_BusinessDomain", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        { "name": "business_metadata", "display_name": "Business Data", "typeName": "SCB_BusinessInfo", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False},
        { "name": "flags", "display_name": "Flags", "typeName": "SCB_Flags", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False},
        { "name": "data_access", "display_name": "Data Access", "typeName": "SCB_DataAccess", "typeName": "array<SCB_DataAccess>", "cardinality": "LIST", "isOptional": True, "isUnique": False, "isIndexable": False},
        { "name": "uses", "display_name": "Current Usage", "typeName": "SCB_Adoption", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False},
        { "name": "lifecycle", "display_name": "Lifecycle", "typeName": "SCB_Lifecycle", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False},
        { "name": "freshness", "display_name": "Freshness", "typeName": "SCB_Freshness", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False},
        { "name": "support_team", "display_name": "Support Team", "typeName": "SCB_SupportTeam", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False},
        { "name": "sla", "display_name": "SLA", "typeName": "SCB_Sla", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False},
    ]
)

entity_names = [
    # scb_column.atlas_name,
    scb_standard_column.atlas_name,
    scb_database.atlas_name,
    scb_process.atlas_name,
    scb_source_aligned_data_product.atlas_name,
    scb_table.atlas_name,
    scb_database.atlas_name,
    scb_data_product.atlas_name
]

all_entities = [
    # scb_column.prepare_atlas_type_definition(),
    scb_standard_column.prepare_atlas_type_definition(),
    scb_database.prepare_atlas_type_definition(),
    scb_process.prepare_atlas_type_definition(),
    scb_table.prepare_atlas_type_definition(),
    scb_source_aligned_data_product.prepare_atlas_type_definition(),
    scb_data_product.prepare_atlas_type_definition()
]