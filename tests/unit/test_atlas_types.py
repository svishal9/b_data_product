"""
Tests for SCB Atlas entity type definitions.

Validates that:
- Type definitions are properly structured
- All required attributes are present
- Entity types extend correct base types
- Type definitions are compatible with Atlas
"""

import pytest

from scb_atlas.atlas.atlas_type_def import all_types
from scb_atlas.atlas.atlas_type_def.scb_entity import(
    scb_data_product,
    scb_database,
    scb_table,
    scb_standard_column,
    scb_process
)


class TestTypeDefinitionStructure:
    """Tests for type definition structure validation."""

    def test_type_definitions_contains_all_entity_types(self):
        """Test that type_definitions includes all entity types."""
        entity_types = all_types['entityDefs']

        type_names = [entity['name'] for entity in entity_types]

        assert 'SCB_DataProduct' in type_names
        assert 'SCB_Database' in type_names
        assert 'SCB_Table' in type_names
        assert 'SCB_StandardColumn' in type_names
        assert 'SCB_Process' in type_names

    def test_each_entity_definition_has_required_fields(self):
        """Test that each entity definition has required fields."""
        definitions = [
            [scb_data_product.prepare_atlas_type_definition()],
            [scb_database.prepare_atlas_type_definition()],
            [scb_table.prepare_atlas_type_definition()],
            [scb_standard_column.prepare_atlas_type_definition()],
            [scb_process.prepare_atlas_type_definition()]
        ]

        required_fields = ['name', 'category', 'typeVersion', 'superTypes', 'attributeDefs']

        for def_list in definitions:
            for entity in def_list:
                for field in required_fields:
                    assert field in entity, f"Missing {field} in {entity.get('name', 'unknown')}"

    def test_entity_category_is_entity(self):
        """Test that all entities have category ENTITY or PROCESS."""
        definitions = [
            [scb_data_product.prepare_atlas_type_definition()],
            [scb_database.prepare_atlas_type_definition()],
            [scb_table.prepare_atlas_type_definition()],
            [scb_standard_column.prepare_atlas_type_definition()],
            [scb_process.prepare_atlas_type_definition()]
        ]

        for def_list in definitions:
            for entity in def_list:
                assert entity['category'] in ['ENTITY', 'PROCESS'], f"Invalid category for {entity['name']}"


class TestDatabaseEntityType:
    """Tests for SCB_Database entity type definition."""

    def test_database_entity_extends_dataset(self):
        """Test that SCB_Database extends DataSet."""
        db_entity = [scb_database.prepare_atlas_type_definition()][0]
        assert 'DataSet' in db_entity['superTypes']

    def test_database_entity_has_required_attributes(self):
        """Test that SCB_Database has all required attributes."""
        db_entity = [scb_database.prepare_atlas_type_definition()][0]
        attr_names = [attr['name'] for attr in db_entity['attributeDefs']]

        assert 'database_name' in attr_names
        assert 'locationUri' in attr_names
        assert 'createTime' in attr_names

    def test_database_attributes_are_unique(self):
        """Test that database_name is marked as unique."""
        db_entity = [scb_database.prepare_atlas_type_definition()][0]
        attrs = {attr['name']: attr for attr in db_entity['attributeDefs']}

        assert attrs['database_name']['isUnique'] == True

    def test_database_attributes_types(self):
        """Test that database attributes have correct types."""
        db_entity = [scb_database.prepare_atlas_type_definition()][0]
        attrs = {attr['name']: attr for attr in db_entity['attributeDefs']}

        assert attrs['database_name']['typeName'] == 'string'
        assert attrs['locationUri']['typeName'] == 'string'
        assert attrs['createTime']['typeName'] == 'date'


class TestTableEntityType:
    """Tests for SCB_Table entity type definition."""

    def test_table_entity_extends_dataset(self):
        """Test that SCB_Table extends DataSet."""
        table_entity = [scb_table.prepare_atlas_type_definition()][0]
        assert 'DataSet' in table_entity['superTypes']

    def test_table_entity_has_required_attributes(self):
        """Test that SCB_Table has all required attributes."""
        table_entity = [scb_table.prepare_atlas_type_definition()][0]
        attr_names = [attr['name'] for attr in table_entity['attributeDefs']]

        assert 'table_name' in attr_names
        assert 'temporary' in attr_names

    def test_table_name_is_unique(self):
        """Test that table_name is marked as unique."""
        table_entity = [scb_table.prepare_atlas_type_definition()][0]
        attrs = {attr['name']: attr for attr in table_entity['attributeDefs']}

        assert attrs['table_name']['isUnique'] == True

    def test_table_temporary_is_boolean(self):
        """Test that temporary attribute is boolean type."""
        table_entity = [scb_table.prepare_atlas_type_definition()][0]
        attrs = {attr['name']: attr for attr in table_entity['attributeDefs']}

        assert attrs['temporary']['typeName'] == 'boolean'

    def test_table_optional_attributes_are_optional(self):
        """Test that table optional attributes are marked optional."""
        table_entity = [scb_table.prepare_atlas_type_definition()][0]
        attrs = {attr['name']: attr for attr in table_entity['attributeDefs']}

        optional_attrs = ['createTime', 'tableType', 'temporary', 'serde1', 'serde2', 'description']

        for attr_name in optional_attrs:
            if attr_name in attrs:
                assert attrs[attr_name]['isOptional'] == True


