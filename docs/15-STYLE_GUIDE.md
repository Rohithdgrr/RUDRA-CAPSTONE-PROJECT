# 15 — Style Guide (QSS & UX)

> **Files:** `src/gui/styles/dark_theme.qss`, `light_theme.qss`, `resources/icons/*` | `src/gui/utils/qt_helpers.py`

## 1. Theme Philosophy

- Dark-first: reduces eye strain for long campaigns (`README.md:312`).
- Embedded-native: sidebar nav, dockable panels, monospace console (`Fira Code`/`Consolas`).
- Information dense but uncluttered; 60fps PyQtGraph.

## 2. Color Palette

| Token | Hex | Usage | Example |
|-------|-----|-------|---------|
| PASS/Safe | `#4CAF50` | Table PASS, status safe | `15-STYLE_GUIDE.md:4` |
| FAIL/Unsafe | `#F44336` | FAIL, unsafe | — |
| WARNING/Partial | `#FF9800` | Warning | — |
| INFO | `#2196F3` | Log INFO | — |
| Grade A | `#2ECC71` | Emerald 90-100 | Gauge |
| Grade B | `#3498DB` | Blue 70-89 | Gauge |
| Grade C | `#F1C40F` | Yellow 50-69 | Gauge |
| Grade D | `#E67E22` | Orange 30-49 | Gauge |
| Grade F | `#E74C3C` | Red <30 | Gauge |
| Background | `#1E1E2F` | Main dark | `dark_theme.qss` |
| Surface | `#2A2A3C` | Cards/docks | — |
| Text primary | `#E0E0E0` | Labels | — |
| Text muted | `#9AA0A6` | Hints | — |

Grade colors also map to `08-RESILIENCE_INDEX.md`.

## 3. QSS Structure

`dark_theme.qss` sections:
```qss
QMainWindow { background: #1E1E2F; }
QDockWidget::title { background: #2A2A3C; color: #E0E0E0; padding: 6px; }
QTableView { gridline-color: #3A3A4C; selection-background: #3498DB; }
QTextEdit#Console { font-family: "Consolas"; font-size: 9pt; color: #E0E0E0; }
QProgressBar::chunk { background: #4CAF50; }
QPushButton { background: #3498DB; border-radius: 4px; padding: 6px 12px; }
QPushButton:hover { background: #5DADE2; }
```

Light theme inverts bg/text but keeps grade/status hues.

Apply: `app.setStyleSheet(open("src/gui/styles/dark_theme.qss").read())` in `src/app.py`.

## 4. Icons

`resources/icons/` SVG source + PNG exports 16/32/48/128/256. Naming: `app_icon.svg`, `fault_sensor.svg`, `run.svg`, `stop.svg`. Use `QIcon(":/icons/run.svg")` via Qt resource `*.qrc`.

## 5. Typography

- UI: `Segoe UI` (Win), `San Francisco` (macOS), `Noto Sans` (Linux) — 10pt.
- Console/logs: `Consolas`/`Fira Code` 9pt monospace.
- Headings: Bold 12-14pt; code: inline `QLabel` with `background #2A2A3C`.

## 6. Components

- Sidebar `QTreeView` indentation 16px, expand/collapse arrows themed.
- Tables `QTableView + PandasModel` alternating row `#252538`/`#2A2A3C`.
- Charts PyQtGraph axis color `#9AA0A6`, grid `#3A3A4C`.
- Gauges circular progress with grade color fill.

## 7. Interaction

- Hover brighten +10%, pressed darken -10%.
- Tooltips: `QToolTip { background: #3A3A4C; color: #E0E0E0; border: 1px solid #4A4A5C; }`.
- Shortcuts displayed in `QMenu` with `Ctrl+` hints.

## 8. Accessibility

- Contrast ratio ≥4.5:1 for text.
- Status not color-only: icons + words PASS/FAIL.
- Scalable SVG icons.

## 9. Adding Styles

Edit `dark_theme.qss` → restart `python -m src.main`; no rebuild. For new widget, add class selector and test both themes.
