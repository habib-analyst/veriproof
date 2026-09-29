import pytest

import veriproof
from veriproof.cli import main


def test_version_flag(capsys):
    with pytest.raises(SystemExit) as e:
        main(["--version"])
    assert e.value.code == 0
    out = capsys.readouterr().out
    assert veriproof.__version__ in out


def test_verify_stub_exits_with_message(capsys):
    with pytest.raises(SystemExit) as e:
        main(["verify", "fake.png"])
    assert e.value.code == 1
    err = capsys.readouterr().err
    assert "not implemented until M4" in err


def test_no_args_prints_help(capsys):
    assert main([]) == 0
    out = capsys.readouterr().out
    assert "usage" in out.lower() or "usage" in out
