"""Step-response metrics for control demos (educational / research use)."""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class StepResponseMetrics:
    """Classic time-domain step-response figures of merit.

    Times are absolute (same units as ``t``). Fields that cannot be determined
    from the finite record are ``None`` (e.g. never entered the settling band).
    """

    rise_time: float | None
    overshoot_pct: float
    settling_time: float | None
    peak_time: float | None
    peak_value: float
    steady_state: float
    final_value: float

    def as_dict(self) -> dict[str, float | None]:
        return {
            "rise_time": self.rise_time,
            "overshoot_pct": self.overshoot_pct,
            "settling_time": self.settling_time,
            "peak_time": self.peak_time,
            "peak_value": self.peak_value,
            "steady_state": self.steady_state,
            "final_value": self.final_value,
        }


def _as_1d(name: str, arr: np.ndarray | list[float]) -> np.ndarray:
    a = np.asarray(arr, dtype=float).reshape(-1)
    if a.size == 0:
        raise ValueError(f"{name} must be non-empty")
    if not np.all(np.isfinite(a)):
        raise ValueError(f"{name} must be finite")
    return a


def step_response_metrics(
    t: np.ndarray | list[float],
    y: np.ndarray | list[float],
    *,
    y_final: float | None = None,
    rise_low: float = 0.1,
    rise_high: float = 0.9,
    settling_band: float = 0.02,
    y0: float | None = None,
) -> StepResponseMetrics:
    """Compute rise time, overshoot, and settling time for a step response.

    Definitions (standard textbook / interview convention)
    ------------------------------------------------------
    - **final_value**: ``y_final`` if given, else mean of the last 5% of samples
      (proxy for steady state on a finite record).
    - **rise_time**: first time ``y`` crosses ``y0 + rise_high * Δ`` minus first
      time it crosses ``y0 + rise_low * Δ``, where ``Δ = final_value - y0``
      (default 10%–90%). Requires ``Δ > 0``.
    - **overshoot_pct**: ``100 * (peak - final) / |Δ|`` using the peak in the
      direction of the step (max if ``Δ > 0``, min if ``Δ < 0``). Zero if no
      overshoot past the final value.
    - **settling_time**: first time after which ``|y - final|`` stays within
      ``settling_band * |Δ|`` for the remainder of the record (default 2% band).

    Parameters
    ----------
    t, y:
        Monotonic time vector and scalar output series of equal length.
    y_final:
        Known steady-state target (preferred when the reference is known).
    rise_low, rise_high:
        Fractional thresholds in ``(0, 1]`` with ``rise_low < rise_high``.
    settling_band:
        Fraction of ``|Δ|`` for the settling envelope (e.g. ``0.02`` → ±2%).
    y0:
        Initial output; defaults to ``y[0]``.
    """
    tt = _as_1d("t", t)
    yy = _as_1d("y", y)
    if tt.shape != yy.shape:
        raise ValueError("t and y must have the same length")
    if tt.size < 2:
        raise ValueError("need at least two samples")
    if np.any(np.diff(tt) < 0):
        raise ValueError("t must be non-decreasing")
    if not (0.0 < rise_low < rise_high <= 1.0):
        raise ValueError("require 0 < rise_low < rise_high <= 1")
    if not (isinstance(settling_band, (int, float)) and 0 < settling_band < 1):
        raise ValueError("settling_band must be in (0, 1)")

    y_start = float(yy[0] if y0 is None else y0)
    if y_final is None:
        n_tail = max(1, int(np.ceil(0.05 * yy.size)))
        y_ss = float(np.mean(yy[-n_tail:]))
    else:
        y_ss = float(y_final)
        if not np.isfinite(y_ss):
            raise ValueError("y_final must be finite")

    delta = y_ss - y_start
    abs_delta = abs(delta)
    final_value = y_ss

    # Peak in the direction of the step
    if delta >= 0:
        peak_idx = int(np.argmax(yy))
        peak_value = float(yy[peak_idx])
        overshoot = max(0.0, peak_value - y_ss)
    else:
        peak_idx = int(np.argmin(yy))
        peak_value = float(yy[peak_idx])
        overshoot = max(0.0, y_ss - peak_value)

    if abs_delta < 1e-15:
        overshoot_pct = 0.0
        rise_time = None
        settling_time = 0.0 if np.all(np.abs(yy - y_ss) <= settling_band) else None
        peak_time = float(tt[peak_idx])
        return StepResponseMetrics(
            rise_time=rise_time,
            overshoot_pct=overshoot_pct,
            settling_time=settling_time,
            peak_time=peak_time,
            peak_value=peak_value,
            steady_state=y_ss,
            final_value=final_value,
        )

    overshoot_pct = 100.0 * overshoot / abs_delta
    peak_time = float(tt[peak_idx])

    def _first_cross(level: float) -> float | None:
        # Crossing from below if delta>0, from above if delta<0
        if delta > 0:
            mask = yy >= level
        else:
            mask = yy <= level
        idxs = np.flatnonzero(mask)
        if idxs.size == 0:
            return None
        return float(tt[int(idxs[0])])

    t_lo = _first_cross(y_start + rise_low * delta)
    t_hi = _first_cross(y_start + rise_high * delta)
    if t_lo is None or t_hi is None or t_hi < t_lo:
        rise_time = None
    else:
        rise_time = t_hi - t_lo

    band = settling_band * abs_delta
    outside = np.abs(yy - y_ss) > band
    if not np.any(outside):
        settling_time = float(tt[0])
    else:
        last_out = int(np.flatnonzero(outside)[-1])
        if last_out >= yy.size - 1:
            settling_time = None  # never stayed inside through the end
        else:
            settling_time = float(tt[last_out + 1])

    return StepResponseMetrics(
        rise_time=rise_time,
        overshoot_pct=overshoot_pct,
        settling_time=settling_time,
        peak_time=peak_time,
        peak_value=peak_value,
        steady_state=y_ss,
        final_value=final_value,
    )
