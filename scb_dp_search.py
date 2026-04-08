#!/usr/bin/env python3
"""Backward-compatible shim for legacy scb_dp_search entry point.
The actual implementation has been moved to scripts/legacy/scb_dp_search.py
"""
from __future__ import annotations

# Re-export the functions and app for backward compatibility
from scripts.legacy.scb_dp_search import app, catalog_search, process_find

__all__ = ["app", "catalog_search", "process_find"]

if __name__ == "__main__":
    raise SystemExit(app())