class TestColumnEntityType:
    """Tests for SCB_StandardColumn entity type definition."""

    def test_column_entity_extends_dataset(self):
        """Test that SCB_StandardColumn extends DataSet."""
        col_entity = [scb_standard_column.prepare_atlas_type_definition()][0]
        assert 'DataSet' in col_entity['superTypes']

    def test_column_entity_has_required_attributes(self):
        """Test that SCB_StandardColumn has all required attributes."""
        col_entity = [scb_standard_column.prepare_atlas_type_definition()][0]
        attr_names = [attr['name'] for attr in col_entity['attributeDefs']]

        assert 'field_name' in attr_names
        assert 'data_type' in attr_names

    def test_column_attributes_types(self):
        """Test that column attributes have correct types."""
        col_entity = [scb_standard_column.prepare_atlas_type_definition()][0]
        attrs = {attr['name']: attr for attr in col_entity['attributeDefs']}

        assert attrs['field_name']['typeName'] == 'string'
        assert attrs['data_type']['typeName'] == 'string'

    def test_column_optional_attributes_are_optional(self):
        """Test that column optional attributes are optional."""
        col_entity = [scb_standard_column.prepare_atlas_type_definition()][0]
        attrs = {attr['name']: attr for attr in col_entity['attributeDefs']}

        optional_attrs = ['data_type', 'description', 'position']

        for attr_name in optional_attrs:
            if attr_name in attrs:
                assert attrs[attr_name]['isOptional'] == True

    def test_column_field_name_not_globally_unique(self):
        """Test that field_name is NOT globally unique (allows same column name in different tables/data products).
        
        This is a regression test for the bug where field_name was marked as unique,
        causing "violates uniqueness constraint" errors when creating columns with
        the same name in different data products.
        
        Uniqueness should be enforced at the qualifiedName level (inherited from DataSet),
        not at the field_name level, to allow semantic reuse of column names across tables.
        """
        col_entity = [scb_standard_column.prepare_atlas_type_definition()][0]
        attrs = {attr['name']: attr for attr in col_entity['attributeDefs']}

        # field_name should NOT be unique globally
        assert attrs['field_name']['isUnique'] == False, \
            "field_name must not be globally unique to allow same column name in different tables"


class TestProcessEntityType:
    """Tests for SCB_Process entity type definition."""

    def test_process_entity_extends_process(self):
        """Test that SCB_Process extends Process."""
        proc_entity = [scb_process.prepare_atlas_type_definition()][0]
        assert 'Process' in proc_entity['superTypes']

    def test_process_entity_has_required_attributes(self):
        """Test that SCB_Process has all required attributes."""
        proc_entity = [scb_process.prepare_atlas_type_definition()][0]
        attr_names = [attr['name'] for attr in proc_entity['attributeDefs']]

        assert 'process_name' in attr_names
        assert 'queryId' in attr_names
        assert 'queryText' in attr_names

    def test_process_required_attributes_are_not_optional(self):
        """Test that required process attributes are not optional."""
        proc_entity = [scb_process.prepare_atlas_type_definition()][0]
        attrs = {attr['name']: attr for attr in proc_entity['attributeDefs']}

        assert attrs['process_name']['isOptional'] == False
        assert attrs['queryId']['isOptional'] == False
        assert attrs['queryText']['isOptional'] == False

    def test_process_unique_attributes(self):
        """Test that process_name and queryId are unique."""
        proc_entity = [scb_process.prepare_atlas_type_definition()][0]
        attrs = {attr['name']: attr for attr in proc_entity['attributeDefs']}

        assert attrs['process_name']['isUnique'] == True
        assert attrs['queryId']['isUnique'] == True

    def test_process_timestamp_types(self):
        """Test that process timestamps are long type."""
        proc_entity = [scb_process.prepare_atlas_type_definition()][0]
        attrs = {attr['name']: attr for attr in proc_entity['attributeDefs']}

        if 'startTime' in attrs:
            assert attrs['startTime']['typeName'] == 'long'
        if 'endTime' in attrs:
            assert attrs['endTime']['typeName'] == 'long'


class TestDataProductEntityType:
    """Tests for SCB_DataProduct entity type definition."""

    def test_data_product_entity_extends_dataset(self):
        """Test that SCB_DataProduct extends DataSet."""
        dp_entity = [scb_data_product.prepare_atlas_type_definition()][0]
        assert 'DataSet' in dp_entity['superTypes']

    def test_data_product_name_is_unique(self):
        """Test that data_product_name is marked as unique."""
        dp_entity = [scb_data_product.prepare_atlas_type_definition()][0]
        attrs = {attr['name']: attr for attr in dp_entity['attributeDefs']}

        if 'data_product_name' in attrs:
            assert attrs['data_product_name']['isUnique'] == True


