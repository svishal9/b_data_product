"""
SCB Atlas module provides API wrappers for Apache Atlas integration.
"""

from .atlas import (
    create_atlas_client,
    delete_entity,
    delete_typedef,
    create_typedef,
    AtlasConnectionError,
    AtlasAuthenticationError,
    EntityTypeNotFoundError,
    EntityCreationError,
    EntityDeletionError,
    TypeCreationError,
    validate_metadata_workbook,
    #parse_workbook_to_data_products,
    parse_master_schema_workbook_to_data_products,
    create_data_products_from_workbook,
)


from .atlas.atlas_settings import settings as atlas_settings

__all__ = [
    # utility functions
    "convert_to_atlas_model",
    # Atlas client functions
    "create_atlas_client",
    "delete_entity",
    "delete_typedef",
    "create_typedef",
    # Atlas settings
    "atlas_settings",
    # Custom exceptions
    "AtlasConnectionError",
    "AtlasAuthenticationError",
    "EntityTypeNotFoundError",
    "EntityCreationError",
    "EntityDeletionError",
    "TypeCreationError",
    "validate_metadata_workbook",
    #"parse_workbook_to_data_products",
    "parse_master_schema_workbook_to_data_products"
    "create_data_products_from_workbook",
]