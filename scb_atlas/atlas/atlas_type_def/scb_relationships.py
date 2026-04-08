from .base import BaseRelationshipCategory

scb_database_table_relation = BaseRelationshipCategory(
    atlas_name="SCB_Database_Tables",

    enddef1={
        "type": "SCB_Database",
        "name": "tables",
        "isContainer": True,
        "cardinality": "SET",
        "isLegacyAttribute": False,
    },
    enddef2={
        "type": "SCB_Table",
        "name": "database",
        "isContainer": False,
        "cardinality": "SINGLE",
        "isLegacyAttribute": False,
    })




scb_table_columns_relation = BaseRelationshipCategory(
    atlas_name="SCB_Table_Columns",
    enddef1={
        "type": "SCB_Table",
        "name": "columns",
        "isContainer": True,
        "cardinality": "SET",
        "isLegacyAttribute": False,
    },
    enddef2={
        "type": "SCB_StandardColumn",
        "name": "table",
        "isContainer": False,
        "cardinality": "SINGLE",
        "isLegacyAttribute": False,
    }
)
    


scb_process_inputporttables_relation = BaseRelationshipCategory(
    atlas_name="SCB_Process_InputPortTables",
    relationship_category="ASSOCIATION",
    enddef1= {
        "type": "SCB_Process",
        "name": "input_port_tables",
        "isContainer": False,
        "cardinality": "SET",
        "isLegacyAttribute": False,
    },
    enddef2={
        "type": "SCB_Table",
        "name": "inputProcess",
        "isContainer": False,
        "cardinality": "SET",
        "isLegacyAttribute": False,
    }
)


scb_process_outputporttables = BaseRelationshipCategory(
    atlas_name="SCB_Process_OutputPortTables",
    relationship_category="ASSOCIATION",
    enddef1={
        "type": "SCB_Process",
        "name": "output_port_tables",
        "isContainer": False,
        "cardinality": "SET",
        "isLegacyAttribute": False,
    },
    enddef2={
        "type": "SCB_Table",
        "name": "outputProcess",
        "isContainer": False,
        "cardinality": "SET",
        "isLegacyAttribute": False,
    }
)

scb_dataproduct_inputports = BaseRelationshipCategory(
    atlas_name="SCB_DataProduct_InputPorts",
    relationship_category="ASSOCIATION",
    enddef1={
        "type": "DataSet",
        "name": "input_port",
        "isContainer": False,
        "cardinality": "SET",
        "isLegacyAttribute": False,
    },
    enddef2={
        "type": "SCB_Table",
        "name": "input_port_of",
        "isContainer": False,
        "cardinality": "SET",
        "isLegacyAttribute": False,
    }
)

scb_dataproduct_outputport = BaseRelationshipCategory(
    atlas_name="SCB_DataProduct_OutputPort",
    relationship_category="ASSOCIATION",
    enddef1={
        "type": "DataSet",
        "name": "output_port",
        "isContainer": False,
        "cardinality": "SINGLE",
        "isLegacyAttribute": False,
    },
    enddef2={
        "type": "SCB_Table",
        "name": "output_port_of",
        "isContainer": False,
        "cardinality": "SET",
        "isLegacyAttribute": False,
    },
)

    
scb_dataproduct_inputprocess = BaseRelationshipCategory(
    atlas_name="SCB_DataProduct_InputProcess",
    relationship_category="ASSOCIATION",
    enddef1={
        "type": "DataSet",
        "name": "inputProcess",
        "isContainer": False,
        "cardinality": "SET",
        "isLegacyAttribute": False,
    },
    enddef2={
        "type": "SCB_Process",
        "name": "inputProcessOf",
        "isContainer": False,
        "cardinality": "SET",
        "isLegacyAttribute": False,
    }
)

scb_dataproduct_outputprocess = BaseRelationshipCategory(
    atlas_name="SCB_DataProduct_OutputProcess",
    relationship_category="ASSOCIATION",
    enddef1={
        "type": "DataSet",
        "name": "outputProcess",
        "isContainer": False,
        "cardinality": "SET",
        "isLegacyAttribute": False,
    },
    enddef2={
        "type": "SCB_Process",
        "name": "outputProcessOf",
        "isContainer": False,
        "cardinality": "SET",
        "isLegacyAttribute": False,
    }
)

relationship_names = [
    scb_database_table_relation.atlas_name,
    scb_dataproduct_inputports.atlas_name,
    scb_dataproduct_inputprocess.atlas_name,
    scb_dataproduct_outputport.atlas_name,
    scb_dataproduct_outputprocess.atlas_name,
    scb_process_inputporttables_relation.atlas_name,
    scb_process_outputporttables.atlas_name,
    scb_table_columns_relation.atlas_name
]

all_relationships = [
    scb_database_table_relation.prepare_atlas_type_definition(),
    scb_dataproduct_inputports.prepare_atlas_type_definition(),
    scb_dataproduct_inputprocess.prepare_atlas_type_definition(),
    scb_dataproduct_outputport.prepare_atlas_type_definition(),
    scb_dataproduct_outputprocess.prepare_atlas_type_definition(),
    scb_process_inputporttables_relation.prepare_atlas_type_definition(),
    scb_process_outputporttables.prepare_atlas_type_definition(),
    scb_table_columns_relation.prepare_atlas_type_definition()
]