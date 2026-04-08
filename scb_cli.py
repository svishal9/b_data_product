#!/usr/bin/env python3
"""Backward-compatible alias to the renamed unified CLI module."""

from __future__ import annotations

from scb_dp_cli import main


if __name__ == "__main__":
    raise SystemExit(main())

