# twistdiff

Lightweight **ODE integration** + **PID control** demos in pure Python (CPU-only).

Educational / research portfolio library — not industrial control software.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## Features

- Fixed-step **Euler** and **RK4** integrators (`twistdiff.integrate`)
- Discrete **PID** with output limits and simple anti-windup (`twistdiff.PID`)
- Demo plants: **damped harmonic oscillator**, **1-D cruise control**
- CLI entry point: `twistdiff`
- Optional **matplotlib** plots (`pip install 'twistdiff[plot]'`)
- **No GPU** dependencies

## Install

```bash
pip install -e ".[dev]"          # numpy + pytest + ruff + matplotlib
# or minimal:
pip install -e .
pip install -e ".[plot]"         # add matplotlib
```

Requires Python **3.10+**.

## Quick start (library)

```python
from twistdiff import DampedHarmonicOscillator, integrate

plant = DampedHarmonicOscillator(mass=1.0, damping=0.2, stiffness=4.0)
traj = integrate(plant.rhs(), y0=[1.0, 0.0], t_span=(0.0, 20.0), dt=0.01)
print(traj.t[-1], traj.y[-1])
```

```python
from twistdiff import CruiseControl, PID

plant = CruiseControl(mass=1000.0, drag=50.0)
pid = PID(kp=800, ki=40, kd=50, setpoint=25.0, output_limits=(0.0, 5000.0))
v, dt = 0.0, 0.05
for _ in range(800):
    u = pid.update(v, dt)
    v = v + dt * plant.accel(v, u)
print(v)  # ~ setpoint
```

## CLI

```bash
twistdiff oscillator --plot examples/oscillator.png
twistdiff cruise --plot examples/cruise.png
twistdiff --version
```

## Example plots

Regenerate with the commands above (also produced by `examples/generate_plots.py`).

### Damped harmonic oscillator

![Oscillator](examples/oscillator.png)

### 1-D cruise control (PID)

![Cruise](examples/cruise.png)

## API surface

| Symbol | Module | Role |
|--------|--------|------|
| `integrate` | `twistdiff.ode` | Fixed-step ODE solver → `Trajectory` |
| `Trajectory` | `twistdiff.ode` | `t`, `y` arrays |
| `PID` | `twistdiff.pid` | Discrete PID controller |
| `DampedHarmonicOscillator` | `twistdiff.models` | `m x'' + c x' + k x = u(t)` |
| `CruiseControl` | `twistdiff.models` | `m v' = u - b v` |
| `save_trajectory_plot` | `twistdiff.plotting` | Optional matplotlib helper |

## Tests

```bash
pytest -q
ruff check src tests
```

## Project layout

```
src/twistdiff/   # library + CLI
tests/           # pytest
examples/        # PNG demos + plot generator
ci/              # GitHub Actions templates (see note below)
SECURITY.md
COMPLIANCE_NOTES.md
```

## CI note

Workflow YAML lives under `ci/` because some push credentials lack the GitHub OAuth `workflow` scope. Copy to `.github/workflows/` when that scope is available:

```bash
mkdir -p .github/workflows
cp ci/ci.yml ci/security-ci.yml .github/workflows/
```

## Security & compliance

- Vulnerability reports: see [`SECURITY.md`](SECURITY.md)
- Research/edu posture, no PII: see [`COMPLIANCE_NOTES.md`](COMPLIANCE_NOTES.md)

## License

MIT © 2026 Max McCutcheon (`MaxMcCutcheon1@outlook.com`)
