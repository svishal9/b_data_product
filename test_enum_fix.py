#!/usr/bin/env python3
"""
Test to verify the enum validation fix works correctly.
This addresses the issue: "invalid value for type SCB_SubDomain" with "Retail Lending"
"""

from scb_atlas.atlas.atlas_type_def.scb_enums import scb_sub_domains_enums
from scb_atlas.atlas.read_data_product import _normalize_mapped_value, _SUB_DOMAIN_MAP, _DOMAIN_MAP


def test_enum_typos_fixed():
    """Verify typos in enum definitions were fixed"""
    sub_domain_values = [d["value"] for d in scb_sub_domains_enums.element_defs]
    
    # These were the issues
    assert "Retail Lending" in sub_domain_values, "Retail Lending should be in enum"
    assert "Customer Deposits" in sub_domain_values, "Customer Deposits should be in enum"
    assert "Investment Banking" in sub_domain_values, "Investment Banking should be in enum"
    
    # These should NOT be in enum anymore
    assert "Retail Landing" not in sub_domain_values, "Old typo should be removed"
    assert "Cusotmer Deposits" not in sub_domain_values, "Old typo should be removed"
    
    print("✓ Enum definitions fixed")


def test_subdomain_validation():
    """Verify sub_domain enum validation works"""
    
    # The failing case from user report
    result = _normalize_mapped_value(
        "Retail Lending",
        _SUB_DOMAIN_MAP,
        field_name="Sub-Domain",
        strict=False
    )
    assert result == "Retail Lending", f"Expected 'Retail Lending', got {result}"
    
    # Case-insensitive
    result = _normalize_mapped_value(
        "retail lending",
        _SUB_DOMAIN_MAP,
        field_name="Sub-Domain",
        strict=False
    )
    assert result == "Retail Lending", f"Case-insensitive match failed"
    
    # Other validated values
    result = _normalize_mapped_value(
        "money market",
        _SUB_DOMAIN_MAP,
        field_name="Sub-Domain",
        strict=False
    )
    assert result == "Money Market"
    
    result = _normalize_mapped_value(
        "customer deposits",
        _SUB_DOMAIN_MAP,
        field_name="Sub-Domain",
        strict=False
    )
    assert result == "Customer Deposits"
    
    print("✓ Sub-domain validation working")


def test_domain_validation():
    """Verify domain enum validation works"""
    
    result = _normalize_mapped_value(
        "FM",
        _DOMAIN_MAP,
        field_name="Domain",
        strict=False
    )
    assert result == "FM"
    
    result = _normalize_mapped_value(
        "cib-banking",
        _DOMAIN_MAP,
        field_name="Domain",
        strict=False
    )
    assert result == "CIB-Banking"
    
    print("✓ Domain validation working")


def test_strict_mode():
    """Verify strict mode rejects invalid values"""
    
    try:
        _normalize_mapped_value(
            "Invalid Value",
            _SUB_DOMAIN_MAP,
            field_name="Sub-Domain",
            strict=True
        )
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "Invalid Value" in str(e)
    
    print("✓ Strict mode validation working")


if __name__ == "__main__":
    test_enum_typos_fixed()
    test_subdomain_validation()
    test_domain_validation()
    test_strict_mode()
    
    print("\n" + "=" * 70)
    print("SUCCESS! All enum validation tests passed.")
    print("=" * 70)
    print("\nThe issue with 'Retail Lending' causing:")
    print('  "Invalid instance creation/updation parameters passed"')
    print('  "invalid value for type SCB_SubDomain"')
    print("\nHas been resolved by:")
    print("  1. Fixing enum typo: 'Retail Landing' → 'Retail Lending'")
    print("  2. Fixing enum typo: 'Cusotmer Deposits' → 'Customer Deposits'")
    print("  3. Removing duplicate: 'Wealth Management' duplicate")
    print("  4. Adding case-insensitive enum validation during ingestion")
    print("\nData products can now use 'Retail Lending' without errors.")

