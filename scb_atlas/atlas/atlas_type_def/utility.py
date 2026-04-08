import re

def prepare_qualified_name(name: str) -> str:
    """
        Convert a string to a qualified data-product name:
        - strip leading/trailing whitespace
        - replace runs of whitespace with '_'
        - convert to lower case
        - prefix with 'scb:::dp:::'
    """


    if name is None:
        raise ValueError("name must be a non-empty string")
    s = str(name).strip()
    if not s:
        raise ValueError("name must be a non-empty string")
    s = re.sub(r"\s+", "_", s).lower()
    return f"scb:::dp:::{s}"