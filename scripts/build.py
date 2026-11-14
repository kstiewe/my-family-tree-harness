#!/usr/bin/env python3
"""Validate the family-tree data and generate outputs (see --help)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from familytree.build import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
