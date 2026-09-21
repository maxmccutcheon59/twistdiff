"""Tests for step-response metrics."""

from __future__ import annotations

import numpy as np
import pytest

from twistdiff.metrics import step_response_metrics
from twistdiff.statespace import second_order_plant


def test_ideal_first_order_like_ramp_then_flat():
    # Synthetic: rise linearly 0→1 over [0,1], then flat — rise 10–90% = 0.8
    t = np.linspace(0.0, 5.0, 501)
    y = np.clip(t, 0.0, 1.0)
    m = step_response_metrics(t, y, y_final=1.0)
    assert m.rise_time == pytest.approx(0.8, abs=0.02)
    assert m.overshoot_pct == pytest.approx(0.0, abs=1e-9)
    assert m.settling_time is not None
    assert m.settling_time == pytest.approx(1.0, abs=0.02)
    assert m.peak_value == pytest.approx(1.0)


def test_overshoot_on_second_order_underdamped():
    plant = second_order_plant(wn=2.0, zeta=0.2, gain=1.0)
    t, y, _ = plant.simulate_step(1.0, t_end=30.0, dt=0.005)
    m = step_response_metrics(t, y[:, 0], y_final=1.0)
    # Analytic %OS ≈ 100*exp(-ζπ / sqrt(1-ζ²)) for underdamped 2nd order
    analytic = 100.0 * np.exp(-0.2 * np.pi / np.sqrt(1.0 - 0.2**2))
    assert m.overshoot_pct == pytest.approx(analytic, rel=0.15)
    assert m.rise_time is not None and m.rise_time > 0
    assert m.settling_time is not None and m.settling_time > m.rise_time


def test_overdamped_little_overshoot():
    plant = second_order_plant(wn=1.5, zeta=1.5, gain=1.0)
    t, y, _ = plant.simulate_step(1.0, t_end=40.0, dt=0.01)
    m = step_response_metrics(t, y[:, 0], y_final=1.0)
    assert m.overshoot_pct < 1.0


def test_rejects_bad_inputs():
    t = np.linspace(0, 1, 10)
    y = np.linspace(0, 1, 10)
    with pytest.raises(ValueError):
        step_response_metrics(t, y[:-1])
    with pytest.raises(ValueError):
        step_response_metrics(t[::-1], y)
    with pytest.raises(ValueError):
        step_response_metrics(t, y, rise_low=0.9, rise_high=0.1)


def test_as_dict_keys():
    t = np.linspace(0, 2, 21)
    y = 1.0 - np.exp(-t)
    d = step_response_metrics(t, y, y_final=1.0).as_dict()
    assert set(d) >= {"rise_time", "overshoot_pct", "settling_time", "peak_value"}
