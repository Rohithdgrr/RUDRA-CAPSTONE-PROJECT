# 15 — Style Guide (QSS & UX)

> **Files:** `src/gui/styles/dark_theme.qss`, `light_theme.qss`, `src/gui/utils/icons.py`

## 1. Theme Philosophy

- Dark-first: reduces eye strain for long campaigns.
- Light theme available via View → Theme menu.
- Embedded-native: sidebar nav, dockable panels, monospace console.
- Information dense but uncluttered.

## 2. Color Palette

### Dark Theme

| Token | Hex | Usage |
|-------|-----|-------|
| Background | `#0F0F1A` | Main window background |
| Surface | `#16162A` | Cards, panels |
| Surface Hover | `#1E1E35` | Hover states |
| Border | `#27273A` | Dividers, frames |
| Text Primary | `#D4D4D8` | Labels, body |
| Text Muted | `#71717A` | Hints, secondary |
| Text Bright | `#F4F4F5` | Headings |
| Brand | `#3B82F6` | Links, active, accent |
| PASS | `#10B981` | Success, safe |
| FAIL | `#EF4444` | Error, unsafe |
| WARNING | `#F59E0B` | Partial, warning |
| INFO | `#3B82F6` | Info messages |
| Grade A | `#10B981` | 90-100 |
| Grade B | `#3B82F6` | 70-89 |
| Grade C | `#F59E0B` | 50-69 |
| Grade D | `#F97316` | 30-49 |
| Grade F | `#EF4444` | <30 |

### Light Theme

| Token | Hex | Usage |
|-------|-----|-------|
| Background | `#F8FAFC` | Main window |
| Surface | `#FFFFFF` | Cards, panels |
| Border | `#E5E7EB` | Dividers |
| Text Primary | `#1F2937` | Labels |
| Text Muted | `#9CA3AF` | Hints |
| Brand | `#3B82F6` | Same accent |

## 3. QSS Structure

`dark_theme.qss` — 200+ rules covering:
- `QMainWindow`, `QWidget`, `QMenuBar`, `QMenu`
- `QDockWidget` (section headers)
- `QTreeWidget` (sidebar items with hover/active)
- `QTableWidget` (alternating rows, colored selection)
- `QPushButton` (primary, stop, save, export variants)
- `QProgressBar` (gradient chunk blue→purple)
- `QLineEdit`, `QSpinBox`, `QComboBox` (focus border)
- `QTextEdit` (console with monospace font)
- `QScrollBar` (thin 8px, rounded handle)
- `QTabWidget`, `QSplitter`, `QGroupBox`, `QDialog`
- `QCheckBox`, `QToolTip`
- Custom selectors: `#card`, `#summaryCard`, `#sectionLabel`, `#titleLabel`

Apply: `app.setStyleSheet(qss.read_text())` in `src/app.py`.

## 4. Vector Icons

20 icons via `src/gui/utils/icons.py` — programmatic `QPainter` on `QPixmap`:

```python
from src.gui.utils.icons import AppIcons
icon = AppIcons.play("#A1A1AA")  # returns QIcon
```

- No external SVG/PNG assets required
- Antialiased rendering at any size
- Color parameter for dark/light theme adaptation
- Used in: sidebar, menu bar, buttons, cards

## 5. Typography

- UI: `Segoe UI` (Win), `SF Pro` (macOS), `Noto Sans` (Linux) — 13px
- Console/logs: `Cascadia Code`, `JetBrains Mono`, `Consolas` — 12px monospace
- Headings: Bold 22-36px
- Section labels: 11px uppercase, bold, letter-spacing 1px

## 6. Components

- **Sidebar:** Fixed 220px, sections with headers, vector icons on every item
- **Summary Cards:** `QFrame#summaryCard` with stat value + label
- **Tables:** Alternating rows, colored status cells, bold RI values
- **Charts:** Custom `paintEvent` donut arcs and bars
- **Console:** Timestamped, color-coded per level, auto-scroll

## 7. Interaction

- Hover brighten, pressed darken
- Active sidebar item highlighted with blue background
- Tooltips on all actionable elements
- Keyboard: standard Qt shortcuts

## 8. Accessibility

- Contrast ratio ≥4.5:1 for text
- Status not color-only: icons + words PASS/FAIL
- Vector icons scale cleanly
