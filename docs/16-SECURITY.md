# 16 — Security

> **Source:** `README.md:380-398` threat model

## 1. Threat Model

| Threat | Risk | Mitigation | Implementation |
|--------|------|------------|----------------|
| Firmware IP theft | High | Local-only, no cloud upload ever | No network egress; `RenodeBridge` local `subprocess.Popen` |
| Test data leakage | Medium | No external services, disk-only | Results in `results/*.json` local; `.gitignore campaigns/private/` |
| Malicious firmware | Medium | Sandboxed Renode, resource limits, timeout guards | ELF loaded in emulator, never native exec; `QProcess` timeout 10s `stop()` |
| Report sensitivity | Low | Optional AES-256 encryption | `report.pdf.enc` with passphrase (`10-REPORT_SPEC.md`) |
| CI/CD secret exposure | Medium | Read-only tokens, no secrets in YAML | `src/config/schemas.py` forbids `secret` keys; token via env |
| Dependency supply chain | Medium | Pinned `requirements.txt` hashes, no unvetted pkgs | `pip hash-checking` |

## 2. Local-Only Execution

- Renode runs on user machine; zero network dependency (`README.md:394`).
- API `13-API_REST.md` binds `127.0.0.1` by default; LAN expose requires `--host 0.0.0.0` explicit.
- WebSocket only on loopback.

## 3. Sandboxing

- Firmware ELF → `sysbus LoadELF` inside Renode memory model; host not executing code.
- Resource guards: CPU/memory limits on subprocess; auto-kill after `duration*1.5` timeout.
- No network access from emulator (isolated `sysbus`).

## 4. Encrypted Reports (Optional)

```bash
# GUI: Settings → Encrypt reports → passphrase
# CLI:
renode-resilience report --results results/latest.json --format pdf --encrypt --passphrase env:REPORT_PASS
```
Produces `report.pdf.enc` AES-256-GCM; decrypt `openssl enc -d -aes-256-gcm -in report.pdf.enc`.

## 5. Audit Logging

- All injections logged to `logs/audit.log` tamper-evident (append-only, SHA256 chain).
- Entries: `timestamp, run_id, fault_id, command, result`.
- Rotate via `src/config/defaults.py:log_retention_days=30`.

## 6. Tokens & Secrets

- API token (`13-API_REST.md`) read-only for CI: `Authorization: Bearer <token>`.
- Never store secrets in `campaign.yaml` — use env `RENODE_TOKEN` or `~/.config/renode-resilience/token`.
- `.gitignore` should contain `campaigns/private/`, `results/private/`.

## 7. Dependency Pinning

```
# requirements.txt with hashes (include renode-test + pyrenode3 transitive deps)
PyQt6==6.6.0 --hash=sha256:...
pythonnet>=3.0.1  # via pyrenode3/pyproject.toml:28, required for pyrenode3
```
Update via `pip-compile --generate-hashes`. Vendored `renode/tests/requirements.txt` (Robot) hashed separately for `renode-test-action`.

Docker `renode-docker/Dockerfile:15` base `mcr.microsoft.com/dotnet/runtime:8.0-noble` + `python3-pip` audited; `Dockerfile.min` uses `bookworm-slim` minimal surface.

## 8. Reporting Vulnerabilities

Contact `security@renode-resilience.local` (placeholder); see `SECURITY.md` (root) for disclosure policy.

## 9. Future

- LDAP auth, audit trails, multi-user campaigns (`README.md:776` Enterprise v3.0).
