import logging
from typing import Optional

from apache_atlas.client.base_client import AtlasClient
from apache_atlas.model.enums import EntityOperation
from apache_atlas.model.instance import AtlasEntityWithExtInfo
from apache_atlas.utils import type_coerce

from .discovery_service import dsl_search

from ..exceptions import EntityCreationError, EntityDeletionError
from ..metadata_models import (
    DatabaseModel,
    TableModel,
    #ColumnModel,
    StandardColumnModel,
    ProcessModel,
    CompleteDataProductModel,
)

logger = logging.getLogger(__name__)

def delete_entity(atlas_client: AtlasClient, guids: list[str]) -> bool:
    """
    Deletes entities from Atlas using the provided GUIDs.

    Args:
        atlas_client (AtlasClient): The Atlas client instance.
        guids (list[str]): A list of entity GUIDs to be deleted.

    Returns:
        bool: True if the entities were successfully purged, False otherwise.

    Raises:
        EntityDeletionError: If there's an error during deletion.
    """
    try:
        atlas_client.entity.delete_entities_by_guids(guids)
        response = atlas_client.entity.purge_entities_by_guids(guids)

        if response is not None:
            logger.info(f"Successfully purged entities: {guids}")
            return True

        logger.warning(f"Failed to purge entities: {guids}")
        return False
    except Exception as e:
        logger.error(f"Error deleting entities {guids}: {e}")
        raise EntityDeletionError(f"Failed to delete entities: {e}") from e

def get_entity_guid_from_attribute(atlas_client: AtlasClient, type_name: str, unique_attribute: dict) -> str | None:

    """
    Retrieves the GUID of an entity based on a unique attribute.

    Args:
        atlas_client (AtlasClient): The Atlas client instance.
        type_name (str): The type name of the entity.
        unique_attribute (dict): A dictionary representing the unique attribute to search for.

    Returns:
        str: The GUID of the entity if found, None otherwise.
    """
        
    response = atlas_client.entity.get_entities_by_attribute(type_name, [unique_attribute])

    if response and response["entities"] and len(response["entities"]) > 0:
        logger.info(f"Found entity GUID: {response['entities'][0]['guid']}")
        return response["entities"][0]["guid"]

    logger.warning(f"No entity found with attributes: {unique_attribute}")
    return None


def _create_entity_in_atlas(atlas_client: AtlasClient, entity_attribute: dict):
    """
    Creates a new entity in Atlas. If the entity already exists (based on the unique attribute),
    it will be updated instead.

    Args:
        atlas_client (AtlasClient): The Atlas client instance.
        entity_attribute (dict): A dictionary representing the attributes of the entity to be created.

    Returns:
        None

    Raises:
        EntityCreationError: If there's an error during entity creation.
    """

    entity = type_coerce(entity_attribute, AtlasEntityWithExtInfo)

    try:
        response = atlas_client.entity.create_entity(entity)
        guid = None
        header_list = None

        if response and response.mutatedEntities:
            if EntityOperation.CREATE.name in response.mutatedEntities:
                header_list = response.mutatedEntities[EntityOperation.CREATE.name]
            elif EntityOperation.UPDATE.name in response.mutatedEntities:
                header_list = response.mutatedEntities[EntityOperation.UPDATE.name]

            if header_list and len(header_list) > 0:
                guid = header_list[0].guid

        elif response and response.guidAssignments:
            if entity.entity is not None and entity.entity.guid is not None:
                in_guid = entity.entity.guid
            else:
                in_guid = None

            if in_guid:
                guid = response.guidAssignments.get(in_guid)

            # Atlas may return a different temporary GUID key than the one on the outgoing payload.
            if not guid:
                guid = next(iter(response.guidAssignments.values()), None)

        if guid:
            entity.entity.guid = guid
            logger.info(f"Successfully created/updated entity with GUID: {guid}")
        else:
            logger.error("Failed to get GUID after entity creation")

    except Exception as e:
        logger.exception(f"Failed to create entity: {entity}")
        raise EntityCreationError(f"Failed to create entity: {e}") from e



# ============================================================================
# PYDANTIC MODEL-BASED ENTITY CREATION FUNCTIONS
# ============================================================================

def create_database_from_model(atlas_client: AtlasClient, database_model: DatabaseModel) -> bool:
    """
    Creates a database entity in Atlas using a Pydantic DatabaseModel.

    Args:
        atlas_client (AtlasClient): The Atlas client instance.
        database_model (DatabaseModel): The database model with all required data.

    Returns:
        bool: True if the entity was successfully created, False otherwise.

    Raises:
        EntityCreationError: If there's an error during entity creation.
    """
    entity_attribute = {
        "entity": database_model.to_atlas_entity()
    }
    _create_entity_in_atlas(atlas_client, entity_attribute)
    return True


def create_table_from_model(atlas_client: AtlasClient, table_model: TableModel, 
                           database_qualified_name: Optional[str] = None) -> bool:
    """
    Creates a table entity in Atlas using a Pydantic TableModel.

    Args:
        atlas_client (AtlasClient): The Atlas client instance.
        table_model (TableModel): The table model with all required data.
        database_qualified_name (str, optional): Qualified name of parent database for relationship.

    Returns:
        bool: True if the entity was successfully created, False otherwise.

    Raises:
        EntityCreationError: If there's an error during entity creation.
    """
    entity_attribute = {
        "entity": table_model.to_atlas_entity()
    }
    
    # Add relationship to parent database if provided
    if database_qualified_name:
        entity_attribute["entity"].setdefault("relationshipAttributes", {})["database"] = {
            "typeName": "SCB_Database",
            "uniqueAttributes": {"qualifiedName": database_qualified_name},
        }
    
    _create_entity_in_atlas(atlas_client, entity_attribute)
    return True


