"""Discrete PID controller with optional output clamping and integral windup guard."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class PID:
    """Classic parallel-form PID: ``u = Kp*e + Ki*∫e dt + Kd*de/dt``.

    Designed for fixed-step simulation loops (educational / research demos).
    Not a certified industrial controller.
    """

    kp: float
    ki: float = 0.0
    kd: float = 0.0
    setpoint: float = 0.0
    output_limits: tuple[float | None, float | None] = (None, None)
    _integral: float = field(default=0.0, init=False, repr=False)
    _prev_error: float | None = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        for name in ("kp", "ki", "kd", "setpoint"):
            val = getattr(self, name)
            if not isinstance(val, (int, float)):
                raise TypeError(f"{name} must be a number")
        lo, hi = self.output_limits
        if lo is not None and hi is not None and lo > hi:
            raise ValueError("output_limits lower bound must be <= upper bound")

    def reset(self) -> None:
        """Clear integral and derivative history."""
        self._integral = 0.0
        self._prev_error = None

    def update(self, measurement: float, dt: float) -> float:
        """Compute control output for one sample.

        Parameters
        ----------
        measurement:
            Process variable.
        dt:
            Sample period (seconds); must be positive.
        """
        if not (isinstance(dt, (int, float)) and dt > 0):
            raise ValueError("dt must be positive")
        error = self.setpoint - float(measurement)
        self._integral += error * dt

        if self._prev_error is None:
            derivative = 0.0
        else:
            derivative = (error - self._prev_error) / dt
        self._prev_error = error

        u = self.kp * error + self.ki * self._integral + self.kd * derivative
        lo, hi = self.output_limits
        if lo is not None or hi is not None:
            u_clamped = u
            if lo is not None:
                u_clamped = max(lo, u_clamped)
            if hi is not None:
                u_clamped = min(hi, u_clamped)
            # Conditional integration (anti-windup): freeze integral if saturating
            if u_clamped != u:
                self._integral -= error * dt
            u = u_clamped
        return u
