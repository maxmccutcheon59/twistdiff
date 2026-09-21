"""Command-line demos for twistdiff."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from twistdiff import __version__
from twistdiff.metrics import step_response_metrics
from twistdiff.models import CruiseControl, DampedHarmonicOscillator
from twistdiff.ode import integrate
from twistdiff.pid import PID
from twistdiff.statespace import second_order_plant


def _cmd_oscillator(args: argparse.Namespace) -> int:
    plant = DampedHarmonicOscillator(
        mass=args.mass, damping=args.damping, stiffness=args.stiffness
    )
    traj = integrate(
        plant.rhs(),
        y0=[args.x0, args.v0],
        t_span=(0.0, args.t_end),
        dt=args.dt,
        method=args.method,
    )
    print(f"steps={len(traj.t) - 1}  t_end={traj.t[-1]:.4f}  x_final={traj.y[-1, 0]:.6f}")
    if args.plot:
        from twistdiff.plotting import save_trajectory_plot

        out = Path(args.plot)
        save_trajectory_plot(
            traj,
            out,
            labels=["position", "velocity"],
            title="Damped harmonic oscillator",
        )
        print(f"wrote {out}")
    return 0


def _cmd_cruise(args: argparse.Namespace) -> int:
    plant = CruiseControl(mass=args.mass, drag=args.drag)
    pid = PID(
        kp=args.kp,
        ki=args.ki,
        kd=args.kd,
        setpoint=args.setpoint,
        output_limits=(args.u_min, args.u_max),
    )
    dt = args.dt
    n = int(np.ceil(args.t_end / dt))
    t = np.empty(n + 1)
    v = np.empty(n + 1)
    u_hist = np.empty(n + 1)
    t[0] = 0.0
    v[0] = args.v0
    u_hist[0] = 0.0
    for i in range(n):
        u = pid.update(v[i], dt)
        a = plant.accel(v[i], u)
        v[i + 1] = v[i] + dt * a
        t[i + 1] = t[i] + dt
        u_hist[i + 1] = u
    metrics = step_response_metrics(t, v, y_final=args.setpoint)
    print(
        f"steps={n}  t_end={t[-1]:.4f}  v_final={v[-1]:.4f}  "
        f"setpoint={args.setpoint:.4f}  err={args.setpoint - v[-1]:.4f}"
    )
    print(
        f"metrics  rise={_fmt(metrics.rise_time)}  "
        f"overshoot%={metrics.overshoot_pct:.2f}  "
        f"settling={_fmt(metrics.settling_time)}"
    )
    if args.plot:
        from twistdiff.plotting import save_series_plot

        out = Path(args.plot)
        save_series_plot(
            t,
            {"speed": v, "setpoint": np.full_like(t, args.setpoint), "thrust_u": u_hist},
            out,
            title="1-D cruise control (PID)",
            ylabel="value",
        )
        print(f"wrote {out}")
    return 0


def _cmd_second_order(args: argparse.Namespace) -> int:
    plant = second_order_plant(wn=args.wn, zeta=args.zeta, gain=args.gain)
    t, y, x = plant.simulate_step(
        args.amplitude,
        t_end=args.t_end,
        dt=args.dt,
        method=args.method,
    )
    y1 = y[:, 0]
    # Analytic DC gain of G(s) is `gain` for a unit step of amplitude A → A*gain
    y_final = args.amplitude * args.gain
    metrics = step_response_metrics(t, y1, y_final=y_final)
    print(
        f"wn={args.wn:.4f}  zeta={args.zeta:.4f}  gain={args.gain:.4f}  "
        f"steps={len(t) - 1}  y_final={y1[-1]:.6f}"
    )
    print(
        f"metrics  rise={_fmt(metrics.rise_time)}  "
        f"overshoot%={metrics.overshoot_pct:.2f}  "
        f"settling={_fmt(metrics.settling_time)}  "
        f"peak={metrics.peak_value:.6f}@{_fmt(metrics.peak_time)}"
    )
    if args.plot:
        from twistdiff.plotting import save_series_plot

        out = Path(args.plot)
        save_series_plot(
            t,
            {
                "y": y1,
                "x1": x[:, 0],
                "x2": x[:, 1],
                "ref": np.full_like(t, y_final),
            },
            out,
            title=f"Second-order plant (ζ={args.zeta}, ωn={args.wn})",
            ylabel="value",
        )
        print(f"wrote {out}")
    return 0


def _fmt(v: float | None) -> str:
    if v is None:
        return "None"
    return f"{v:.4f}"


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="twistdiff",
        description="ODE integration + PID / LTI demos (CPU-only, educational).",
    )
    p.add_argument("--version", action="version", version=f"%(prog)s {__version__}")
    sub = p.add_subparsers(dest="command", required=True)

    o = sub.add_parser("oscillator", help="Damped harmonic oscillator free response")
    o.add_argument("--mass", type=float, default=1.0)
    o.add_argument("--damping", type=float, default=0.2)
    o.add_argument("--stiffness", type=float, default=4.0)
    o.add_argument("--x0", type=float, default=1.0)
    o.add_argument("--v0", type=float, default=0.0)
    o.add_argument("--t-end", type=float, default=20.0)
    o.add_argument("--dt", type=float, default=0.01)
    o.add_argument("--method", choices=["rk4", "euler"], default="rk4")
    o.add_argument("--plot", type=str, default="", help="Optional PNG output path")
    o.set_defaults(func=_cmd_oscillator)

    c = sub.add_parser("cruise", help="1-D cruise control with PID")
    c.add_argument("--mass", type=float, default=1000.0)
    c.add_argument("--drag", type=float, default=50.0)
    c.add_argument("--v0", type=float, default=0.0)
    c.add_argument("--setpoint", type=float, default=25.0)
    c.add_argument("--kp", type=float, default=800.0)
    c.add_argument("--ki", type=float, default=40.0)
    c.add_argument("--kd", type=float, default=50.0)
    c.add_argument("--u-min", type=float, default=0.0)
    c.add_argument("--u-max", type=float, default=5000.0)
    c.add_argument("--t-end", type=float, default=40.0)
    c.add_argument("--dt", type=float, default=0.05)
    c.add_argument("--plot", type=str, default="", help="Optional PNG output path")
    c.set_defaults(func=_cmd_cruise)

    s = sub.add_parser(
        "second-order",
        help="Second-order LTI plant step response (state-space) + metrics",
    )
    s.add_argument("--wn", type=float, default=2.0, help="Natural frequency ωn > 0")
    s.add_argument("--zeta", type=float, default=0.3, help="Damping ratio ζ ≥ 0")
    s.add_argument("--gain", type=float, default=1.0, help="DC gain of G(s)")
    s.add_argument("--amplitude", type=float, default=1.0, help="Step input amplitude")
    s.add_argument("--t-end", type=float, default=20.0)
    s.add_argument("--dt", type=float, default=0.01)
    s.add_argument("--method", choices=["rk4", "euler"], default="rk4")
    s.add_argument("--plot", type=str, default="", help="Optional PNG output path")
    s.set_defaults(func=_cmd_second_order)

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.plot == "":
        args.plot = None
    try:
        return int(args.func(args))
    except (ValueError, FloatingPointError, TypeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
