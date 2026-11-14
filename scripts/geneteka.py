#!/usr/bin/env python3
"""Geneteka helper: search links, parish lists, surname overview (see --help)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from familytree.geneteka import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
