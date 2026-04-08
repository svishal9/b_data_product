from typing import Any
import logging


from apache_atlas.client.base_client import AtlasClient
from apache_atlas.utils import type_coerce
from apache_atlas.model.typedef import AtlasTypesDef

from ..exceptions import TypeCreationError

logger = logging.getLogger(__name__)


def _is_immutable_relationship_update_error(error: Exception) -> bool:
    """Detect Atlas errors raised when relationship endpoints are changed via update."""
    message = str(error)
    return "invalid update for relationshipDef" in message


def _new_empty_types_def() -> AtlasTypesDef:
    """Create an empty AtlasTypesDef with all collections initialized."""
    type_def = AtlasTypesDef()
    type_def.enumDefs = []
    type_def.structDefs = []
    type_def.classificationDefs = []
    type_def.entityDefs = []
    type_def.relationshipDefs = []
    type_def.businessMetadataDefs = []
    return type_def

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

    Existing types are updated via PUT (not skipped) so that attribute-level
    changes — such as removing a uniqueness constraint — are applied to a live
    cluster without having to delete and recreate entities.

    Args:
        type_defs (dict): The type definitions to create or update.
        atlas_client (AtlasClient): The client used to interact with Apache Atlas.

    Returns:
        dict: A dictionary containing the result of the operation.

    Raises:
        TypeCreationError: If there is an error creating or updating type definitions.
    """
    type_def = type_coerce(type_defs, AtlasTypesDef)

    type_to_create = _new_empty_types_def()
    type_to_update = _new_empty_types_def()

    _collections = [
        (type_def.enumDefs,             type_to_create.enumDefs,             type_to_update.enumDefs),
        (type_def.structDefs,           type_to_create.structDefs,           type_to_update.structDefs),
        (type_def.classificationDefs,   type_to_create.classificationDefs,   type_to_update.classificationDefs),
        (type_def.entityDefs,           type_to_create.entityDefs,           type_to_update.entityDefs),
        (type_def.relationshipDefs,     type_to_create.relationshipDefs,     type_to_update.relationshipDefs),
        (type_def.businessMetadataDefs, type_to_create.businessMetadataDefs, type_to_update.businessMetadataDefs),
    ]

    for source_defs, create_list, update_list in _collections:
        if not source_defs:
            continue
        for defn in source_defs:
            if atlas_client.typedef.type_with_name_exists(defn.name):
                logger.info("Type '%s' already exists — will update.", defn.name)
                update_list.append(defn)
            else:
                logger.info("Type '%s' does not exist — will create.", defn.name)
                create_list.append(defn)

    def _has_any(td: AtlasTypesDef) -> bool:
        return any([
            td.enumDefs, td.structDefs, td.classificationDefs,
            td.entityDefs, td.relationshipDefs, td.businessMetadataDefs,
        ])

    result = None

    try:
        if _has_any(type_to_create):
            result = atlas_client.typedef.create_atlas_typedefs(type_to_create)
            logger.info("Type definitions created successfully.")
    except Exception as e:
        logger.error(f"Error creating type definitions: {e}")
        raise TypeCreationError(f"Failed to create type definitions: {e}") from e

    try:
        if _has_any(type_to_update):
            result = atlas_client.typedef.update_atlas_typedefs(type_to_update)
            logger.info("Type definitions updated successfully.")
    except Exception as e:
        if _is_immutable_relationship_update_error(e):
            logger.warning(
                "Atlas rejected relationshipDef endpoint updates; retrying update without relationshipDefs. Error: %s",
                e,
            )

            retry_update = _new_empty_types_def()
            retry_update.enumDefs = type_to_update.enumDefs
            retry_update.structDefs = type_to_update.structDefs
            retry_update.classificationDefs = type_to_update.classificationDefs
            retry_update.entityDefs = type_to_update.entityDefs
            retry_update.businessMetadataDefs = type_to_update.businessMetadataDefs

            skipped_relationships = [rel.name for rel in type_to_update.relationshipDefs]
            if skipped_relationships:
                logger.warning(
                    "Skipped updating existing relationshipDefs due to Atlas immutability: %s",
                    ", ".join(skipped_relationships),
                )

            try:
                if _has_any(retry_update):
                    result = atlas_client.typedef.update_atlas_typedefs(retry_update)
                    logger.info("Type definitions updated successfully (excluding relationshipDefs).")
            except Exception as retry_error:
                logger.error(f"Error updating type definitions after relationshipDef fallback: {retry_error}")
                raise TypeCreationError(f"Failed to update type definitions: {retry_error}") from retry_error
        else:
            logger.error(f"Error updating type definitions: {e}")
            raise TypeCreationError(f"Failed to update type definitions: {e}") from e

    return result
