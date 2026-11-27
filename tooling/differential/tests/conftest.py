import os
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

FAKE_IMPL = Path(__file__).resolve().parent / "fake_impl.py"


@pytest.fixture
def fake_impl_argv():
    """A protocol-speaking implementation: an error `X1` on every line
    holding `BAD`, two on a line holding `BAD2`, `X0` at line 0 for `EOF!`."""
    return [sys.executable, str(FAKE_IMPL)]


def _beancount():
    try:
        import beancount.parser.parser  # noqa: F401
    except ImportError:
        return False
    return True


#: Tests that need beancount skip without it, except where
#: PTADIFF_REQUIRE_BEANCOUNT=1 (CI) makes a missing beancount a failure, so
#: they cannot pass by skipping everywhere.
def require_beancount():
    if _beancount():
        return
    if os.environ.get("PTADIFF_REQUIRE_BEANCOUNT") == "1":
        pytest.fail("beancount is not importable but PTADIFF_REQUIRE_BEANCOUNT=1")
    pytest.skip("beancount not installed")
