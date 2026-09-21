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
from twistdiff.sweep import damping_sweep, parse_zeta_list


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



def _cmd_damping_sweep(args: argparse.Namespace) -> int:
    """Root-locus-free ζ sweep: time-domain metrics only (honest edu)."""
    zetas = parse_zeta_list(args.zetas)
    rows = damping_sweep(
        zetas,
        wn=args.wn,
        gain=args.gain,
        amplitude=args.amplitude,
        t_end=args.t_end,
        dt=args.dt,
        method=args.method,
    )
    print(
        f"wn={args.wn:.4f}  gain={args.gain:.4f}  amplitude={args.amplitude:.4f}  "
        f"n={len(rows)}  (damping sweep — not a root locus)"
    )
    print(f"{'zeta':>8}  {'rise':>10}  {'overshoot%':>10}  {'settling':>10}  {'peak':>10}")
    for row in rows:
        m = row.metrics
        print(
            f"{row.zeta:8.4f}  {_fmt(m.rise_time):>10}  {m.overshoot_pct:10.2f}  "
            f"{_fmt(m.settling_time):>10}  {m.peak_value:10.6f}"
        )
    if args.plot:
        from twistdiff.plotting import save_series_plot

        out = Path(args.plot)
        zz = np.array([r.zeta for r in rows], dtype=float)
        # Metrics vs ζ — use zeta as the independent axis (not time).
        overshoot = np.array([r.metrics.overshoot_pct for r in rows], dtype=float)
        # None settling → nan so matplotlib gaps honestly
        settling = np.array(
            [
                np.nan if r.metrics.settling_time is None else r.metrics.settling_time
                for r in rows
            ],
            dtype=float,
        )
        rise = np.array(
            [np.nan if r.metrics.rise_time is None else r.metrics.rise_time for r in rows],
            dtype=float,
        )
        save_series_plot(
            zz,
            {
                "overshoot_%": overshoot,
                "settling_time": settling,
                "rise_time": rise,
            },
            out,
            title=f"Damping sweep (ωn={args.wn}) — not a root locus",
            xlabel="ζ",
            ylabel="metric",
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

    d = sub.add_parser(
        "damping-sweep",
        help="Root-locus-free ζ sweep: step metrics vs damping (honest edu)",
    )
    d.add_argument(
        "--zetas",
        type=str,
        default="0.2,0.5,0.7,1.0,1.5",
        help="Comma-separated damping ratios (default: under→overdamped set)",
    )
    d.add_argument("--wn", type=float, default=2.0, help="Natural frequency ωn > 0")
    d.add_argument("--gain", type=float, default=1.0, help="DC gain of G(s)")
    d.add_argument("--amplitude", type=float, default=1.0, help="Step input amplitude")
    d.add_argument("--t-end", type=float, default=25.0)
    d.add_argument("--dt", type=float, default=0.01)
    d.add_argument("--method", choices=["rk4", "euler"], default="rk4")
    d.add_argument(
        "--plot",
        type=str,
        default="",
        help="Optional PNG: metrics vs ζ (not a root-locus diagram)",
    )
    d.set_defaults(func=_cmd_damping_sweep)

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
