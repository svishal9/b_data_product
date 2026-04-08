"""Backward-compatible imports for Atlas metadata models.

Prefer importing from `scb_atlas.atlas.metadata_models`.
"""

from .metadata_models import (
    ColumnModel,
    CompleteDataProductModel,
    DataProductBasicMetadata,
    DataProductBusinessMetadata,
    DataProductClassification,
    DataProductGovernanceMetadata,
    DataProductLifecycle,
    DataProductPorts,
    DataProductSchemaField,
    DataProductUsage,
    DatabaseModel,
    LifecycleStatusEnum,
    PIIEnum,
    ProcessModel,
    TableModel,
    TableTypeEnum,
)

__all__ = [
    "ColumnModel",
    "CompleteDataProductModel",
    "DataProductBasicMetadata",
    "DataProductBusinessMetadata",
    "DataProductClassification",
    "DataProductGovernanceMetadata",
    "DataProductLifecycle",
    "DataProductPorts",
    "DataProductSchemaField",
    "DataProductUsage",
    "DatabaseModel",
    "LifecycleStatusEnum",
    "PIIEnum",
    "ProcessModel",
    "TableModel",
    "TableTypeEnum",
]
