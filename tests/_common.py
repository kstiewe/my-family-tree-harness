"""Shared helpers for the tests. Tests use only the fictional sample family (examples/sample-family)
and invented data created on the fly — never real family data."""

import contextlib
import io
import os
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "examples" / "sample-family"
sys.path.insert(0, str(ROOT))


def run(main, argv: list[str]) -> tuple[int, str, str]:
    """Run a CLI main() and capture (exit code, stdout, stderr)."""
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        try:
            code = main(argv)
        except SystemExit as e:
            code = e.code if isinstance(e.code, int) else 1
    return code, out.getvalue(), err.getvalue()


@contextlib.contextmanager
def env(**values):
    """Temporarily set (or with None: remove) environment variables."""
    old = {k: os.environ.get(k) for k in values}
    try:
        for k, v in values.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v
        yield
    finally:
        for k, v in old.items():
            if v is None:
                os.environ.pop(k, None)
            else:
                os.environ[k] = v


def tmpdir() -> Path:
    return Path(tempfile.mkdtemp(prefix="familytree-test-"))
