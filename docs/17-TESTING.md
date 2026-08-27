# 17 — Testing

> **Target:** 90%+ coverage | `tests/unit/`, `tests/integration/`, `tests/gui/` | `README.md:782`

## 1. Stack

| Layer | Tool | Purpose |
|-------|------|---------|
| Unit | `pytest` + `pytest-qt` + `pytest-cov` | `src/core/*` logic without Renode |
| Integration | `Robot Framework` + `renode-test` (`renode-test-action/action.yml:36`, `renode/README.md:126`) | Full `RenodeBridge` + campaign run (requires Renode `1.16.1`) + `renode/tests/requirements.txt` |
| GUI | `pytest-qt` + `qtbot` | `src/gui/widgets/*` without display (`xvfb`) |
| Lint | `ruff`, `mypy` | `pyproject.toml` strict |

## 2. Unit Tests (`tests/unit/`) — 27 tests

| File | Tests | Covers |
|------|-------|--------|
| `test_api.py` | 4 | FastAPI endpoints, faults list (27), run single, campaign flow |
| `test_campaign.py` | 2 | YAML loading, campaign execution |
| `test_cli.py` | 4 | CLI commands, YAML validator |
| `test_diagnosis.py` | 3 | Diagnosis rules, SF-01 median filter, TF-01 watchdog |
| `test_fault_injector.py` | 4 | 27 fault IDs, build commands, bridge injection |
| `test_renode_bridge.py` | 7 | Start, stop, inject, read, command building |
| `test_report.py` | 2 | HTML generation, JUnit XML, comparison |
| `test_resilience.py` | 1 | RI calculation, grade mapping |

Run:
```bash
pytest tests/unit -v --tb=short
# 27 passed in ~1s
```

Run:
```bash
pytest tests/unit --cov=src --cov-report=html -q
# target 90%
```

## 3. Integration Tests (`tests/integration/`)

Requires Renode installed; marked `pytest.mark.integration`:
```bash
pytest tests/integration -m integration --run-renode
```

Robot example (`tests/integration/campaign.robot`) — pattern from `renode/tests/peripherals` + `renode-test-action/__tests__/hello_world.robot:236`:
```robot
*** Test Cases ***
Sensor Campaign
    Run Campaign    campaigns/sensor_suite.yaml    parallel=2
    Result Should Be    RI >= 70
```

Uses real `RenodeBridge` + `examples/sensor-firmware/build/sensor.elf`. Reference: `renode-test-action/action.yml:20` `antmicro/renode-test-action@v5` with `renode-revision: 'master'` + `tests-to-run: 'tests/**/*.robot'`; local `renode-test -r $ARTIFACTS_PATH` (`src/run_renode_test.sh:36`) + `results.py:84` markdown summary.

## 4. GUI Tests (`tests/gui/`)

```python
def test_campaign_editor(qtbot):
    from src.gui.widgets.campaign_editor import CampaignEditor
    w = CampaignEditor(); qtbot.addWidget(w)
    w.name_edit.setText("Test")
    assert w.is_valid() is False  # no firmware
```

Headless CI: `xvfb-run pytest tests/gui`.

## 5. Coverage

```bash
pytest --cov=src --cov-fail-under=90
coverage html  # opens htmlcov/index.html
```

CI enforces in `.github/workflows/ci.yml` (`README.md:776`).

## 6. Test Data

- ELFs: `examples/*/build/*.elf` prebuilt; rebuild needs `arm-none-eabi-gcc`.
- Campaigns: `tests/fixtures/*.yaml` minimal 1-fault YAMLs.
- Mock peripheral reads: `tests/mocks/renode_responses.json`.

## 7. Adding Tests

- New fault in `06-FAULT_CATALOG.md` → add case in `test_fault_injector.py` + diagnosis rule.
- New widget → `tests/gui/test_<widget>.py` with `qtbot`.
- Run `ruff check` and `mypy src/` before push (pre-commit hook).

## 8. CI/CD — Vendored Actions

- **renode-test-action** (`renode-test-action/action.yml:1` `Run tests in Renode`): composite action clones `renode` at `renode-revision`, caches `renode-{os}-{arch}-{rev}`, `build.sh --net`, `actions/cache/restore@v4/save@v4`, `setup-uv@v7`, `uv pip install -r tests/requirements.txt`, `src/run_renode_test.sh` + `src/results.py` → `GITHUB_STEP_SUMMARY`. Use: `.github/workflows/ci.yml` `uses: ./renode-test-action with: tests-to-run: 'tests/integration/**/*.robot'` + `renode-docker/Dockerfile:8` for containerized runs.

GitHub Actions: `test (matrix win/mac/linux) → cov → package (PyInstaller) → release`. See `19-PACKAGING.md`. JUnit export used for Jenkins (`10-REPORT_SPEC.md`).
