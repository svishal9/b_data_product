"""
Unit tests for SCB Atlas entity builders and service functions.

Tests the following components:
- DatabaseEntityBuilder
- TableEntityBuilder
- ColumnEntityBuilder
- ProcessEntityBuilder
"""

import pytest
from scb_atlas.atlas.entity_builders import (
    DatabaseEntityBuilder,
    TableEntityBuilder,
    ColumnEntityBuilder,
    ProcessEntityBuilder
)
from scb_atlas.atlas.atlas_type_def import prepare_qualified_name


class TestDatabaseEntityBuilder:
    """Tests for DatabaseEntityBuilder."""

    def test_database_builder_basic_creation(self):
        """Test basic database entity creation."""
        builder = DatabaseEntityBuilder("my_database", "hdfs://data/my_database")
        entity = builder.build()

        assert entity['entity']['typeName'] == 'SCB_Database'
        assert entity['entity']['attributes']['database_name'] == 'my_database'
        assert entity['entity']['attributes']['locationUri'] == 'hdfs://data/my_database'
        assert 'createTime' in entity['entity']['attributes']
        assert 'qualifiedName' in entity['entity']['attributes']

    def test_database_builder_with_description(self):
        """Test database builder with description."""
        builder = DatabaseEntityBuilder("test_db", "hdfs://test")
        builder.set_description("Test database for unit tests")
        entity = builder.build()

        assert entity['entity']['attributes']['description'] == "Test database for unit tests"

    def test_database_builder_with_create_time(self):
        """Test database builder with custom create time."""
        create_time = "2026-03-24T10:00:00"
        builder = DatabaseEntityBuilder("test_db", "hdfs://test")
        builder.set_create_time(create_time)
        entity = builder.build()

        assert entity['entity']['attributes']['createTime'] == create_time

    def test_database_builder_fluent_api(self):
        """Test fluent API chaining."""
        entity = (DatabaseEntityBuilder("db_1", "hdfs://path1")
                  .set_description("Database 1")
                  .set_create_time("2026-03-24")
                  .build())

        assert entity['entity']['attributes']['database_name'] == 'db_1'
        assert entity['entity']['attributes']['description'] == "Database 1"

    def test_database_builder_qualified_name_generation(self):
        """Test that qualified name is properly generated."""
        builder = DatabaseEntityBuilder("finance_db", "hdfs://finance")
        entity = builder.build()

        qualified_name = entity['entity']['attributes']['qualifiedName']
        assert qualified_name.startswith("scb:::dp:::")
        assert "finance_db" in qualified_name

    def test_database_builder_required_attributes(self):
        """Test that required attributes are always set."""
        builder = DatabaseEntityBuilder("minimal_db", "hdfs://minimal")
        entity = builder.build()

        assert entity['entity']['attributes']['database_name'] == "minimal_db"
        assert entity['entity']['attributes']['locationUri'] == "hdfs://minimal"
        assert entity['entity']['attributes']['createTime'] is not None


class TestTableEntityBuilder:
    """Tests for TableEntityBuilder."""

    def test_table_builder_basic_creation(self):
        """Test basic table entity creation."""
        builder = TableEntityBuilder("trades", "finance_db")
        entity = builder.build()

        assert entity['entity']['typeName'] == 'SCB_Table'
        assert entity['entity']['attributes']['table_name'] == 'trades'
        assert entity['entity']['attributes']['temporary'] == False
        assert 'qualifiedName' in entity['entity']['attributes']

    def test_table_builder_with_table_type(self):
        """Test table builder with table type."""
        builder = TableEntityBuilder("external_data", "source_db")
        builder.set_table_type("EXTERNAL")
        entity = builder.build()

        assert entity['entity']['attributes']['tableType'] == "EXTERNAL"

    def test_table_builder_with_temporary_flag(self):
        """Test table builder with temporary flag."""
        builder = TableEntityBuilder("temp_table", "work_db")
        builder.set_temporary(True)
        entity = builder.build()

        assert entity['entity']['attributes']['temporary'] == True

    def test_table_builder_with_serde_information(self):
        """Test table builder with SERDE information."""
        builder = TableEntityBuilder("parquet_table", "data_db")
        builder.set_serde("org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe", 
                         "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe")
        entity = builder.build()

        assert entity['entity']['attributes']['serde1'] == "org.apache.hadoop.hive.serde2.lazy.LazySimpleSerDe"
        assert entity['entity']['attributes']['serde2'] == "org.apache.hadoop.hive.ql.io.parquet.serde.ParquetHiveSerDe"

    def test_table_builder_with_description(self):
        """Test table builder with description."""
        builder = TableEntityBuilder("users", "main_db")
        builder.set_description("User profile data")
        entity = builder.build()

        assert entity['entity']['attributes']['description'] == "User profile data"

    def test_table_builder_qualified_name_with_database(self):
        """Test qualified name includes database name."""
        builder = TableEntityBuilder("sales", "retail_db")
        entity = builder.build()

        qualified_name = entity['entity']['attributes']['qualifiedName']
        assert "retail_db" in qualified_name
        assert "sales" in qualified_name

    def test_table_builder_qualified_name_without_database(self):
        """Test qualified name works without database name."""
        builder = TableEntityBuilder("standalone_table")
        entity = builder.build()

        qualified_name = entity['entity']['attributes']['qualifiedName']
        assert "standalone_table" in qualified_name

    def test_table_builder_fluent_api(self):
        """Test fluent API chaining for tables."""
        entity = (TableEntityBuilder("analytics_table", "analytics_db")
                  .set_table_type("MANAGED")
                  .set_temporary(False)
                  .set_description("Analytics data")
                  .build())

        assert entity['entity']['attributes']['table_name'] == "analytics_table"
        assert entity['entity']['attributes']['tableType'] == "MANAGED"
        assert entity['entity']['attributes']['description'] == "Analytics data"


