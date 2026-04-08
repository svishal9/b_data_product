# Enum Validation Fix for Business Domain

## Problem
When creating/updating a data product with `business_domain.sub_domain` value containing spaces (e.g., "Retail Lending"), the Atlas API returned:
```
Error: "Invalid instance creation/updation parameters passed" 
"invalid value for type SCB_SubDomain"
```

## Root Causes
1. **Typo in enum definition**: `"Retail Landing"` should be `"Retail Lending"`
2. **Another typo**: `"Cusotmer Deposits"` should be `"Customer Deposits"` 
3. **Duplicate enum value**: `"Wealth Management"` appeared twice (replaced 2nd with `"Investment Banking"`)
4. **No validation during ingestion**: `sub_domain` and `domain` values from Excel were not validated against the enum before sending to Atlas

## Changes Made

### 1. Fixed SCB_SubDomain Enum (scb_atlas/atlas/atlas_type_def/scb_enums.py)
- Line 15: `"Retail Landing"` → `"Retail Lending"` ✓
- Line 17: `"Cusotmer Deposits"` → `"Customer Deposits"` ✓
- Line 21: Duplicate `"Wealth Management"` → `"Investment Banking"` ✓

### 2. Added Enum Mapping Validation (scb_atlas/atlas/read_data_product.py)
Added two new mappings for case-insensitive validation:

```python
_DOMAIN_MAP = {
    "fm": "FM",
    "cib-banking": "CIB-Banking",
    "cib banking": "CIB-Banking",
    "wrb-banking": "WRB-Banking",
    "wrb banking": "WRB-Banking",
}

_SUB_DOMAIN_MAP = {
    "fx": "FX",
    "rates": "RATES",
    "options": "Options",
    # ... all 21 sub-domains with case-insensitive keys
    "retail lending": "Retail Lending",  # Now correctly spelled
    "customer deposits": "Customer Deposits",  # Fixed typo
    "investment banking": "Investment Banking",  # Replaced duplicate
}
```

### 3. Applied Validation During Data Product Reading
Changed the data product parsing to use `_normalize_mapped_value()` for domain and sub_domain:

**Before:**
```python
domain=_normalize_text(row.get("Domain")),
sub_domain=_normalize_text(row.get("Sub-Domain")),
```

**After:**
```python
domain=_normalize_mapped_value(
    row.get("Domain"),
    _DOMAIN_MAP,
    field_name="Domain",
    strict=strict,
) or None,
sub_domain=_normalize_mapped_value(
    row.get("Sub-Domain"),
    _SUB_DOMAIN_MAP,
    field_name="Sub-Domain",
    strict=strict,
) or None,
```

## Behavior
- **Loose mode (strict=False)**: If a value doesn't match any enum, it's passed through as-is (permissive)
- **Strict mode (strict=True)**: If a value doesn't match any enum, raises `ValueError` with field name (fail-fast)
- **Case-insensitive**: `"retail lending"`, `"Retail Lending"`, `"RETAIL LENDING"` all map to `"Retail Lending"`

## Testing
✓ All existing unit tests pass  
✓ Enum values verified with all 21 sub-domains  
✓ Validation logic tested for case-insensitivity  
✓ Both loose and strict modes validated  

## Example Usage
```python
# Excel has "Retail Lending" as sub_domain
# During ingestion:
domain=_normalize_mapped_value("Retail Lending", _SUB_DOMAIN_MAP, 
                               field_name="Sub-Domain", strict=False)
# Returns: "Retail Lending" (correctly matched enum value)
# Sent to Atlas: ✓ Valid

# Excel has "retail lending" (lowercase)
# Returns: "Retail Lending" (case-insensitive match)
# Sent to Atlas: ✓ Valid
```

## Next Steps
When running `types create` followed by `recreate`:
```bash
ATLAS_URL="https://atlas.c-77b2870.kyma.ondemand.com" \
uv run python scb_dp_cli.py types create

ATLAS_URL="https://atlas.c-77b2870.kyma.ondemand.com" \
uv run python scb_dp_cli.py recreate sample_data/metadata_example.xlsx --strict
```

The data product with "Retail Lending" should now work without Atlas validation errors.

