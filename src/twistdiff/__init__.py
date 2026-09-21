"""twistdiff — lightweight ODE integration and PID control demos (CPU-only)."""

from __future__ import annotations

from twistdiff.models import CruiseControl, DampedHarmonicOscillator
from twistdiff.ode import Trajectory, integrate
from twistdiff.pid import PID

__version__ = "0.1.0"
__all__ = [
    "PID",
    "Trajectory",
    "integrate",
    "DampedHarmonicOscillator",
    "CruiseControl",
    "__version__",
]
