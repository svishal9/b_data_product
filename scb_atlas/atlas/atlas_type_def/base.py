import logging
from abc import ABC, abstractmethod

logger = logging.getLogger(__name__)

class BaseCategory(ABC):

    def __init__(self, atlas_category: str, atlas_name: str):
        self.atlas_category = atlas_category
        self.atlas_name = atlas_name

    def get_atlas_category(self):
        return self.atlas_category

    @abstractmethod
    def prepare_atlas_type_definition(self):
        pass

       
class BaseEnumCategory(BaseCategory):

    def __init__(
        self,
        atlas_name: str,
        atlas_description: str,
        atlas_type_version: str = "1.0",
        element_defs: list[dict] | None = None
    ):
        super().__init__(
            atlas_category="ENUM",
            atlas_name=atlas_name
        )

        self.atlas_description=atlas_description
        self.atlas_type_version = atlas_type_version
        self.element_defs = element_defs
    
    def add_element(self, element: dict):
        if self.element_defs is None:
            self.element_defs = dict()

        self.element_defs[element["value"]] = element
    
    def prepare_atlas_type_definition(self):
        
        return {
            "name"       : self.atlas_name,
            "description": self.atlas_description,
            "category":    self.atlas_category,
            "typeVersion": self.atlas_type_version,
            "elementDefs": self.element_defs
        }


class BaseClassificationCategory(BaseCategory):

    def __init__(
        self,
        atlas_name: str,
        atlas_type_version: str = "1.0"
    ):
        super().__init__(
            atlas_name=atlas_name,
            atlas_category="CLASSIFICATION",
        )
        self.atlas_type_version = atlas_type_version
    
    def prepare_atlas_type_definition(self):
        return {
            "name": self.atlas_name,
            "category": self.atlas_category,
            "typeVersion": "1.0"
        }

class BaseStructCategory(BaseCategory):

    def __init__(
        self,
        atlas_name: str,
        atlas_type_version: str = "1.0",
        attributes: dict | None = None
    ):
        super().__init__(
            atlas_category="STRUCT",
            atlas_name=atlas_name,
        )
        self.atlas_type_version = atlas_type_version
        self.attributes = attributes


    def add_attribute(self, attribute: dict):
        if self.attributes is None:
            self.attributes = []

        self.attributes.append(attribute)
    
    def prepare_atlas_type_definition(self):
        return {
            "name": self.atlas_name,
            "category": self.atlas_category,
            "typeVersion": self.atlas_type_version,
            "attributeDefs": self.attributes
        }

class BaseEntityCategory(BaseCategory):

    def __init__(
        self,
        atlas_name: str,
        display_name: str,
        super_types: list[str] = ["DataSet"],
        atlas_type_version: str = "1.0",
        attributes: list[dict] | None = None
    ):
        super().__init__(
            atlas_category="ENTITY",
            atlas_name=atlas_name
        )
        self.display_name = display_name
        self.super_types = super_types
        self.atlas_type_version = atlas_type_version
        self.attributes = attributes

    def add_attribute(self, attribute: dict):

        if self.attributes is None:
            self.attributes = []
        self.attributes.append(attribute)
    
    def prepare_atlas_type_definition(self):
        
        return {

            "name": self.atlas_name,
            "qualifiedName": self.atlas_name,
            "displayName": self.display_name,
            "superTypes":  self.super_types,
            "category":   self.atlas_category,
            "typeVersion": self.atlas_type_version,
            "attributeDefs": self.attributes
        }
    
class BaseRelationshipCategory(BaseCategory):

    def __init__(
        self,
        atlas_name: str,
        relationship_category: str = "COMPOSITION",
        atlas_type_version: str = "1.0",
        enddef1: dict | None = None,
        enddef2: dict | None = None
    ):
        super().__init__(
            atlas_name=atlas_name,
            atlas_category="RELATIONSHIP"
        )
        self.atlas_type_version = atlas_type_version
        self.relationship_category = relationship_category
        self.enddef1 = enddef1
        self.enddef2 = enddef2

    def add_ends(self, enddef1: dict, enddef2):
        self.enddef1 = enddef1
        self.enddef2 = enddef2
    
    def prepare_atlas_type_definition(self):
        return {
            "name": self.atlas_name,
            "category": self.atlas_category,
            "typeVersion": self.atlas_type_version,
            "relationshipCategory": self.relationship_category,
            "propagateTags": "NONE",
            "endDef1": self.enddef1,
            "endDef2": self.enddef2
        }