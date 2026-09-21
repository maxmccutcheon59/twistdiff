# WRITEUP — twistdiff (v0.2.0)

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

## Reproducibility

```bash
pip install -e ".[dev]"
pytest -q
ruff check src tests
twistdiff second-order --zeta 0.3 --plot examples/second_order.png
twistdiff cruise --plot examples/cruise.png
```

## Honest limitations (say this in interviews)

- Not Simulink / not `python-control` / not a digital twin of a real plant.
- Not IEC 61508 / ISO 26262 / DO-178 certified. Do not close the loop on
  safety-critical hardware without independent engineering review.
- Metrics assume a clean SISO step-like transient; noise, MIMO, and nonlinear
  constraints are out of scope in v0.2.0.
- No GPU, no network service, no telemetry, no PII collection.

## Author

Max McCutcheon (`@maxmccutcheon59`) — `MaxMcCutcheon1@outlook.com`
