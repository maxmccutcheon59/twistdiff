"""Tests for plant models."""

from __future__ import annotations

import pytest

from twistdiff.models import CruiseControl, DampedHarmonicOscillator
from twistdiff.ode import integrate
from twistdiff.pid import PID


def test_oscillator_energy_decays():
    plant = DampedHarmonicOscillator(mass=1.0, damping=0.5, stiffness=4.0)
    traj = integrate(plant.rhs(), [1.0, 0.0], (0.0, 30.0), dt=0.01)
    # Underdamped to near rest
    assert abs(traj.y[-1, 0]) < 0.05
    assert abs(traj.y[-1, 1]) < 0.05


def test_oscillator_rejects_bad_mass():
    with pytest.raises(ValueError):
        DampedHarmonicOscillator(mass=0.0)


def test_cruise_pid_reaches_setpoint():
    plant = CruiseControl(mass=1000.0, drag=50.0)
    pid = PID(kp=800.0, ki=40.0, kd=50.0, setpoint=25.0, output_limits=(0.0, 5000.0))
    dt = 0.05
    v = 0.0
    for _ in range(800):
        u = pid.update(v, dt)
        v = v + dt * plant.accel(v, u)
    assert v == pytest.approx(25.0, abs=0.5)


def test_cruise_accel():
    plant = CruiseControl(mass=1000.0, drag=0.0)
    assert plant.accel(0.0, 1000.0) == pytest.approx(1.0)