class TestColumnEntityBuilder:
    """Tests for ColumnEntityBuilder."""

    def test_column_builder_basic_creation(self):
        """Test basic column entity creation."""
        builder = ColumnEntityBuilder("user_id", "bigint")
        entity = builder.build()

        assert entity['entity']['typeName'] == 'SCB_Column'
        assert entity['entity']['attributes']['column_name'] == 'user_id'
        assert entity['entity']['attributes']['dataType'] == 'bigint'
        assert 'qualifiedName' in entity['entity']['attributes']

    def test_column_builder_with_table_name(self):
        """Test column builder with table name."""
        builder = ColumnEntityBuilder("email", "string", "users_db.users")
        entity = builder.build()

        qualified_name = entity['entity']['attributes']['qualifiedName']
        assert "users_db" in qualified_name
        assert "users" in qualified_name
        assert "email" in qualified_name

    def test_column_builder_with_comment(self):
        """Test column builder with comment."""
        builder = ColumnEntityBuilder("age", "int")
        builder.set_comment("User age in years")
        entity = builder.build()

        assert entity['entity']['attributes']['comment'] == "User age in years"

    def test_column_builder_with_position(self):
        """Test column builder with position."""
        builder = ColumnEntityBuilder("name", "string")
        builder.set_position(1)
        entity = builder.build()

        assert entity['entity']['attributes']['position'] == 1

    def test_column_builder_various_data_types(self):
        """Test column builder with various data types."""
        data_types = [
            "string", "int", "bigint", "float", "double", "boolean", "date",
            "timestamp", "decimal(18,2)", "array<string>", "map<string,int>"
        ]

        for dtype in data_types:
            builder = ColumnEntityBuilder(f"col_{dtype.replace('<', '_').replace('>', '_')}", dtype)
            entity = builder.build()
            assert entity['entity']['attributes']['dataType'] == dtype

    def test_column_builder_fluent_api(self):
        """Test fluent API chaining for columns."""
        entity = (ColumnEntityBuilder("transaction_id", "string", "finance_db.transactions")
                  .set_comment("Unique transaction identifier")
                  .set_position(1)
                  .build())

        assert entity['entity']['attributes']['column_name'] == "transaction_id"
        assert entity['entity']['attributes']['comment'] == "Unique transaction identifier"
        assert entity['entity']['attributes']['position'] == 1

    def test_column_builder_position_zero(self):
        """Test column with position 0."""
        builder = ColumnEntityBuilder("first_col", "string")
        builder.set_position(0)
        entity = builder.build()

        assert entity['entity']['attributes']['position'] == 0

    def test_column_builder_without_table_name(self):
        """Test column builder without parent table name."""
        builder = ColumnEntityBuilder("standalone_col", "varchar(255)")
        entity = builder.build()

        qualified_name = entity['entity']['attributes']['qualifiedName']
        assert "standalone_col" in qualified_name


