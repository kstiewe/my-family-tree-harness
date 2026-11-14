#!/usr/bin/env python3
"""Privacy guard: block family data from entering the repository (see --help)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from familytree.guard import main  # noqa: E402

if __name__ == "__main__":
    sys.exit(main())
