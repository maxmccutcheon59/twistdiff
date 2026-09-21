"""CLI smoke tests."""

from __future__ import annotations

import pytest

from twistdiff.cli import main


def test_oscillator_cli(capsys):
    assert main(["oscillator", "--t-end", "1.0", "--dt", "0.05"]) == 0
    out = capsys.readouterr().out
    assert "steps=" in out


def test_cruise_cli(capsys):
    assert main(["cruise", "--t-end", "2.0", "--dt", "0.1"]) == 0
    out = capsys.readouterr().out
    assert "v_final=" in out
    assert "metrics" in out


def test_second_order_cli(capsys):
    assert main(["second-order", "--t-end", "5.0", "--dt", "0.05", "--zeta", "0.4"]) == 0
    out = capsys.readouterr().out
    assert "metrics" in out
    assert "overshoot%" in out


def test_version():
    with pytest.raises(SystemExit) as exc:
        main(["--version"])
    assert exc.value.code == 0


def test_damping_sweep_cli(capsys):
    assert main(["damping-sweep", "--zetas", "0.3,1.0", "--t-end", "8.0", "--dt", "0.05"]) == 0
    out = capsys.readouterr().out
    assert "damping sweep" in out.lower() or "not a root locus" in out.lower()
    assert "overshoot%" in out
