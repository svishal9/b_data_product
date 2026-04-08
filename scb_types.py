#!/usr/bin/env python3
"""Backward-compatible shim for legacy scb_types entry point.
The actual implementation has been moved to scripts/legacy/scb_types.py
"""
from __future__ import annotations

from scripts.legacy.scb_types import app
if __name__ == "__main__":
    raise SystemExit(app())
