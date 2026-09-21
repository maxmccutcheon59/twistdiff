"""Continuous-time linear state-space plants (educational LTI demos)."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass

import numpy as np

from twistdiff.ode import RHS


def _as_2d(
    name: str,
    arr: np.ndarray | list | float,
    *,
    rows: int | None = None,
    cols: int | None = None,
) -> np.ndarray:
    a = np.asarray(arr, dtype=float)
    if a.ndim == 0:
        a = a.reshape(1, 1)
    elif a.ndim == 1:
        a = a.reshape(-1, 1) if cols == 1 else a.reshape(1, -1)
    if a.ndim != 2:
        raise ValueError(f"{name} must be 2-D")
    if rows is not None and a.shape[0] != rows:
        raise ValueError(f"{name} must have {rows} rows, got {a.shape[0]}")
    if cols is not None and a.shape[1] != cols:
        raise ValueError(f"{name} must have {cols} columns, got {a.shape[1]}")
    if not np.all(np.isfinite(a)):
        raise ValueError(f"{name} must be finite")
    return a.copy()


@dataclass(frozen=True)
class StateSpace:
    """Continuous LTI system ``ẋ = A x + B u``, ``y = C x + D u``.

    Matrices are stored as float ``ndarray``. SISO is the common demo case
    (``B`` n×1, ``C`` 1×n, ``D`` 1×1) but MIMO shapes are accepted if consistent.
    """

    A: np.ndarray
    B: np.ndarray
    C: np.ndarray
    D: np.ndarray

    def __post_init__(self) -> None:
        A = _as_2d("A", self.A)
        n = A.shape[0]
        if A.shape[1] != n:
            raise ValueError("A must be square")
        B = _as_2d("B", self.B, rows=n)
        m = B.shape[1]
        C = _as_2d("C", self.C, cols=n)
        p = C.shape[0]
        D = _as_2d("D", self.D, rows=p, cols=m)
        object.__setattr__(self, "A", A)
        object.__setattr__(self, "B", B)
        object.__setattr__(self, "C", C)
        object.__setattr__(self, "D", D)

    @property
    def n_states(self) -> int:
        return int(self.A.shape[0])

    @property
    def n_inputs(self) -> int:
        return int(self.B.shape[1])

    @property
    def n_outputs(self) -> int:
        return int(self.C.shape[0])

    def rhs(self, u: Callable[[float], float | np.ndarray] | float | np.ndarray = 0.0) -> RHS:
        """Build ``f(t, x) = A x + B u(t)`` for :func:`twistdiff.ode.integrate`."""
        A, B = self.A, self.B

        def f(t: float, x: np.ndarray) -> np.ndarray:
            if callable(u):
                uu = np.asarray(u(t), dtype=float).reshape(-1)
            else:
                uu = np.asarray(u, dtype=float).reshape(-1)
            if uu.size != B.shape[1]:
                raise ValueError(f"u must have length {B.shape[1]}, got {uu.size}")
            return A @ x + B @ uu

        return f

    def output(self, x: np.ndarray, u: float | np.ndarray = 0.0) -> np.ndarray:
        """``y = C x + D u``."""
        uu = np.asarray(u, dtype=float).reshape(-1)
        xx = np.asarray(x, dtype=float).reshape(-1)
        if xx.size != self.n_states:
            raise ValueError(f"x must have length {self.n_states}")
        if uu.size != self.n_inputs:
            raise ValueError(f"u must have length {self.n_inputs}")
        return self.C @ xx + self.D @ uu

    def simulate_step(
        self,
        u_value: float,
        *,
        t_end: float = 20.0,
        dt: float = 0.01,
        x0: np.ndarray | list[float] | None = None,
        method: str = "rk4",
    ) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        """Open-loop unit/custom step response.

        Returns
        -------
        t, y, x
            Time vector, output series (shape ``(N, p)``), state series ``(N, n)``.
        """
        from twistdiff.ode import integrate

        if x0 is None:
            x0 = np.zeros(self.n_states)
        traj = integrate(
            self.rhs(
                float(u_value)
                if self.n_inputs == 1
                else np.full(self.n_inputs, float(u_value))
            ),
            y0=x0,
            t_span=(0.0, t_end),
            dt=dt,
            method=method,  # type: ignore[arg-type]
        )
        y = np.empty((traj.y.shape[0], self.n_outputs), dtype=float)
        u_vec = np.full(self.n_inputs, float(u_value))
        for i in range(traj.y.shape[0]):
            y[i] = self.output(traj.y[i], u_vec)
        return traj.t, y, traj.y


def second_order_plant(
    wn: float = 2.0,
    zeta: float = 0.3,
    *,
    gain: float = 1.0,
) -> StateSpace:
    """Classic second-order SISO plant in controllable canonical form.

    Transfer function::

        G(s) = gain * wn² / (s² + 2 ζ wn s + wn²)

    State: ``[x1, x2]`` with output ``y = gain * wn² * x1`` (position-like).
    """
    if not (isinstance(wn, (int, float)) and np.isfinite(wn) and wn > 0):
        raise ValueError("wn (natural frequency) must be positive and finite")
    if not (isinstance(zeta, (int, float)) and np.isfinite(zeta) and zeta >= 0):
        raise ValueError("zeta (damping ratio) must be non-negative and finite")
    if not (isinstance(gain, (int, float)) and np.isfinite(gain)):
        raise ValueError("gain must be finite")
    wn = float(wn)
    zeta = float(zeta)
    gain = float(gain)
    A = np.array([[0.0, 1.0], [-wn * wn, -2.0 * zeta * wn]], dtype=float)
    B = np.array([[0.0], [1.0]], dtype=float)
    C = np.array([[gain * wn * wn, 0.0]], dtype=float)
    D = np.array([[0.0]], dtype=float)
    return StateSpace(A=A, B=B, C=C, D=D)
