# tests/test_version.py
import veriproof


def test_version_exists():
    assert isinstance(veriproof.__version__, str)
    assert veriproof.__version__.count(".") >= 1
