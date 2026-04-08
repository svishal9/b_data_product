"""
Entity builders for creating different types of entities in Apache Atlas.
This module provides functions to build entity payloads for:
- Database entities (SCB_Database)
- Table entities (SCB_Table)
- Column entities (SCB_Column)
- Process entities (SCB_Process)
"""

from typing import Optional, Any
from datetime import datetime
from .atlas_type_def import prepare_qualified_name


def _now_epoch_millis() -> int:
    """Return current timestamp in milliseconds for Atlas `date` fields."""
    return int(datetime.now().timestamp() * 1000)


class DatabaseEntityBuilder:
    """Builder for SCB_Database entities."""
    
    def __init__(self, database_name: str, location_uri: str):
        """
        Initialize a Database entity builder.
        
        Args:
            database_name (str): Name of the database
            location_uri (str): Location URI for the database
        """
        self.database_name = database_name
        self.location_uri = location_uri
        self.description = None
        self.create_time = None
    
    def set_description(self, description: str) -> 'DatabaseEntityBuilder':
        """Set the database description."""
        self.description = description
        return self
    
    def set_create_time(self, create_time: str) -> 'DatabaseEntityBuilder':
        """Set the creation time."""
        self.create_time = create_time
        return self
    
    def build(self) -> dict:
        """Build the database entity."""
        attributes = {
            'name': self.database_name,
            'database_name': self.database_name,
            'locationUri': self.location_uri,
            'qualifiedName': prepare_qualified_name(self.database_name)
        }
        
        if self.description:
            attributes['description'] = self.description
        
        if self.create_time:
            attributes['createTime'] = self.create_time
        else:
            attributes['createTime'] = str(_now_epoch_millis())
        
        return {
            'entity': {
                'typeName': 'SCB_Database',
                'attributes': attributes
            }
        }


class TableEntityBuilder:
    """Builder for SCB_Table entities."""
    
    def __init__(self, table_name: str, database_name: Optional[str] = None):
        """
        Initialize a Table entity builder.
        
        Args:
            table_name (str): Name of the table
            database_name (str, optional): Name of the parent database
        """
        self.table_name = table_name
        self.database_name = database_name
        self.table_type = None
        self.temporary = False
        self.serde1 = None
        self.serde2 = None
        self.description = None
        self.create_time = None
    
    def set_table_type(self, table_type: str) -> 'TableEntityBuilder':
        """Set the table type (e.g., 'EXTERNAL', 'MANAGED')."""
        self.table_type = table_type
        return self
    
    def set_temporary(self, temporary: bool) -> 'TableEntityBuilder':
        """Set whether the table is temporary."""
        self.temporary = temporary
        return self
    
    def set_serde(self, serde1: str, serde2: Optional[str] = None) -> 'TableEntityBuilder':
        """Set SERDE information."""
        self.serde1 = serde1
        self.serde2 = serde2
        return self
    
    def set_description(self, description: str) -> 'TableEntityBuilder':
        """Set the table description."""
        self.description = description
        return self
    
    def set_create_time(self, create_time: str) -> 'TableEntityBuilder':
        """Set the creation time."""
        self.create_time = create_time
        return self
    
    def build(self) -> dict:
        """Build the table entity."""
        qualified_name = prepare_qualified_name(f"{self.database_name}.{self.table_name}" if self.database_name else self.table_name)
        
        attributes = {
            'name': self.table_name,
            'table_name': self.table_name,
            'qualifiedName': qualified_name,
            'temporary': self.temporary
        }
        
        if self.table_type:
            attributes['tableType'] = self.table_type
        
        if self.serde1:
            attributes['serde1'] = self.serde1
        
        if self.serde2:
            attributes['serde2'] = self.serde2
        
        if self.description:
            attributes['description'] = self.description
        
        if self.create_time:
            attributes['createTime'] = self.create_time
        else:
            attributes['createTime'] = str(_now_epoch_millis())
        
        return {
            'entity': {
                'typeName': 'SCB_Table',
                'attributes': attributes
            }
        }


