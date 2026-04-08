
from typing import Any
import logging


from apache_atlas.client.base_client import AtlasClient
from apache_atlas.utils import type_coerce
from apache_atlas.model.typedef import AtlasTypesDef

from ..exceptions import TypeCreationError

logger = logging.getLogger(__name__)

def delete_typedef(atlas_client:AtlasClient, type_name: str) -> None:
    """
    Deletes a type definition from Atlas.

    Args:
        atlas_client: The Atlas client instance.
        type_name (str): The name of the type to delete.

    Raises:
        EntityTypeNotFoundError: If the type does not exist.
        TypeCreationError: If there's an error during deletion.
    """
    try:
        atlas_client.typedef.delete_type_by_name(type_name)
        logger.info(f"Successfully deleted type: {type_name}")
    except Exception as e:
        logger.error(f"Error deleting type {type_name}: {e}")
        raise TypeCreationError(f"Failed to delete type '{type_name}': {e}") from e


def create_typedef(type_defs: dict, atlas_client: AtlasClient) -> Any:

    """
    Create or update type definitions in Apache Atlas using the provided client.

    Args:
        type_defs (dict): The type definitions to create.
        atlas_client (AtlasClient): The client used to interact with Apache Atlas.

    Returns:
        dict: A dictionary containing the result of the type creation/update operation.

    Raises:
        TypeCreationError: If there is an error creating or updating type definitions.
    """
    type_def = type_coerce(type_defs, AtlasTypesDef)

    type_to_create = AtlasTypesDef()

    type_to_create.enumDefs             = []
    type_to_create.structDefs           = []
    type_to_create.classificationDefs   = []
    type_to_create.entityDefs           = []
    type_to_create.relationshipDefs     = []
    type_to_create.businessMetadataDefs = []

    if type_def.enumDefs:
        for enum_def in type_def.enumDefs:
            if atlas_client.typedef.type_with_name_exists(enum_def.name):
                print("Type with name %s already exists. Skipping.", enum_def.name)
            else:
                type_to_create.enumDefs.append(enum_def)

    if type_def.structDefs:
        for struct_def in type_def.structDefs:
            if atlas_client.typedef.type_with_name_exists(struct_def.name):
                print("Type with name %s already exists. Skipping.", struct_def.name)
            else:
                type_to_create.structDefs.append(struct_def)

    if type_def.classificationDefs:
        for classification_def in type_def.classificationDefs:
            if atlas_client.typedef.type_with_name_exists(classification_def.name):
                print("Type with name %s already exists. Skipping.", classification_def.name)
            else:
                type_to_create.classificationDefs.append(classification_def)

    if type_def.entityDefs:
        for entity_def in type_def.entityDefs:
            if atlas_client.typedef.type_with_name_exists(entity_def.name):
                logger.info("Type with name %s already exists. Skipping.", entity_def.name)
            else:
                type_to_create.entityDefs.append(entity_def)

    if type_def.relationshipDefs:
        for relationship_def in type_def.relationshipDefs:
            if atlas_client.typedef.type_with_name_exists(relationship_def.name):
                logger.info("Type with name %s already exists. Skipping.", relationship_def.name)
            else:
                type_to_create.relationshipDefs.append(relationship_def)

    if type_def.businessMetadataDefs:
        for business_metadata_def in type_def.businessMetadataDefs:
            if atlas_client.typedef.type_with_name_exists(business_metadata_def.name):
                logger.info("Type with name %s already exists. Skipping.", business_metadata_def.name)
            else:
                type_to_create.businessMetadataDefs.append(business_metadata_def)

    try:
        result = atlas_client.typedef.create_atlas_typedefs(type_to_create)
        return result
    except Exception as e:
        logger.error(f"Error creating type definitions: {e}")
        raise TypeCreationError(f"Failed to create type definitions: {e}") from e
