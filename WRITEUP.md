# WRITEUP — twistdiff (v0.2.1)

Interview-oriented notes: how classical control intuition maps to this code.
**Honest edu/pro numerical tooling** — not a fake fusion company, not certified
industrial control software, not safety-rated for real plants or vehicles.

## What this repo is

| Layer | Idea | Code |
|-------|------|------|
| Numerics | Fixed-step ODE: Euler / RK4 | `twistdiff/ode.py` → `integrate` |
| Feedback | Discrete parallel PID + clamp / anti-windup | `twistdiff/pid.py` → `PID` |
| Plants | Oscillator, 1-D cruise, LTI state-space | `twistdiff/models.py`, `statespace.py` |
| Specs | Rise / overshoot / settling | `twistdiff/metrics.py` → `step_response_metrics` |
| Sweep | ζ → metrics (no root locus) | `twistdiff/sweep.py` → `damping_sweep` |
| Demo CLI | Reproduce plots + print metrics | `twistdiff/cli.py` |

CPU-only; required dep is **numpy**. **matplotlib** is optional (`[plot]`).

## Control intuition → code

### 1. Second-order plant (ζ, ωn)

Textbook transfer function:

\[
G(s) = \frac{K\,\omega_n^2}{s^2 + 2\zeta\omega_n s + \omega_n^2}
\]

Controllable canonical state-space (what `second_order_plant` builds):

\[
A = \begin{bmatrix} 0 & 1 \\ -\omega_n^2 & -2\zeta\omega_n \end{bmatrix},\quad
B = \begin{bmatrix} 0 \\ 1 \end{bmatrix},\quad
C = \begin{bmatrix} K\omega_n^2 & 0 \end{bmatrix},\quad
D = 0
\]

| Symbol | Meaning | Knob in code |
|--------|---------|--------------|
| \(\omega_n\) | Natural frequency (rad/time) | `--wn` / `wn=` |
| \(\zeta\) | Damping ratio | `--zeta` / `zeta=` |
| \(K\) | DC gain | `--gain` / `gain=` |

**Interview recall:**

- \(\zeta < 1\): underdamped → oscillatory; % overshoot \(\approx 100\,e^{-\zeta\pi/\sqrt{1-\zeta^2}}\)
- \(\zeta = 1\): critically damped
- \(\zeta > 1\): overdamped → sluggish, little/no overshoot
- Larger \(\omega_n\): faster response (shorter rise/settling), all else equal

Try: `twistdiff second-order --zeta 0.2` vs `--zeta 1.2` and compare printed metrics.

### 2. Step-response metrics

`step_response_metrics(t, y, y_final=...)` implements the definitions interviewers
expect (not proprietary “fusion” metrics):

| Metric | Definition used here |
|--------|----------------------|
| Rise time | Time from 10% → 90% of the step Δ (configurable) |
| Overshoot % | \(100 \times (\mathrm{peak}-\mathrm{final}) / \|\Delta\|\) (0 if no overshoot) |
| Settling time | First time after which \(\|y-\mathrm{final}\|\) stays inside ±2% of \(\|\Delta\|\) through the end of the record |

Finite horizons can yield `settling_time=None` if the band is never held — that is
honest, not a bug. Prefer passing known `y_final` (setpoint / analytic DC gain).

### 3. PID terms on the cruise plant

Plant: \(m\dot v = u - b v\) (`CruiseControl`). Controller: `PID.update(v, dt)`.

| Term | Intuition | Code |
|------|-----------|------|
| P (`kp`) | Corrects present error | `kp * e` |
| I (`ki`) | Removes steady-state offset | accumulates `e * dt` |
| D (`kd`) | Damps rapid error change | `(e - e_prev) / dt` |
| Limits | Actuator saturation | `output_limits` |
| Anti-windup | Freeze integral when saturated | conditional integration in `PID.update` |

Cruise CLI now prints the same metrics helper so you can talk about tuning
(faster rise vs overshoot vs actuator effort) with numbers, not vibes.

### 4. Integrators

- **Euler**: cheap, first-order; educational baseline.
- **RK4**: fourth-order; default for demos (`method="rk4"`).

Both are **fixed-step** — fine for demos; production solvers often use adaptive
step / stiff methods (not claimed here).


### 5. Damping sweep (root-locus-free)

Classical courses often jump to **root locus** (pole paths as a gain varies).
This repo deliberately does **not** draw root loci. Instead, `damping_sweep`
fixes ωn and steps ζ through underdamped → critically → overdamped, reporting
the same time-domain metrics as §2.

| What you see | What it is **not** |
|--------------|--------------------|
| Overshoot % falling as ζ ↑ | A root-locus gain plot |
| Settling / rise shifting with ζ | Routh–Hurwitz certificate |
| Optional PNG of metrics vs ζ | A Bode diagram |

Try: `twistdiff damping-sweep --zetas 0.2,0.5,0.7,1.0,1.5`

### 6. Sibling demo: SimReach recorded run (vision loop)

For a portfolio neighbor that closes a **vision** loop in pure Python (detector →
image-plane error → clamped twist, with lost-target e-stop) **without Gazebo /
ROS / Docker**, see SimReach’s recorded run:

- Repo: https://github.com/maxmccutcheon59/simreach
- Section: [Recorded run (pure Python demo)](https://github.com/maxmccutcheon59/simreach#recorded-run-pure-python-demo)
- Entry: `python scripts/recorded_run.py --output examples/last_run.jsonl`

That path is educational robotics (IBVS-lite), not certified robot safety —
same honest-edu posture as twistdiff.

## Reproducibility

```bash
pip install -e ".[dev]"
pytest -q
ruff check src tests
twistdiff second-order --zeta 0.3 --plot examples/second_order.png
twistdiff damping-sweep --plot examples/damping_sweep.png
twistdiff cruise --plot examples/cruise.png
```

## Honest limitations (say this in interviews)

- Not Simulink / not `python-control` / not a digital twin of a real plant.
- Not IEC 61508 / ISO 26262 / DO-178 certified. Do not close the loop on
  safety-critical hardware without independent engineering review.
- Metrics assume a clean SISO step-like transient; noise, MIMO, and nonlinear
  constraints are out of scope in v0.2.x. No Bode / root-locus claims.
- No GPU, no network service, no telemetry, no PII collection.

## Author

Max McCutcheon (`@maxmccutcheon59`) — `MaxMcCutcheon1@outlook.com`
