# 10 — Report Specification

> **File:** `src/core/report_generator.py` | Templates `resources/templates/report_base.html`, `report_pdf.css` | Tools Jinja2 + WeasyPrint

## 1. Outputs

| Format | File | Audience | Generator |
|--------|------|----------|-----------|
| HTML | `report.html` | Interactive, shareable | `results.to_html(path)` → Jinja2 `report_base.html` |
| PDF | `report.pdf` | Audit-ready, printable | `results.to_pdf(path)` → WeasyPrint + `report_pdf.css` |
| JSON | `report.json` | CI/CD integration | `results.to_json(path)` → `pandas` |
| JUnit XML | `junit.xml` | Jenkins/GitLab | `results.to_junit(path)` → `junit` schema |

All via `results.to_*` (SDK) or `renode-resilience report --format` (CLI) or GUI Report Viewer export buttons.

## 2. Structure (HTML/PDF)

- **Summary Card:** Campaign name, Overall RI `69/100 Grade C Marginal`, Pass `15` Fail `8` Warning `4` Total `27`.
- **Critical Findings:** List with severity icons ⚠/❌, `root_cause` + `Recommendation` from `09-DIAGNOSIS_ENGINE.md`. Example: `1. Impulse noise not detected (SF-03) → Add median filter (3-sample)`.
- **Detailed Charts:** Radar 6 categories, Heatmap fault×RI, Timeline latency, Pie Pass/Fail/Warning, Line RI over time — `src/gui/widgets/charts/*`.
- **Evidence Table:** Per-fault `ID | Type | Status | Detect | Recover | Safety | RI` + logs excerpt `RenodeBridge.log_file` last 100 lines.
- **Comparison delta** if baseline provided (→ `ComparisonView`).

## 3. JSON Schema

```json
{
  "campaign": "Sensor Suite Validation",
  "timestamp": "2026-08-26T12:00:00Z",
  "resilience_index": 73,
  "grade": "B",
  "pass_count": 19, "fail_count": 8, "total": 27,
  "weights": {"detection":0.4,"recovery":0.3,"safety":0.3},
  "results": [
    {"fault_id":"SF-01","status":"PASS","latency_ms":23,"recovery_ms":45,"safe":true,"ri":100},
    {"fault_id":"SF-03","status":"FAIL","latency_ms":null,"ri":40,"diagnosis":{"root_cause":"Impulse noise not detected","recommendations":["Add median filter"]}}
  ]
}
```

## 4. JUnit XML

Maps each fault to `<testcase classname="Sensor" name="SF-01 Stuck-at" time="0.023"><passed/></testcase>` or `<failure message="SF-03"/>`. Compatible with Jenkins/GitLab. Generated via `pandas` + `xml.etree`.

## 5. Template System

- Jinja2 env with `bytecode_cache` (perf <5s per `README.md:407`).
- `resources/templates/report_base.html` base + `iso26262_checklist.html` optional annex.
- CSS: `report_pdf.css` for print margins, grade colors (`15-STYLE_GUIDE.md`).

## 6. Performance

- Async WeasyPrint rendering (non-blocking GUI).
- Streaming logs (no full load), Pandas chunking for large campaigns (`README.md:418`).

## 7. CLI/API

```bash
renode-resilience report --results results/campaign_2026-08-26.json --format pdf --output report.pdf
# API
GET /api/v1/report/{run_id}?format=html|pdf|json  # returns file download
```

## 8. Encryption (Optional)

Per `README.md:398`: `report.pdf.enc` AES-256 with passphrase via Settings dialog.

## 9. Trend Analysis

Not in v1.0 — planned: `results.compare()` across runs; see `04-USER_GUIDE.md` Step 7 for manual comparison now.