class TestTypeDefinitionMetadata:
    """Tests for type definition metadata."""

    def test_all_types_have_version(self):
        """Test that all types have typeVersion."""
        all_defs = all_types['entityDefs']

        for entity in all_defs:
            assert 'typeVersion' in entity
            assert entity['typeVersion'] == '1.0'

    def test_all_attributes_have_cardinality(self):
        """Test that all attributes specify cardinality."""
        all_defs = all_types['entityDefs']

        for entity in all_defs:
            for attr in entity.get('attributeDefs', []):
                assert 'cardinality' in attr
                assert attr['cardinality'] in ['SINGLE', 'LIST']

    def test_all_attributes_have_index_info(self):
        """Test that all attributes specify indexing."""
        all_defs = all_types['entityDefs']

        for entity in all_defs:
            for attr in entity.get('attributeDefs', []):
                assert 'isIndexable' in attr
                assert isinstance(attr['isIndexable'], bool)


class TestEnumDefinitions:
    """Tests for ENUM type definitions."""

    def test_enum_definitions_exist(self):
        """Test that enum definitions are present."""
        enum_definitions = all_types["enumDefs"]
        assert len(enum_definitions) > 0

    def test_all_enums_have_element_defs(self):
        """Test that all enums have elementDefs."""
        enum_definitions = all_types["enumDefs"]
        for enum in enum_definitions:
            assert 'elementDefs' in enum
            assert len(enum['elementDefs']) > 0

    def test_enum_elements_have_value_and_ordinal(self):
        """Test that enum elements have value and ordinal."""
        enum_definitions = all_types["enumDefs"]
        for enum in enum_definitions:
            for element in enum['elementDefs']:
                assert 'value' in element
                assert 'ordinal' in element


class TestStructDefinitions:
    """Tests for STRUCT type definitions."""

    def test_struct_definitions_exist(self):
        """Test that struct definitions are present."""
        struct_definitions = all_types["structDefs"]
        assert len(struct_definitions) > 0

    def test_all_structs_are_category_struct(self):
        """Test that all structs have category STRUCT."""
        struct_definitions = all_types["structDefs"]
        for struct in struct_definitions:
            assert struct['category'] == 'STRUCT'

    def test_all_structs_have_attribute_defs(self):
        """Test that all structs have attributeDefs."""
        struct_definitions = all_types["structDefs"]
        for struct in struct_definitions:
            assert 'attributeDefs' in struct
            assert len(struct['attributeDefs']) > 0


class TestClassificationDefinitions:
    """Tests for CLASSIFICATION type definitions."""

    def test_classification_definitions_exist(self):
        """Test that classification definitions are present."""
        classification_definitions = all_types["classificationDefs"]
        assert len(classification_definitions) > 0

    def test_all_classifications_are_category_classification(self):
        """Test that all classifications have category CLASSIFICATION."""
        classification_definitions = all_types["classificationDefs"]
        for classification in classification_definitions:
            assert classification['category'] == 'CLASSIFICATION'


class TestTypeDefinitionConsistency:
    """Tests for consistency across type definitions."""

    def test_no_duplicate_entity_type_names(self):
        """Test that there are no duplicate entity type names."""
        all_defs = all_types['entityDefs']
        type_names = [entity['name'] for entity in all_defs]

        assert len(type_names) == len(set(type_names)), "Duplicate type names found"

    def test_no_duplicate_enum_names(self):
        """Test that there are no duplicate enum names."""
        enum_names = [enum['name'] for enum in all_types['enumDefs']]

        assert len(enum_names) == len(set(enum_names)), "Duplicate enum names found"

    def test_no_duplicate_struct_names(self):
        """Test that there are no duplicate struct names."""
        struct_names = [struct['name'] for struct in all_types['structDefs']]

        assert len(struct_names) == len(set(struct_names)), "Duplicate struct names found"

    def test_attribute_names_unique_within_type(self):
        """Test that attribute names are unique within each type."""
        all_defs = all_types['entityDefs']

        for entity in all_defs:
            attr_names = [attr['name'] for attr in entity.get('attributeDefs', [])]
            assert len(attr_names) == len(set(attr_names)), f"Duplicate attributes in {entity['name']}"


class TestTypeDefinitionAttributeValidation:
    """Tests for attribute definition validation."""

    def test_all_attributes_have_type_name(self):
        """Test that all attributes specify typeName."""
        all_defs = all_types['entityDefs']

        for entity in all_defs:
            for attr in entity.get('attributeDefs', []):
                assert 'typeName' in attr, f"Missing typeName in {entity['name']}.{attr.get('name')}"

    def test_all_attributes_have_optional_flag(self):
        """Test that all attributes specify isOptional."""
        all_defs = all_types['entityDefs']

        for entity in all_defs:
            for attr in entity.get('attributeDefs', []):
                assert 'isOptional' in attr, f"Missing isOptional in {entity['name']}.{attr.get('name')}"

    def test_all_attributes_have_unique_flag(self):
        """Test that all attributes specify isUnique."""
        all_defs = all_types['entityDefs']

        for entity in all_defs:
            for attr in entity.get('attributeDefs', []):
                assert 'isUnique' in attr, f"Missing isUnique in {entity['name']}.{attr.get('name')}"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

