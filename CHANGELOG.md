# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-09-21

### Added

- Continuous LTI **state-space** plant (`StateSpace`) and classic **second-order**
  factory `second_order_plant(wn, zeta, gain=...)` in controllable canonical form.
- CLI demo: `twistdiff second-order` (step response + printed metrics, optional plot).
- **Step-response metrics**: rise time (10–90%), overshoot %, settling time (2% band)
  via `step_response_metrics` / `StepResponseMetrics` (`twistdiff.metrics`).
- Cruise CLI now reports the same metrics against the setpoint.
- `WRITEUP.md` — control intuition mapped to code (interview-oriented, honest edu/pro).
- Expanded pytest coverage (metrics, state-space, PID I/D, ODE harmonic period, CLI).

### Notes

- Still CPU-only (`numpy` required; `matplotlib` optional).
- Educational / research numerical tooling — not certified control or safety software.

## [0.1.0] - 2026-09-21

### Added

- Fixed-step ODE integrators: Euler and RK4 (`twistdiff.integrate`).
- Discrete PID with output limits and simple anti-windup (`twistdiff.PID`).
- Demo plants: damped harmonic oscillator and 1-D cruise control.
- CLI: `twistdiff oscillator` and `twistdiff cruise` (optional matplotlib plots).
- pytest suite, MIT license, `SECURITY.md`, `COMPLIANCE_NOTES.md`.
- CI templates under `ci/` (copy to `.github/workflows/` when `workflow` scope is available).

### Notes

- CPU-only; no GPU / CUDA dependencies.
- Intended for education and research demos — not certified control or safety software.
