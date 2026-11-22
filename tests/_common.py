"""Shared helpers for the tests. Tests use only the fictional sample family (examples/sample-family)
and invented data created on the fly — never real family data."""

import contextlib
import io
import os
import shutil
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
EXAMPLE = ROOT / "examples" / "sample-family"
sys.path.insert(0, str(ROOT))

# The tests never see the configuration of the machine they run on: its registry of workspaces, the `.workspace` file
# of the checkout and these variables would bring a real family's private terms into the guard tests (or switch the
# guard off), and `workspace.py init` would register the test workspaces there.
CONFIG = Path(tempfile.mkdtemp(prefix="familytree-test-config-"))
os.environ["XDG_CONFIG_HOME"] = str(CONFIG)
for _var in ("FAMILYTREE_WORKSPACE", "FAMILYTREE_GUARD_NO_PRIVATE"):
    os.environ.pop(_var, None)

from familytree import workspace as _workspace  # noqa: E402

_workspace.POINTER = CONFIG / "app.workspace"


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


def own_config():
    """A configuration directory of its own (registry of workspaces, user pointer) for one test."""
    return env(XDG_CONFIG_HOME=str(tmpdir()))


def sample_copy(name: str = "sample") -> Path:
    """A copy of the fictional sample family outside the repository; it stands in for another family's workspace."""
    root = (tmpdir() / name).resolve()
    shutil.copytree(EXAMPLE, root, ignore=shutil.ignore_patterns("output"))
    return root
