"""Tests for ODE integrators."""

from __future__ import annotations

import numpy as np
import pytest

from twistdiff.ode import integrate


def test_exponential_decay_rk4():
    # y' = -y, y(0)=1 -> y(t)=e^{-t}
    traj = integrate(lambda t, y: -y, y0=1.0, t_span=(0.0, 2.0), dt=0.01, method="rk4")
    assert traj.y[-1, 0] == pytest.approx(np.exp(-2.0), rel=1e-4)


def test_euler_less_accurate_than_rk4():
    def f(t, y):
        return -y

    euler = integrate(f, 1.0, (0.0, 1.0), dt=0.1, method="euler")
    rk4 = integrate(f, 1.0, (0.0, 1.0), dt=0.1, method="rk4")
    truth = np.exp(-1.0)
    assert abs(rk4.y[-1, 0] - truth) < abs(euler.y[-1, 0] - truth)


def test_rejects_bad_inputs():
    with pytest.raises(ValueError):
        integrate(lambda t, y: y, 1.0, (0.0, 1.0), dt=-0.1)
    with pytest.raises(ValueError):
        integrate(lambda t, y: y, 1.0, (1.0, 0.0), dt=0.1)
    with pytest.raises(ValueError):
        integrate(lambda t, y: y, 1.0, (0.0, 1.0), method="bogus")  # type: ignore[arg-type]


def test_trajectory_shapes():
    traj = integrate(lambda t, y: np.zeros_like(y), [1.0, 2.0], (0.0, 1.0), dt=0.25)
    assert traj.t.shape[0] == traj.y.shape[0]
    assert traj.y.shape[1] == 2
