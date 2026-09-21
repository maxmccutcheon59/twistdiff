"""Simple physics-lite plant models for demos."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from twistdiff.ode import RHS


@dataclass(frozen=True)
class DampedHarmonicOscillator:
    """``m x'' + c x' + k x = 0`` (or forced via optional ``force(t)``).

    State vector: ``[x, v]``.
    """

    mass: float = 1.0
    damping: float = 0.2
    stiffness: float = 4.0

    def __post_init__(self) -> None:
        if self.mass <= 0:
            raise ValueError("mass must be positive")
        if self.stiffness < 0 or self.damping < 0:
            raise ValueError("damping and stiffness must be non-negative")

    def rhs(self, force: Callable[[float], float] | None = None) -> RHS:
        m, c, k = self.mass, self.damping, self.stiffness

        def f(t: float, y: np.ndarray) -> np.ndarray:
            x, v = float(y[0]), float(y[1])
            u = float(force(t)) if force is not None else 0.0
            a = (u - c * v - k * x) / m
            return np.array([v, a], dtype=float)

        return f


@dataclass(frozen=True)
class CruiseControl:
    """1-D point-mass cruise plant: ``m v' = u - b v`` (drag-like resistance).

    State vector: ``[v]`` (speed). Control ``u`` is force/thrust from a PID.
    """

    mass: float = 1000.0
    drag: float = 50.0

    def __post_init__(self) -> None:
        if self.mass <= 0:
            raise ValueError("mass must be positive")
        if self.drag < 0:
            raise ValueError("drag must be non-negative")

    def closed_loop(self, controller) -> RHS:
        """Build ``f(t, y)`` that queries ``controller.update(v, dt_hint)``.

        The PID is advanced with the integrator's step size via a small
        attribute ``_pending_dt`` set by the demo loop, or defaults to 0.01.
        Prefer :meth:`step` for fixed-step PID demos.
        """
        m, b = self.mass, self.drag

        def f(t: float, y: np.ndarray) -> np.ndarray:
            v = float(y[0])
            dt = getattr(controller, "_pending_dt", 0.01)
            u = float(controller.update(v, dt))
            a = (u - b * v) / m
            return np.array([a], dtype=float)

        return f

    def accel(self, v: float, u: float) -> float:
        return (u - self.drag * v) / self.mass
