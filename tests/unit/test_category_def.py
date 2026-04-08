from unittest import TestCase
from scb_atlas.atlas.atlas_type_def.base import (
    BaseEnumCategory, BaseStructCategory, BaseClassificationCategory, BaseEntityCategory, BaseRelationshipCategory
)


def test_enum_definition_is_created_correctly():

    test_enum = BaseEnumCategory(
        atlas_name="TestEnum",
        atlas_description="A Test Enum for Atlas",
        element_defs=[
            { "value": "Choice One", "ordinal": 1 },
            { "value": "Choice Two", "ordinal": 2 }
        ]
    )

    test_enum_atlas_def = test_enum.prepare_atlas_type_definition()

    TestCase().assertDictEqual( 
        {
            "name": "TestEnum",
            "description": "A Test Enum for Atlas",
            "category": "ENUM",
            "typeVersion": "1.0",
            "elementDefs": [
                { "value": "Choice One", "ordinal": 1 },
                { "value": "Choice Two", "ordinal": 2 }
            ]
        },
        test_enum_atlas_def
    )

def test_struct_definition_is_created_correctly():

    test_struct = BaseStructCategory(
        atlas_name="TestStruct",
        attributes=[
            { "name": "attrib_A", "displayName": "Attrib A", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
            { "name": "attrib_B", "displayName": "Attrib B", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        ]
    )

    test_struct_atlas_def = test_struct.prepare_atlas_type_definition()

    TestCase().assertDictEqual( 
        {
            "name": "TestStruct",
            "category": "STRUCT",
            "typeVersion": "1.0",
            "attributeDefs": [
                { "name": "attrib_A", "displayName": "Attrib A", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
                { "name": "attrib_B", "displayName": "Attrib B", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
            ]
        },
        test_struct_atlas_def
    )

def test_classification_definition_is_created_correctly():

    test_classification = BaseClassificationCategory(
        atlas_name="TestClassification"
    )

    test_classification_atlas_def = test_classification.prepare_atlas_type_definition()

    TestCase().assertDictEqual( 
        {
            "name": "TestClassification",
            "category": "CLASSIFICATION",
            "typeVersion": "1.0",
        },
        test_classification_atlas_def
    )

def test_entity_definition_is_created_correctly():

    test_entity = BaseEntityCategory(
        atlas_name="TestEntity",
        display_name="Test Entity",
        super_types = ["Type 1", "Type 2"],
        attributes= [
            { "name": "attrib_A", "displayName": "Attrib A", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
            { "name": "attrib_B", "displayName": "Attrib B", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
        ]
    )

    test_entity_atlas_def = test_entity.prepare_atlas_type_definition()

    TestCase().assertDictEqual( 
        {
            "name": "TestEntity",
            "qualifiedName": "TestEntity",
            "displayName": "Test Entity",
            "superTypes": ["Type 1", "Type 2"],
            "category": "ENTITY",
            "typeVersion": "1.0",
            "attributeDefs": [
                { "name": "attrib_A", "displayName": "Attrib A", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
                { "name": "attrib_B", "displayName": "Attrib B", "typeName": "string", "cardinality": "SINGLE", "isOptional": True, "isUnique": False, "isIndexable": False },
            ]
        },
        test_entity_atlas_def
    )

def test_relationship_definition_is_created_correctly():

    test_relation = BaseRelationshipCategory(
        atlas_name="TestRelation",
        relationship_category="ACategory",
        enddef1={"attr1": "value1"},
        enddef2={"attr2": "value2"}
    )

    test_relation_atlas_def = test_relation.prepare_atlas_type_definition()

    print(test_relation_atlas_def)

    TestCase().assertDictEqual( 
        {
            "name": "TestRelation",
            "category": "RELATIONSHIP",
            "relationshipCategory": "ACategory",
            "propagateTags": "NONE",
            "typeVersion": "1.0",
            "endDef1": {"attr1": "value1"},
            "endDef2": {"attr2": "value2"}
        },
        test_relation_atlas_def
    )