class TestProcessEntityBuilder:
    """Tests for ProcessEntityBuilder."""

    def test_process_builder_basic_creation(self):
        """Test basic process entity creation."""
        builder = ProcessEntityBuilder(
            "daily_etl",
            "etl_001",
            "SELECT * FROM source_table"
        )
        entity = builder.build()

        assert entity['entity']['typeName'] == 'SCB_Process'
        assert entity['entity']['attributes']['process_name'] == 'daily_etl'
        assert entity['entity']['attributes']['queryId'] == 'etl_001'
        assert entity['entity']['attributes']['queryText'] == 'SELECT * FROM source_table'
        assert 'qualifiedName' in entity['entity']['attributes']

    def test_process_builder_with_user_name(self):
        """Test process builder with user name."""
        builder = ProcessEntityBuilder("job_1", "job_001", "SELECT 1")
        builder.set_user_name("data_pipeline")
        entity = builder.build()

        assert entity['entity']['attributes']['userName'] == "data_pipeline"

    def test_process_builder_with_timestamps(self):
        """Test process builder with start and end times."""
        start_time = 1708953600000
        end_time = 1708957200000

        builder = ProcessEntityBuilder("timed_job", "job_002", "SELECT * FROM data")
        builder.set_start_time(start_time)
        builder.set_end_time(end_time)
        entity = builder.build()

        assert entity['entity']['attributes']['startTime'] == start_time
        assert entity['entity']['attributes']['endTime'] == end_time

    def test_process_builder_with_input_entities(self):
        """Test process builder with input entity references."""
        builder = ProcessEntityBuilder("transform", "trans_001", "SELECT * FROM raw")
        builder.add_input_entity("SCB_Table", "scb:::dp:::raw_db.raw_data")
        entity = builder.build()

        inputs = entity['entity']['attributes']['inputs']
        assert len(inputs) == 1
        assert inputs[0]['typeName'] == 'SCB_Table'
        assert inputs[0]['uniqueAttributes']['qualifiedName'] == 'scb:::dp:::raw_db.raw_data'

    def test_process_builder_with_output_entities(self):
        """Test process builder with output entity references."""
        builder = ProcessEntityBuilder("publish", "pub_001", "SELECT * FROM processed")
        builder.add_output_entity("SCB_DataProduct", "scb:::dp:::processed_product")
        entity = builder.build()

        outputs = entity['entity']['attributes']['outputs']
        assert len(outputs) == 1
        assert outputs[0]['typeName'] == 'SCB_DataProduct'
        assert outputs[0]['uniqueAttributes']['qualifiedName'] == 'scb:::dp:::processed_product'

    def test_process_builder_with_multiple_inputs_outputs(self):
        """Test process builder with multiple input and output entities."""
        builder = ProcessEntityBuilder("complex_job", "complex_001", "JOIN query")
        builder.add_input_entity("SCB_Table", "scb:::dp:::db1.table1")
        builder.add_input_entity("SCB_Table", "scb:::dp:::db2.table2")
        builder.add_output_entity("SCB_Table", "scb:::dp:::result_db.result_table")
        builder.add_output_entity("SCB_DataProduct", "scb:::dp:::result_product")
        entity = builder.build()

        assert len(entity['entity']['attributes']['inputs']) == 2
        assert len(entity['entity']['attributes']['outputs']) == 2

    def test_process_builder_multiline_query(self):
        """Test process builder with multiline query."""
        query = """
        SELECT 
            date,
            SUM(amount) as total
        FROM transactions
        WHERE date >= CURRENT_DATE - 7
        GROUP BY date
        """
        builder = ProcessEntityBuilder("weekly_agg", "agg_001", query)
        entity = builder.build()

        assert query in entity['entity']['attributes']['queryText']

    def test_process_builder_fluent_api(self):
        """Test fluent API chaining for processes."""
        entity = (ProcessEntityBuilder("complete_process", "proc_001", "SELECT * FROM data")
                  .set_user_name("etl_team")
                  .set_start_time(1708953600000)
                  .set_end_time(1708957200000)
                  .add_input_entity("SCB_Table", "scb:::dp:::source.data")
                  .add_output_entity("SCB_DataProduct", "scb:::dp:::output_product")
                  .build())

        assert entity['entity']['attributes']['process_name'] == "complete_process"
        assert entity['entity']['attributes']['userName'] == "etl_team"
        assert len(entity['entity']['attributes']['inputs']) == 1
        assert len(entity['entity']['attributes']['outputs']) == 1

    def test_process_builder_no_lineage(self):
        """Test process builder without input/output lineage."""
        builder = ProcessEntityBuilder("simple_process", "simple_001", "SELECT 1")
        entity = builder.build()

        # inputs and outputs should not be in attributes if not set
        assert 'inputs' not in entity['entity']['attributes'] or len(entity['entity']['attributes'].get('inputs', [])) == 0
        assert 'outputs' not in entity['entity']['attributes'] or len(entity['entity']['attributes'].get('outputs', [])) == 0


