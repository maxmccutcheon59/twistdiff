"""Tests for root-locus-free damping sweep."""

from __future__ import annotations

import numpy as np
import pytest

from twistdiff.sweep import damping_sweep, parse_zeta_list


def test_parse_zeta_list():
    assert parse_zeta_list("0.2, 0.5,1.0") == [0.2, 0.5, 1.0]
    with pytest.raises(ValueError):
        parse_zeta_list("")
    with pytest.raises(ValueError):
        parse_zeta_list("0.2,abc")


def test_damping_sweep_overshoot_decreases_with_zeta():
    """Underdamped → more overshoot than critically/overdamped (classic)."""
    rows = damping_sweep([0.2, 0.7, 1.2], wn=2.0, t_end=30.0, dt=0.01)
    assert len(rows) == 3
    assert rows[0].metrics.overshoot_pct > rows[1].metrics.overshoot_pct
    assert rows[1].metrics.overshoot_pct > rows[2].metrics.overshoot_pct
    # Overdamped / near-critical should have little/no overshoot
    assert rows[2].metrics.overshoot_pct < 2.0


def test_damping_sweep_dc_gain_final():
    rows = damping_sweep([0.5], wn=3.0, gain=2.0, amplitude=1.0, t_end=25.0)
    assert rows[0].metrics.final_value == pytest.approx(2.0)
    # Peak should be at least the final for underdamped
    assert rows[0].metrics.peak_value >= rows[0].metrics.final_value - 1e-6


def test_damping_sweep_rejects_bad_zeta():
    with pytest.raises(ValueError):
        damping_sweep([])
    with pytest.raises(ValueError):
        damping_sweep([-0.1])
    with pytest.raises(ValueError):
        damping_sweep([np.nan])


def test_as_dict_includes_zeta():
    row = damping_sweep([0.4], t_end=15.0)[0]
    d = row.as_dict()
    assert d["zeta"] == pytest.approx(0.4)
    assert "overshoot_pct" in d
