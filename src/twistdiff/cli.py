"""Command-line demos for twistdiff."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np

from twistdiff import __version__
from twistdiff.models import CruiseControl, DampedHarmonicOscillator
from twistdiff.ode import integrate
from twistdiff.pid import PID


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
    print(
        f"steps={n}  t_end={t[-1]:.4f}  v_final={v[-1]:.4f}  "
        f"setpoint={args.setpoint:.4f}  err={args.setpoint - v[-1]:.4f}"
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


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="twistdiff",
        description="ODE integration + PID demos (CPU-only, educational).",
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

    return p


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.plot == "":
        args.plot = None
    try:
        return int(args.func(args))
    except (ValueError, FloatingPointError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
