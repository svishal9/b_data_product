
from .base import (
    BaseCategory,
    BaseClassificationCategory,
    BaseEnumCategory,
    BaseEntityCategory,
    BaseRelationshipCategory,
    BaseStructCategory
)

from .scb_classifications import all_classifications, classification_names
from .scb_entity import all_entities, entity_names
from .scb_enums import all_enums, enum_names
from .scb_structs import all_structs, struct_names
from .scb_relationships import all_relationships, relationship_names

from .utility import prepare_qualified_name

all_type_names = relationship_names + entity_names + struct_names + enum_names + classification_names

__all__ = [
    "BaseCategory",
    "BaseClassificationCategory",
    "BaseEnumCategory",
    "BaseEntityCategory",
    "BaseRelationshipCategory",
    "BaseStructCategory",
    "all_classifications",
    "classification_names",
    "all_entities",
    "entity_names",
    "all_enums",
    "enum_names",
    "all_structs",
    "struct_names",
    "all_relationships",
    "relationship_names",
    "prepare_qualified_name",
    "all_type_names",
    "all_types",
]


all_types = {
    "classificationDefs": all_classifications,
    "enumDefs": all_enums,
    "businessMetadataDefs": [],
    "structDefs": all_structs,
    "relationshipDefs": all_relationships,
    "entityDefs": all_entities
}