# Contributing to RenodeResilience

> **License:** MIT | **Python:** 3.11+ | **Renode:** 1.15+ | **Style:** ruff + mypy

## Setup

```bash
git clone https://github.com/user/renode-resilience.git
cd renode-resilience
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt -r requirements-dev.txt
pre-commit install
renode --version  # 1.15+
python -m src.main --help
```

See `docs/02-INSTALL.md`.

## Branch Workflow

- `main` protected; PRs required.
- Branch `feat/<scope>` or `fix/<issue>` from `main`.
- Commit prefix: `feat:`, `fix:`, `docs:`, `test:`.

## Code Standards

- `src/core/` headless logic; `src/gui/` PyQt6 only; `src/config/` Pydantic schemas (`docs/01-ARCHITECTURE.md`).
- File refs: `file_path:line_number` in comments where useful.
- Before push:
```bash
ruff check src/ --fix
mypy src/
pytest tests/unit --cov=src --cov-fail-under=90
xvfb-run pytest tests/gui -q  # if GUI changes
```

## Docs

- Edit `docs/*.md` per `docs/00-INDEX.md` TOC; keep PRD `README.md` slim.
- New fault → update `docs/06-FAULT_CATALOG.md` + `src/core/fault_injector.py` + `tests/unit/test_fault_injector.py`.
- ADR for decisions → `docs/adr/00X-*.md`.

## PR Checklist

- [ ] Tests added, 90% coverage (`docs/17-TESTING.md`)
- [ ] `campaign.yaml` validates (`python -m src.config.validator`)
- [ ] Console color codes PASS `#4CAF50` etc. preserved (`docs/15-STYLE_GUIDE.md`)
- [ ] No secrets in YAML (see `docs/16-SECURITY.md`)

## Community

See `CODE_OF_CONDUCT.md`; report via issue tracker.
