# Security Policy

## Supported versions

Security fixes are applied on the latest release of **twistdiff** on `main`. Older tags are not backported unless noted in a release.

## Reporting a vulnerability

Please report security issues privately — do **not** open a public GitHub issue for undisclosed vulnerabilities.

- **Contact:** [MaxMcCutcheon1@outlook.com](mailto:MaxMcCutcheon1@outlook.com)
- Include: affected version/commit, reproduction steps, impact, and any suggested fix.
- You should receive an acknowledgment within a few business days.

We will work with you to understand and remediate the issue, then credit reporters who want acknowledgment (optional).

## Scope and intended use

twistdiff is an **educational / research** numerical toolkit (ODE integration + simple PID demos). It:

- Runs **locally** on CPU; no network services, auth, or telemetry by default.
- Does **not** claim industrial certification (ISO, IEC, automotive ASPICE, etc.).
- Must not be used as the sole controller for safety-critical hardware without independent engineering review.

## Authorized testing only

You may only run security or penetration tests against systems **you own** or for which you have **explicit written authorization**. Unauthorized testing may violate the CFAA and similar laws.

## Secrets and credentials

- Never commit secrets (`.env`, API keys, tokens, private keys).
- Use environment variables or a secrets manager for any credentials.
- If a secret is exposed: **rotate it first**, then clean history if needed.

## Preferred disclosure process

1. Email the contact above with details.
2. Allow reasonable time for a fix before public disclosure.
3. Coordinated disclosure is appreciated; please do not weaponize findings.

## Incident response (baseline)

1. Contain (revoke tokens, disable distribution if needed).
2. Rotate any exposed credentials.
3. Assess impact and notify affected parties if personal data were involved (none collected by default).
4. Patch, tag a fixed release, and document in `CHANGELOG.md`.
