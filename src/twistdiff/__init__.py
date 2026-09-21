"""twistdiff — lightweight ODE integration and PID control demos (CPU-only)."""

from __future__ import annotations

from twistdiff.metrics import StepResponseMetrics, step_response_metrics
from twistdiff.models import CruiseControl, DampedHarmonicOscillator
from twistdiff.ode import Trajectory, integrate
from twistdiff.pid import PID
from twistdiff.statespace import StateSpace, second_order_plant
from twistdiff.sweep import DampingSweepRow, damping_sweep

__version__ = "0.2.1"
__all__ = [
    "PID",
    "Trajectory",
    "integrate",
    "DampedHarmonicOscillator",
    "CruiseControl",
    "StateSpace",
    "second_order_plant",
    "StepResponseMetrics",
    "step_response_metrics",
    "DampingSweepRow",
    "damping_sweep",
    "__version__",
]