class ColumnEntityBuilder:
    """Builder for SCB_Column entities."""
    
    def __init__(self, column_name: str, data_type: str, table_name: Optional[str] = None):
        """
        Initialize a Column entity builder.
        
        Args:
            column_name (str): Name of the column
            data_type (str): Data type of the column
            table_name (str, optional): Name of the parent table
        """
        self.column_name = column_name
        self.data_type = data_type
        self.table_name = table_name
        self.comment = None
        self.position = None
    
    def set_comment(self, comment: str) -> 'ColumnEntityBuilder':
        """Set the column comment."""
        self.comment = comment
        return self
    
    def set_position(self, position: int) -> 'ColumnEntityBuilder':
        """Set the column position."""
        self.position = position
        return self
    
    def build(self) -> dict:
        """Build the column entity."""
        qualified_name = prepare_qualified_name(
            f"{self.table_name}.{self.column_name}" if self.table_name else self.column_name
        )
        
        attributes = {
            'name': self.column_name,
            'column_name': self.column_name,
            'dataType': self.data_type,
            'qualifiedName': qualified_name
        }
        
        if self.comment:
            attributes['comment'] = self.comment
        
        if self.position is not None:
            attributes['position'] = self.position
        
        return {
            'entity': {
                'typeName': 'SCB_Column',
                'attributes': attributes
            }
        }


class ProcessEntityBuilder:
    """Builder for SCB_Process entities."""
    
    def __init__(self, process_name: str, query_id: str, query_text: str):
        """
        Initialize a Process entity builder.
        
        Args:
            process_name (str): Name of the process
            query_id (str): Unique identifier for the query
            query_text (str): The query text
        """
        self.process_name = process_name
        self.query_id = query_id
        self.query_text = query_text
        self.user_name = None
        self.start_time = None
        self.end_time = None
        self.input_entities = []
        self.output_entities = []
    
    def set_user_name(self, user_name: str) -> 'ProcessEntityBuilder':
        """Set the user name."""
        self.user_name = user_name
        return self
    
    def set_start_time(self, start_time: int) -> 'ProcessEntityBuilder':
        """Set the start time (Unix timestamp in milliseconds)."""
        self.start_time = start_time
        return self
    
    def set_end_time(self, end_time: int) -> 'ProcessEntityBuilder':
        """Set the end time (Unix timestamp in milliseconds)."""
        self.end_time = end_time
        return self
    
    def add_input_entity(self, type_name: str, qualified_name: str) -> 'ProcessEntityBuilder':
        """Add an input entity reference."""
        self.input_entities.append({
            "typeName": type_name,
            "uniqueAttributes": {"qualifiedName": qualified_name}
        })
        return self
    
    def add_output_entity(self, type_name: str, qualified_name: str) -> 'ProcessEntityBuilder':
        """Add an output entity reference."""
        self.output_entities.append({
            "typeName": type_name,
            "uniqueAttributes": {"qualifiedName": qualified_name}
        })
        return self
    
    def build(self) -> dict:
        """Build the process entity."""
        attributes: dict[str, Any] = {
            'name': self.process_name,
            'process_name': self.process_name,
            'queryId': self.query_id,
            'queryText': self.query_text,
            'qualifiedName': prepare_qualified_name(self.query_id)
        }
        
        if self.user_name:
            attributes['userName'] = self.user_name
        
        if self.start_time is not None:
            attributes['startTime'] = self.start_time
        
        if self.end_time is not None:
            attributes['endTime'] = self.end_time
        
        entity_def = {
            'entity': {
                'typeName': 'SCB_Process',
                'attributes': attributes
            }
        }
        
        if self.input_entities:
            entity_def['entity']['attributes']['inputs'] = self.input_entities
        
        if self.output_entities:
            entity_def['entity']['attributes']['outputs'] = self.output_entities
        
        return entity_def

# ============================================================================
# COMPATIBILITY WRAPPER FUNCTIONS FOR BACKWARD COMPATIBILITY
# ============================================================================

