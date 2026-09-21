# Compliance Notes — twistdiff

> Human / lawyer review recommended before any commercial, classroom-mandated, or organizational deployment.
> This file flags legal and compliance-relevant aspects; it is **not** legal advice.

## Product posture

- **Educational / research numerical library + CLI** for ODE integration, LTI state-space, step-response metrics, and simple PID demos.
- **No SaaS, accounts, telemetry, cookies, or intentional PII collection.**
- **No GPU / cloud training stack** — CPU-only `numpy` (+ optional `matplotlib`).
- Portfolio project for Max McCutcheon (`@maxmccutcheon59`).
- Interview write-up in `WRITEUP.md` (honest edu/pro; not a commercial product claim).

## Data inventory

| Data | Collected by this repo? | Storage | Shared? |
|------|-------------------------|---------|---------|
| End-user PII | **No** | — | — |
| Simulation trajectories | Operator-chosen local arrays / optional PNG | Local disk if `--plot` used | Not uploaded by this project |
| Telemetry / analytics | **None** | — | — |
| Payment data | **None** | — | — |

## Privacy / regulatory flags

| Item | Applies? | Action |
|------|----------|--------|
| Privacy Policy / ToS | No (no user-data service) | Re-review if productized as a hosted service |
| GDPR / US state privacy | No intentional PII | N/A for default local use |
| COPPA / minors | No | Do not market as a child-directed product without review |
| Payments / PCI | No | N/A |
| HIPAA / health | No | Do not use for clinical device control claims |
| Export controls / sanctions | General-purpose scientific software | Human review if shipping to restricted jurisdictions |
| Safety-critical control | **Not certified** | Escalate before any real vehicle / plant / medical use |
| IP / third-party | MIT original code; numpy/matplotlib under their licenses | Recorded in pyproject extras |

## Third-party licenses (runtime)

| Package | Role | Typical license |
|---------|------|-----------------|
| numpy | Required | BSD-3-Clause |
| matplotlib | Optional (`[plot]`) | PSF-based |

Pin and audit with `pip-audit` in CI when workflows are enabled.

## Security tooling ethics

- Authorized systems only (see `SECURITY.md`).
- No exploit payloads, malware, or unauthorized-access features.

## Items needing human review before commercial or safety-critical use

- [ ] Functional-safety / control-systems review if closed-loop on real hardware
- [ ] Privacy Policy / Terms if a hosted multi-user product is built
- [ ] Export / sanctions screening if distributing binaries internationally
- [ ] Any collection of personal or telemetry data (out of scope today; escalate)
