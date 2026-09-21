"""Tests for PID controller."""

from __future__ import annotations

import pytest

from twistdiff.pid import PID


def test_proportional_only():
    pid = PID(kp=2.0, setpoint=10.0)
    u = pid.update(measurement=8.0, dt=0.1)
    assert u == pytest.approx(4.0)


def test_output_limits_and_antiwindup():
    pid = PID(kp=0.0, ki=100.0, setpoint=1.0, output_limits=(0.0, 1.0))
    for _ in range(20):
        u = pid.update(0.0, 0.1)
    assert 0.0 <= u <= 1.0
    # Integral should not grow unboundedly under saturation
    assert abs(pid._integral) < 50.0


def test_reset_clears_state():
    pid = PID(kp=1.0, ki=1.0, kd=1.0, setpoint=5.0)
    pid.update(0.0, 0.1)
    pid.reset()
    assert pid._integral == 0.0
    assert pid._prev_error is None


def test_bad_dt():
    pid = PID(kp=1.0)
    with pytest.raises(ValueError):
        pid.update(0.0, 0.0)
