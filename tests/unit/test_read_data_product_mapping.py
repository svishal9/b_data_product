from scb_atlas.atlas.read_data_product import _SUB_DOMAIN_MAP, _normalize_mapped_value


def test_sub_domain_normalizes_whitespace_and_case() -> None:
    assert _normalize_mapped_value(
        "  Wealth   Management  ",
        _SUB_DOMAIN_MAP,
        field_name="Sub-Domain",
        strict=False,
    ) == "Wealth Management"


def test_sub_domain_invalid_strict_raises() -> None:
    try:
        _normalize_mapped_value(
            "Not A Real Sub Domain",
            _SUB_DOMAIN_MAP,
            field_name="Sub-Domain",
            strict=True,
        )
    except ValueError as exc:
        assert "Sub-Domain" in str(exc)
    else:
        raise AssertionError("Expected ValueError for invalid strict mapped value")

