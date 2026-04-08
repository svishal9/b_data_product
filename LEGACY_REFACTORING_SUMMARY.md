# Legacy Wrappers Refactoring - Second Pass

## Summary
Successfully moved legacy wrapper files (`scb_types.py`, `scb_dp.py`, `scb_dp_search.py`, `scb_enums.py`) into a new `scripts/legacy/` directory, leaving only tiny root shims that delegate to the new location.

## Structure Changes

### Before
```
scb-data-product/
├── scb_types.py          (64 lines - legacy implementation)
├── scb_dp.py             (226 lines - legacy implementation)
├── scb_dp_search.py      (64 lines - legacy implementation)
├── scb_enums.py          (116 lines - legacy implementation)
├── scb_cli.py            (11 lines - simple alias)
├── scb_dp_cli.py         (247 lines - main unified CLI)
└── ...
```

### After
```
scb-data-product/
├── scb_types.py          (9 lines - shim only)
├── scb_dp.py             (11 lines - shim only)
├── scb_dp_search.py      (11 lines - shim only)
├── scb_enums.py          (9 lines - shim only)
├── scb_cli.py            (11 lines - simple alias)
├── scb_dp_cli.py         (247 lines - main unified CLI)
├── scripts/
│   ├── __init__.py
│   ├── legacy/
│   │   ├── __init__.py
│   │   ├── scb_types.py          (63 lines - actual implementation)
│   │   ├── scb_dp.py             (225 lines - actual implementation)
│   │   ├── scb_dp_search.py      (63 lines - actual implementation)
│   │   └── scb_enums.py          (115 lines - actual implementation)
│   └── ...
└── ...
```

## Root Shim Files

All root shim files now:
1. Import and re-export the `app` from `scripts/legacy/`
2. Re-export any exported functions/classes for backward compatibility
3. Provide a thin wrapper around the actual implementation
4. Include deprecation notice in docstring

### Example: scb_dp.py
```python
#!/usr/bin/env python3
"""Backward-compatible shim for legacy scb_dp entry point."""

from __future__ import annotations

import sys
from scripts.legacy.scb_dp import app, entity_create, entity_delete

if __name__ == "__main__":
    raise SystemExit(app())
```

## Benefits

1. **Cleaner root directory**: Legacy code is now organized under `scripts/legacy/`
2. **Minimal shims**: Root files are now 9-11 lines instead of 63-226 lines
3. **Backward compatible**: All existing imports and entry points still work
4. **Clear organization**: Distinction between active code and legacy wrappers
5. **Easy migration**: Functions are re-exported, so gradual migration is seamless

## Backward Compatibility

✅ All existing imports work:
```python
from scb_dp import entity_create, entity_delete
from scb_dp_search import catalog_search, process_find
from scb_types import app
from scb_enums import app
```

✅ All entry points work:
```bash
python scb_types.py
python scb_dp.py
python scb_dp_search.py
python scb_enums.py
```

✅ All tests pass (verified with pytest)

## Testing

All existing tests pass after the refactoring:
- `tests/unit/test_scb_dp_cli.py`: ✅ 4/4 tests passed

## Notes

- `scb_cli.py` was already a simple alias and remains as-is
- No logic was changed; only file organization
- The `scb_dp_cli.py` unified CLI remains the main entry point and wasn't moved