def create_column_from_model(atlas_client: AtlasClient, column_model: StandardColumnModel,
                            table_qualified_name: Optional[str] = None) -> bool:
    """
    Creates a column entity in Atlas using a Pydantic StandardColumnModel.

    Args:
        atlas_client (AtlasClient): The Atlas client instance.
        column_model (ColumnModel): The column model with all required data.
        table_qualified_name (str, optional): Qualified name of parent table for relationship.

    Returns:
        bool: True if the entity was successfully created, False otherwise.

    Raises:
        EntityCreationError: If there's an error during entity creation.
    """
    entity_attribute = {
        "entity": column_model.to_atlas_entity()
    }
    
    # Add relationship to parent table if provided
    if table_qualified_name:
        entity_attribute["entity"].setdefault("relationshipAttributes", {})["table"] = {
            "typeName": "SCB_Table",
            "uniqueAttributes": {"qualifiedName": table_qualified_name},
        }
    
    _create_entity_in_atlas(atlas_client, entity_attribute)
    return True


def create_process_from_model(atlas_client: AtlasClient, process_model: ProcessModel,
                             input_refs: Optional[list[tuple[str, str]]] = None,
                             output_refs: Optional[list[tuple[str, str]]] = None) -> bool:
    """
    Creates a process entity in Atlas using a Pydantic ProcessModel.

    Args:
        atlas_client (AtlasClient): The Atlas client instance.
        process_model (ProcessModel): The process model with all required data.
        input_refs (list[tuple[str, str]], optional): Input entity references as (type_name, qualified_name).
        output_refs (list[tuple[str, str]], optional): Output entity references as (type_name, qualified_name).

    Returns:
        bool: True if the entity was successfully created, False otherwise.

    Raises:
        EntityCreationError: If there's an error during entity creation.
    """
    entity_attribute = {
        "entity": process_model.to_atlas_entity()
    }
    
    # Add input/output relationships
    relationship_attributes = entity_attribute["entity"].setdefault("relationshipAttributes", {})
    
    if input_refs:
        relationship_attributes["inputs"] = [
            {
                "typeName": type_name,
                "uniqueAttributes": {"qualifiedName": qualified_name},
            }
            for type_name, qualified_name in input_refs
        ]
    
    if output_refs:
        relationship_attributes["outputs"] = [
            {
                "typeName": type_name,
                "uniqueAttributes": {"qualifiedName": qualified_name},
            }
            for type_name, qualified_name in output_refs
        ]
    
    _create_entity_in_atlas(atlas_client, entity_attribute)
    return True


def create_data_product_from_model(atlas_client: AtlasClient, data_product_model: CompleteDataProductModel,
                                  input_port_qualified_names: Optional[list[str]] = None,
                                  output_port_qualified_name: Optional[str] = None) -> bool:
    """
    Creates a data product entity in Atlas using a Pydantic CompleteDataProductModel.

    Args:
        atlas_client (AtlasClient): The Atlas client instance.
        data_product_model (CompleteDataProductModel): The complete data product model.
        input_port_qualified_names (list[str], optional): Qualified names for input port tables.
        output_port_qualified_name (str, optional): Qualified name for output port table.

    Returns:
        bool: True if the entity was successfully created, False otherwise.

    Raises:
        EntityCreationError: If there's an error during entity creation.
    """
    entity_attribute = {
        "entity": data_product_model.to_atlas_entity()
    }
    
    # Add port relationships
    relationship_attributes = entity_attribute["entity"].setdefault("relationshipAttributes", {})
    
    if input_port_qualified_names:
        relationship_attributes["input_port"] = [
            {
                "typeName": "SCB_Table",
                "uniqueAttributes": {"qualifiedName": qn},
            }
            for qn in input_port_qualified_names
        ]
    
    if output_port_qualified_name:
        relationship_attributes["output_port"] = {
            "typeName": "SCB_Table",
            "uniqueAttributes": {"qualifiedName": output_port_qualified_name},
        }
    
    _create_entity_in_atlas(atlas_client, entity_attribute)
    
    # Add labels if applicable
    entity_retrieved = dsl_search(
        atlas_client=atlas_client,
        names=[data_product_model.basic_metadata.data_product_name],
        type_name="SCB_DataProduct"
    )
    
    if entity_retrieved and len(entity_retrieved) == 1:
        guid = entity_retrieved[0]["guid"]
        labels = []
        if data_product_model.basic_metadata.data_product_category:
            labels.append(data_product_model.basic_metadata.data_product_category)
        tags = []
        if data_product_model.basic_metadata.tags:
            tags.extend(data_product_model.basic_metadata.tags)
        if tags:
            labels.extend(tags)
        
        if labels:
            atlas_client.entity.add_labels_by_guid(entity_guid=guid, labels=labels)
    
    return True
