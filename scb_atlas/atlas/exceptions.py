"""
Custom exceptions for Atlas module operations.
"""


class AtlasConnectionError(Exception):
    """Raised when Atlas client cannot connect"""
    pass


class AtlasAuthenticationError(Exception):
    """Raised when Atlas authentication fails"""
    pass


class EntityTypeNotFoundError(Exception):
    """Raised when requested entity type is not found"""
    pass


class EntityCreationError(Exception):
    """Raised when entity creation fails"""
    pass


class EntityDeletionError(Exception):
    """Raised when entity deletion fails"""
    pass


class TypeCreationError(Exception):
    """Raised when type creation fails"""
    pass