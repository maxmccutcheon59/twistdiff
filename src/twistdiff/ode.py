"""Explicit ODE integrators (Euler, RK4) — educational / research use."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Literal

import numpy as np

Method = Literal["euler", "rk4"]
RHS = Callable[[float, np.ndarray], np.ndarray]


@dataclass(frozen=True)
class Trajectory:
    """Time series returned by :func:`integrate`."""

    t: np.ndarray
    y: np.ndarray  # shape (n_steps, n_state)

    def __post_init__(self) -> None:
        if self.t.ndim != 1:
            raise ValueError("t must be 1-D")
        if self.y.ndim != 2:
            raise ValueError("y must be 2-D (n_steps, n_state)")
        if self.t.shape[0] != self.y.shape[0]:
            raise ValueError("t and y must share the same length")


def _as_state(y0: np.ndarray | list[float] | float) -> np.ndarray:
    arr = np.asarray(y0, dtype=float)
    if arr.ndim == 0:
        arr = arr.reshape(1)
    if arr.ndim != 1:
        raise ValueError("y0 must be a scalar or 1-D array")
    if not np.all(np.isfinite(arr)):
        raise ValueError("y0 must be finite")
    return arr.copy()


def _euler_step(f: RHS, t: float, y: np.ndarray, dt: float) -> np.ndarray:
    return y + dt * np.asarray(f(t, y), dtype=float)


def _rk4_step(f: RHS, t: float, y: np.ndarray, dt: float) -> np.ndarray:
    k1 = np.asarray(f(t, y), dtype=float)
    k2 = np.asarray(f(t + 0.5 * dt, y + 0.5 * dt * k1), dtype=float)
    k3 = np.asarray(f(t + 0.5 * dt, y + 0.5 * dt * k2), dtype=float)
    k4 = np.asarray(f(t + dt, y + dt * k3), dtype=float)
    return y + (dt / 6.0) * (k1 + 2 * k2 + 2 * k3 + k4)


_STEPPERS = {
    "euler": _euler_step,
    "rk4": _rk4_step,
}


def integrate(
    f: RHS,
    y0: np.ndarray | list[float] | float,
    t_span: tuple[float, float],
    *,
    dt: float = 0.01,
    method: Method = "rk4",
) -> Trajectory:
    """Integrate ``dy/dt = f(t, y)`` from ``t_span[0]`` to ``t_span[1]``.

    Parameters
    ----------
    f:
        Right-hand side ``f(t, y) -> dy/dt``.
    y0:
        Initial state (scalar or 1-D).
    t_span:
        ``(t0, t_end)``. ``t_end`` must be strictly greater than ``t0``.
    dt:
        Fixed step size (must be positive and finite).
    method:
        ``\"rk4\"`` (default) or ``\"euler\"``.

    Returns
    -------
    Trajectory
        Arrays ``t`` and ``y`` including the initial condition.
    """
    if method not in _STEPPERS:
        raise ValueError(f"unknown method {method!r}; choose from {sorted(_STEPPERS)}")
    if not (isinstance(dt, (int, float)) and np.isfinite(dt) and dt > 0):
        raise ValueError("dt must be a positive finite number")
    t0, t_end = float(t_span[0]), float(t_span[1])
    if not (np.isfinite(t0) and np.isfinite(t_end)):
        raise ValueError("t_span values must be finite")
    if t_end <= t0:
        raise ValueError("t_span requires t_end > t0")

    y = _as_state(y0)
    step = _STEPPERS[method]
    # Inclusive endpoint via n_steps intervals
    n_steps = int(np.ceil((t_end - t0) / dt))
    t = np.empty(n_steps + 1, dtype=float)
    ys = np.empty((n_steps + 1, y.size), dtype=float)
    t[0] = t0
    ys[0] = y

    for i in range(n_steps):
        remaining = t_end - t[i]
        h = dt if remaining > dt else remaining
        if h <= 0:
            t = t[: i + 1]
            ys = ys[: i + 1]
            break
        y = step(f, t[i], y, h)
        if not np.all(np.isfinite(y)):
            raise FloatingPointError(f"non-finite state at t={t[i] + h}")
        t[i + 1] = t[i] + h
        ys[i + 1] = y
    else:
        # Snap final time exactly to t_end when last step was full dt
        t[-1] = t_end

    return Trajectory(t=t, y=ys)