def convert_to_atlas_model(excel_data: dict):
    """
    Convert Excel data dictionary to a CompleteDataProductModel.
    
    Args:
        excel_data: Dictionary containing data product metadata from Excel
        
    Returns:
        CompleteDataProductModel: Pydantic model ready for Atlas ingestion
    """
    from .metadata_models import (
        CompleteDataProductModel,
        DataProductBasicMetadata,
        DataProductBusinessMetadata,
        DataProductClassification,
        DataProductPorts,
        DataProductUsage,
        DataProductLifecycle,
        DataProductGovernanceMetadata,
        SensitivityEnum,
        LifecycleStatusEnum,
    )
    
    # Map sensitivity values
    sensitivity_map = {
        "Internal": SensitivityEnum.SENSITITY_INTERNAL,
        "External": SensitivityEnum.SENSITIVITY_EXTERNAL,
        "SCB Sensitive Internal": SensitivityEnum.SENSITITY_INTERNAL,
        "SCB Sensitive External": SensitivityEnum.SENSITIVITY_EXTERNAL,
    }
    
    # Map lifecycle status values
    lifecycle_map = {
        "Production": LifecycleStatusEnum.PUBLISH_CONSUME,
        "Staging": LifecycleStatusEnum.VALIDATE_APPROVE,
        "Development": LifecycleStatusEnum.DEVELOP_BUILD,
        "Proposed": LifecycleStatusEnum.IDEATE_PROPOSE,
        "Ideate & Propose": LifecycleStatusEnum.IDEATE_PROPOSE,
        "Define & Design": LifecycleStatusEnum.DEFINE_DESIGN,
        "Develop & Build": LifecycleStatusEnum.DEVELOP_BUILD,
        "Validate & Approve": LifecycleStatusEnum.VALIDATE_APPROVE,
        "Publish & Consume": LifecycleStatusEnum.PUBLISH_CONSUME,
        "Monitor & Maintain": LifecycleStatusEnum.MONITOR_MAINTAIN,
        "Change & Retire": LifecycleStatusEnum.CHANGE_RETIRE,
    }
    
    # Extract nested data from Excel dict
    basic_metadata = DataProductBasicMetadata(
        data_product_name=excel_data.get("Data Product Name", ""),
        description=excel_data.get("Description", ""),
        data_product_category=excel_data.get("Data Product Category", "Source-Aligned"),
    )
    
    business_metadata = DataProductBusinessMetadata(
        business_purpose=excel_data.get("Business Purpose", ""),
        gcfo_owner_name=excel_data.get("GCFO Owner", ""),
        gcfo_owner_contact=excel_data.get("Support Contact", ""),
    )
    
    # Map sensitivity enum
    sensitivity_input = excel_data.get("Sensitivity", "Internal")
    sensitivity = sensitivity_map.get(sensitivity_input, SensitivityEnum.SENSITITY_INTERNAL)
    
    classification = DataProductClassification(
        sensitivity=sensitivity,
        personal=excel_data.get("Personal", "No").lower() == "yes",
        geo_location_access=None,
        regulatory_flags=None,
        certifications=None,
        approval=excel_data.get("Lifecycle Status", ""),
    )
    
    usage = DataProductUsage(
        users=None if not excel_data.get("Users") else str(excel_data.get("Users", "")).split(","),
        systems=int(excel_data.get("Systems", 0)) if excel_data.get("Systems") else None,
        usecases=None if not excel_data.get("Usecases") else excel_data.get("Usecases", "").split(","),
    )
    
    # Map lifecycle status enum
    lifecycle_input = excel_data.get("Lifecycle Status", "Production")
    lifecycle_status = lifecycle_map.get(lifecycle_input, LifecycleStatusEnum.PUBLISH_CONSUME)
    
    lifecycle = DataProductLifecycle(
        lifecycle_status=lifecycle_status,
        version=excel_data.get("Version", "1.0"),
        environment=excel_data.get("Environment", "Production"),
        delivery_date=None,
    )
    
    governance = DataProductGovernanceMetadata(
        domain=excel_data.get("Domain", ""),
        sub_domain=excel_data.get("Sub-Domain", ""),
        data_steward=excel_data.get("Data Steward", ""),
        domain_owner=excel_data.get("Source Domain Owner", ""),
    )
    
    ports = DataProductPorts(
        data_product_input_ports=None,
        data_product_output_port=None,
    )
    
    # Create and return model using Pydantic v2 syntax
    return CompleteDataProductModel(
        basic_metadata=basic_metadata,
        business_metadata=business_metadata,
        classification=classification,
        usage=usage,
        lifecycle=lifecycle,
        governance_metadata=governance,
        ports=ports,
    )


