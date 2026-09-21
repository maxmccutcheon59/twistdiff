"""Parameter sweeps for educational control demos (no root-locus plots)."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from twistdiff.metrics import StepResponseMetrics, step_response_metrics
from twistdiff.statespace import second_order_plant


@dataclass(frozen=True)
class DampingSweepRow:
    """One ζ sample: time-domain step metrics for a fixed ωn plant.

    This is intentionally **not** a root-locus construction — poles are not
    plotted. Interview story: sweep damping, watch overshoot / settling move.
    """

    zeta: float
    metrics: StepResponseMetrics

    def as_dict(self) -> dict[str, float | None]:
        d = self.metrics.as_dict()
        d["zeta"] = self.zeta
        return d


def damping_sweep(
    zetas: Sequence[float],
    *,
    wn: float = 2.0,
    gain: float = 1.0,
    amplitude: float = 1.0,
    t_end: float = 25.0,
    dt: float = 0.01,
    method: str = "rk4",
) -> list[DampingSweepRow]:
    """Sweep damping ratio ζ on a second-order plant; return step metrics per ζ.

    Uses the same controllable-canonical plant as :func:`second_order_plant` and
    the same definitions as :func:`step_response_metrics`. Educational only —
    not a substitute for classical root-locus / Routh design tools.

    Parameters
    ----------
    zetas:
        Non-negative finite damping ratios to evaluate (order preserved).
    wn, gain:
        Natural frequency and DC gain of ``G(s)``.
    amplitude:
        Step input size (final value ≈ ``amplitude * gain``).
    t_end, dt, method:
        Forwarded to :meth:`StateSpace.simulate_step`.
    """
    if len(zetas) == 0:
        raise ValueError("zetas must be non-empty")
    rows: list[DampingSweepRow] = []
    y_final = float(amplitude) * float(gain)
    for z in zetas:
        zf = float(z)
        if not np.isfinite(zf) or zf < 0.0:
            raise ValueError(f"each zeta must be non-negative and finite, got {z!r}")
        plant = second_order_plant(wn=wn, zeta=zf, gain=gain)
        t, y, _ = plant.simulate_step(
            amplitude, t_end=t_end, dt=dt, method=method
        )
        m = step_response_metrics(t, y[:, 0], y_final=y_final)
        rows.append(DampingSweepRow(zeta=zf, metrics=m))
    return rows


def parse_zeta_list(text: str) -> list[float]:
    """Parse a comma-separated ζ list for the CLI (e.g. ``0.2,0.5,1.0``)."""
    parts = [p.strip() for p in text.split(",")]
    parts = [p for p in parts if p]
    if not parts:
        raise ValueError("zeta list is empty")
    out: list[float] = []
    for p in parts:
        try:
            v = float(p)
        except ValueError as exc:
            raise ValueError(f"invalid zeta value: {p!r}") from exc
        out.append(v)
    return out
