#!/usr/bin/env python3
"""Backward-compatible shim for legacy scb_dp entry point.
The actual implementation has been moved to scripts/legacy/scb_dp.py
"""
from __future__ import annotations

# Re-export the functions and app for backward compatibility
from scripts.legacy.scb_dp import app, entity_create, entity_delete

__all__ = ["app", "entity_create", "entity_delete"]

if __name__ == "__main__":
    raise SystemExit(app())