def create_data_product_entity(atlas_client, data_product_model, source_systems: list[str] | None = None) -> bool:
    """
    Create a data product entity in Atlas.
    
    Args:
        atlas_client: The Atlas client instance
        data_product_model: The data product model to create
        
    Returns:
        bool: True if creation was successful
    """
    from datetime import datetime, timezone
    from .metadata_models import DatabaseModel, TableModel
    from .service.entity_service import (
        create_data_product_from_model,
        create_database_from_model,
        create_table_from_model,
    )

    # Create a dedicated output port table and attach it to the DataProduct.
    domain = (data_product_model.governance_metadata.domain or "default").strip().lower().replace(" ", "_")
    db_name = f"{domain}_data_products"
    output_table_name = f"{data_product_model.basic_metadata.data_product_name.strip().lower().replace(' ', '_')}_output_port"

    database_model = DatabaseModel(
        database_name=db_name,
        location_uri=f"atlas://scb/{db_name}",
        create_time=datetime.now(timezone.utc),
        description="Auto-created database for data product ports",
    )
    create_database_from_model(atlas_client, database_model)

    output_table = TableModel(
        table_name=output_table_name,
        database_name=db_name,
        description=f"Output port for {data_product_model.basic_metadata.data_product_name}",
    )
    create_table_from_model(
        atlas_client,
        output_table,
        database_qualified_name=database_model.qualified_name,
    )

    input_port_qualified_names = None
    if source_systems:
        input_port_qualified_names = [
            prepare_qualified_name(f"source_systems.{sys}") for sys in source_systems
        ]

    return create_data_product_from_model(
        atlas_client,
        data_product_model,
        input_port_qualified_names=input_port_qualified_names,
        output_port_qualified_name=output_table.qualified_name,
    )


def create_dataset_entity(atlas_client, dataset_names: list[str]) -> bool:
    """
    Create dataset entities in Atlas for the given dataset names.

    Each source-system name is stored as an SCB_Table under a shared
    SCB_Database called 'source_systems'.

    Args:
        atlas_client: The Atlas client instance
        dataset_names: List of dataset names to create

    Returns:
        bool: True if creation was successful
    """
    from datetime import datetime, timezone
    from .metadata_models import DatabaseModel, TableModel
    from .service.entity_service import create_database_from_model, create_table_from_model

    # Create (or ensure) the shared parent database for source-system datasets
    db_name = "source_systems"
    database_model = DatabaseModel(
        database_name=db_name,
        location_uri=f"atlas://scb/{db_name}",
        create_time=datetime.now(timezone.utc),
        description="Auto-created database for source system datasets",
    )
    create_database_from_model(atlas_client, database_model)

    for name in dataset_names:
        table_model = TableModel(
            table_name=name,
            database_name=db_name,
            description=f"Source system dataset: {name}",
        )
        create_table_from_model(
            atlas_client,
            table_model,
            database_qualified_name=database_model.qualified_name,
        )

    return True


def create_process_entity(
    atlas_client,
    source_systems: list[str],
    data_product_name: str,
    description=None,
    domain: str = "default",
) -> bool:
    """
    Create a process entity linking source systems to a data product.

    Args:
        atlas_client: The Atlas client instance
        source_systems: List of source system names
        data_product_name: Name of the data product
        description: Optional process description

    Returns:
        bool: True if creation was successful
    """
    from .metadata_models import ProcessModel
    from .service.entity_service import create_process_from_model

    # Process 1: source system tables -> data product
    ingest_process_name = f"{data_product_name}_ingest_process"
    ingest_process = ProcessModel(
        process_name=ingest_process_name,
        query_id=ingest_process_name,
        query_text=description or f"Ingest lineage process for {data_product_name}",
    )

    input_refs = [("SCB_Table", prepare_qualified_name(f"source_systems.{sys}")) for sys in source_systems]
    data_product_qn = prepare_qualified_name(data_product_name)
    ingest_output_refs = [("SCB_DataProduct", data_product_qn)]

    create_process_from_model(
        atlas_client,
        ingest_process,
        input_refs=input_refs,
        output_refs=ingest_output_refs,
    )

    # Process 2: data product -> output port table
    domain_slug = (domain or "default").strip().lower().replace(" ", "_")
    dp_slug = data_product_name.strip().lower().replace(" ", "_")
    output_table_qn = prepare_qualified_name(f"{domain_slug}_data_products.{dp_slug}_output_port")

    publish_process_name = f"{data_product_name}_publish_process"
    publish_process = ProcessModel(
        process_name=publish_process_name,
        query_id=publish_process_name,
        query_text=f"Publish lineage process for {data_product_name}",
    )

    publish_input_refs = [("SCB_DataProduct", data_product_qn)]
    publish_output_refs = [("SCB_Table", output_table_qn)]

    return create_process_from_model(
        atlas_client,
        publish_process,
        input_refs=publish_input_refs,
        output_refs=publish_output_refs,
    )