class TestEntityStructures:
    """Tests for entity structure validation."""

    def test_all_entities_have_qualified_name(self):
        """Test that all entity types include qualified name."""
        entities = [
            DatabaseEntityBuilder("db", "hdfs://db").build(),
            TableEntityBuilder("tbl", "db").build(),
            ColumnEntityBuilder("col", "string").build(),
            ProcessEntityBuilder("proc", "proc_1", "SELECT 1").build()
        ]

        for entity in entities:
            assert 'qualifiedName' in entity['entity']['attributes']
            qn = entity['entity']['attributes']['qualifiedName']
            assert qn.startswith("scb:::dp:::")

    def test_all_entities_have_type_name(self):
        """Test that all entity types have typeName set."""
        entities = [
            ("SCB_Database", DatabaseEntityBuilder("db", "hdfs://db").build()),
            ("SCB_Table", TableEntityBuilder("tbl", "db").build()),
            ("SCB_Column", ColumnEntityBuilder("col", "string").build()),
            ("SCB_Process", ProcessEntityBuilder("proc", "proc_1", "SELECT 1").build())
        ]

        for expected_type, entity in entities:
            assert entity['entity']['typeName'] == expected_type

    def test_entity_structure_format(self):
        """Test that all entities follow correct structure format."""
        builder = DatabaseEntityBuilder("test", "hdfs://test")
        entity = builder.build()

        # Check structure
        assert 'entity' in entity
        assert 'typeName' in entity['entity']
        assert 'attributes' in entity['entity']
        assert isinstance(entity['entity']['attributes'], dict)


class TestQualifiedNameGeneration:
    """Tests for qualified name generation."""

    def test_qualified_name_consistency(self):
        """Test that same names generate same qualified names."""
        qn1 = prepare_qualified_name("test_database")
        qn2 = prepare_qualified_name("test_database")

        assert qn1 == qn2

    def test_qualified_name_with_spaces(self):
        """Test qualified name generation with spaces."""
        qn = prepare_qualified_name("my test database")
        assert "my_test_database" in qn.lower()

    def test_qualified_name_case_insensitivity(self):
        """Test qualified name generation is case insensitive."""
        qn1 = prepare_qualified_name("TestDatabase")
        qn2 = prepare_qualified_name("testdatabase")

        # Both should contain lowercase versions
        assert "testdatabase" in qn1.lower()
        assert "testdatabase" in qn2.lower()


class TestBuilderEdgeCases:
    """Tests for edge cases and error conditions."""

    def test_empty_description(self):
        """Test builder with empty description."""
        builder = DatabaseEntityBuilder("db", "hdfs://db")
        builder.set_description("")
        entity = builder.build()

        # Empty string should not be added to attributes if empty
        if 'description' in entity['entity']['attributes']:
            assert entity['entity']['attributes']['description'] == ""

    def test_special_characters_in_names(self):
        """Test builder with special characters in names."""
        builder = DatabaseEntityBuilder("db-test_123", "hdfs://db/path")
        entity = builder.build()

        assert entity['entity']['attributes']['database_name'] == "db-test_123"

    def test_very_long_query_text(self):
        """Test process builder with very long query."""
        long_query = "SELECT " + ", ".join([f"col_{i}" for i in range(1000)]) + " FROM large_table"
        builder = ProcessEntityBuilder("big_query", "query_001", long_query)
        entity = builder.build()

        assert long_query == entity['entity']['attributes']['queryText']

    def test_unicode_in_descriptions(self):
        """Test builder with unicode characters in descriptions."""
        builder = DatabaseEntityBuilder("db", "hdfs://db")
        builder.set_description("Database with émojis 🎯 and ünïcödé")
        entity = builder.build()

        assert "🎯" in entity['entity']['attributes']['description']
        assert "ünïcödé" in entity['entity']['attributes']['description']

    def test_table_without_database_name(self):
        """Test table builder without database name."""
        builder = TableEntityBuilder("orphan_table")
        entity = builder.build()

        assert entity['entity']['attributes']['table_name'] == "orphan_table"
        assert 'qualifiedName' in entity['entity']['attributes']

    def test_multiple_builder_instances_independent(self):
        """Test that multiple builder instances don't interfere."""
        builder1 = DatabaseEntityBuilder("db1", "hdfs://db1")
        builder1.set_description("Database 1")

        builder2 = DatabaseEntityBuilder("db2", "hdfs://db2")
        builder2.set_description("Database 2")

        entity1 = builder1.build()
        entity2 = builder2.build()

        assert entity1['entity']['attributes']['database_name'] == "db1"
        assert entity2['entity']['attributes']['database_name'] == "db2"
        assert entity1['entity']['attributes']['description'] == "Database 1"
        assert entity2['entity']['attributes']['description'] == "Database 2"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

