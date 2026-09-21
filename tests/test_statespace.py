"""Tests for state-space / second-order plant."""

from __future__ import annotations

import numpy as np
import pytest

from twistdiff.ode import integrate
from twistdiff.statespace import StateSpace, second_order_plant


def test_second_order_dc_gain():
    plant = second_order_plant(wn=3.0, zeta=0.7, gain=2.0)
    t, y, _ = plant.simulate_step(1.0, t_end=25.0, dt=0.01)
    assert y[-1, 0] == pytest.approx(2.0, abs=0.05)


def test_state_space_shapes_and_output():
    ss = StateSpace(
        A=[[0.0, 1.0], [-4.0, -0.4]],
        B=[[0.0], [1.0]],
        C=[[1.0, 0.0]],
        D=[[0.0]],
    )
    assert ss.n_states == 2
    assert ss.n_inputs == 1
    assert ss.n_outputs == 1
    y = ss.output([1.0, 0.0], 0.0)
    assert y.shape == (1,)
    assert y[0] == pytest.approx(1.0)


def test_integrate_open_loop_matches_simulate():
    plant = second_order_plant(wn=1.0, zeta=0.5)
    traj = integrate(plant.rhs(1.0), [0.0, 0.0], (0.0, 5.0), dt=0.01)
    t, y, x = plant.simulate_step(1.0, t_end=5.0, dt=0.01)
    assert np.allclose(traj.t, t)
    assert np.allclose(traj.y, x)
    assert np.allclose(y[:, 0], (plant.C @ traj.y.T).ravel())


def test_rejects_bad_wn_zeta():
    with pytest.raises(ValueError):
        second_order_plant(wn=0.0)
    with pytest.raises(ValueError):
        second_order_plant(wn=1.0, zeta=-0.1)


def test_rejects_nonsquare_a():
    with pytest.raises(ValueError):
        StateSpace(A=[[1.0, 0.0]], B=[[1.0]], C=[[1.0]], D=[[0.0]])
