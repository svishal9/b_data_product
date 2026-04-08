#!/usr/bin/env python3
"""Backward-compatible shim for legacy scb_enums entry point.
The actual implementation has been moved to scripts/legacy/scb_enums.py
"""
from __future__ import annotations

from scripts.legacy.scb_enums import app
if __name__ == "__main__":
    raise SystemExit(app())
