#!/usr/bin/env python3
"""
Simple test verification script to run all tests manually.
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

# Import test classes
from tests.unit.test_entity_builders import (
    TestDatabaseEntityBuilder,
    TestTableEntityBuilder,
    TestColumnEntityBuilder,
    TestProcessEntityBuilder,
)
from tests.unit.test_atlas_types import (
    TestTypeDefinitionStructure,
    TestDatabaseEntityType,
    TestTableEntityType,
    TestColumnEntityType,
    TestProcessEntityType,
)

def run_test(test_class, method_name):
    """Run a single test method."""
    try:
        instance = test_class()
        method = getattr(instance, method_name)
        method()
        return True, None
    except Exception as e:
        return False, str(e)

def main():
    """Run all tests."""
    
    # Unit tests for builders
    builder_tests = [
        (TestDatabaseEntityBuilder, [
            'test_database_builder_basic_creation',
            'test_database_builder_with_description',
            'test_database_builder_fluent_api',
        ]),
        (TestTableEntityBuilder, [
            'test_table_builder_basic_creation',
            'test_table_builder_with_table_type',
            'test_table_builder_fluent_api',
        ]),
        (TestColumnEntityBuilder, [
            'test_column_builder_basic_creation',
            'test_column_builder_with_comment',
            'test_column_builder_fluent_api',
        ]),
        (TestProcessEntityBuilder, [
            'test_process_builder_basic_creation',
            'test_process_builder_with_user_name',
            'test_process_builder_fluent_api',
        ]),
    ]
    
    # Unit tests for types
    type_tests = [
        (TestTypeDefinitionStructure, [
            'test_type_definitions_contains_all_entity_types',
            'test_each_entity_definition_has_required_fields',
        ]),
        (TestDatabaseEntityType, [
            'test_database_entity_extends_dataset',
            'test_database_entity_has_required_attributes',
        ]),
        (TestTableEntityType, [
            'test_table_entity_extends_dataset',
            'test_table_entity_has_required_attributes',
        ]),
        (TestColumnEntityType, [
            'test_column_entity_extends_dataset',
            'test_column_entity_has_required_attributes',
        ]),
        (TestProcessEntityType, [
            'test_process_entity_extends_process',
            'test_process_entity_has_required_attributes',
        ]),
    ]
    
    all_tests = builder_tests + type_tests
    passed = 0
    failed = 0
    failed_tests = []
    
    print("\n" + "="*80)
    print("SCB Atlas Entity Types - Test Verification")
    print("="*80 + "\n")
    
    for test_class, methods in all_tests:
        class_name = test_class.__name__
        print(f"Testing {class_name}...")
        
        for method_name in methods:
            success, error = run_test(test_class, method_name)
            
            if success:
                print(f"  ✅ {method_name}")
                passed += 1
            else:
                print(f"  ❌ {method_name}")
                print(f"     Error: {error}")
                failed += 1
                failed_tests.append((class_name, method_name, error))
    
    # Print summary
    print("\n" + "="*80)
    print("Test Summary")
    print("="*80)
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"Total: {passed + failed}")
    
    if failed > 0:
        print("\n" + "="*80)
        print("Failed Tests Details:")
        print("="*80)
        for class_name, method_name, error in failed_tests:
            print(f"\n{class_name}::{method_name}")
            print(f"  Error: {error}")
    
    print("\n" + "="*80)
    if failed == 0:
        print("✅ ALL TESTS PASSED!")
        print("="*80 + "\n")
        return 0
    else:
        print(f"❌ {failed} TESTS FAILED")
        print("="*80 + "\n")
        return 1

if __name__ == "__main__":
    sys.exit(main())

