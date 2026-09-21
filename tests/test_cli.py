"""CLI smoke tests."""

from __future__ import annotations

from twistdiff.cli import main


def test_oscillator_cli(capsys):
    assert main(["oscillator", "--t-end", "1.0", "--dt", "0.05"]) == 0
    out = capsys.readouterr().out
    assert "steps=" in out


def test_cruise_cli(capsys):
    assert main(["cruise", "--t-end", "2.0", "--dt", "0.1"]) == 0
    out = capsys.readouterr().out
    assert "v_final=" in out


def test_version():
    import pytest
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0
