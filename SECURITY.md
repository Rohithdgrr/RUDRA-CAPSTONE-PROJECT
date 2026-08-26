# Security Policy

> **See also:** `docs/16-SECURITY.md` threat model & mitigations

## Supported Versions

| Version | Supported |
|---------|-----------|
| 1.0.x   | ✅ |
| <1.0    | ❌ |

## Reporting Vulnerabilities

- Do NOT open public issue for sensitive vulns.
- Email `security@renode-resilience.local` (placeholder; replace with real) with details, PoC, impact.
- Expect ack in 48h, fix timeline per severity.

## Guarantees

- Local-only execution: no firmware/cloud upload (`docs/16-SECURITY.md`).
- Sandboxed Renode ELF; resource guards; no network from emulator.
- Optional AES-256 report encryption `report.pdf.enc`.
- Audit log `logs/audit.log` SHA256-chained.

## Dependency Security

- Pinned `requirements.txt` with hashes; update via `pip-compile --generate-hashes`.
- No secrets in `campaign.yaml`; tokens via env `RENODE_TOKEN`.

## Disclosure

Coordinated disclosure; credit reporter if desired.
