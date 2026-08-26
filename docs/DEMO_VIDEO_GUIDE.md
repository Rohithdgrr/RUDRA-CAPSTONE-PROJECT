# Demo Video Guide — 5-Minute Capstone Walkthrough

> **Target:** 5 min MP4 / YouTube, 1080p, narration, showcases Desktop + CLI + API.

## Script (300s)

| Time | Scene | Action | File |
|------|-------|--------|------|
| 0:00-0:20 | Title card | "RenodeResilience — Find firmware bugs before they find you" + 27 faults + RI | `resources/icons/app_icon.svg` |
| 0:20-1:00 | Problem | HIL $50K vs free emulation, no metric → RI 0-100 | `README.md:22` |
| 1:00-2:00 | Architecture | Diagram `docs/01-ARCHITECTURE.md:7` GUI → Bridge → Renode → ELF | `src/main_window.py:73` 1400×900 |
| 2:00-3:00 | Live Demo — GUI | `python -m src.main` → Welcome → Campaign Designer (3 faults) → Run → progress 3/3 → Report RI 43 Grade D | `campaigns/sensor_suite.yaml` |
| 3:00-3:40 | CLI | `renode-resilience campaign --config campaigns/sensor_suite.yaml --parallel 4` + `report --format html` | `src/cli.py:11` |
| 3:40-4:10 | API | `uvicorn src.api.app:app` → Swagger `/docs` → `POST /api/v1/run` → WebSocket `/live` | `src/api/app.py:60` |
| 4:10-4:40 | Results | HTML report `results/preview_report.html` + `comparison.html` delta + Diagnosis `median filter` | `src/core/report_generator.py:14` |
| 4:40-5:00 | Wrap | Future v1.1 ESP32 + ML + VSCode, MIT, GitHub, Q&A | `CHANGELOG.md:21` |

## Capture

- Windows: OBS Studio, 1400×900 window, 60fps.
- Headless auto: `python preview.py` (needs display, not offscreen — offscreen squares are headless-only, native is clean) → `preview*.png` → stitch with `ffmpeg -framerate 2 -i preview_%d.png demo.mp4`.
- Narration script in this file; export with `pyinstaller` demo `scripts/build.py`.

## Checklist

- [ ] Firmware ELF builds: `make -C examples/sensor-firmware`
- [ ] Renode 1.16.1 on PATH: `renode --version`
- [ ] Run campaign achieves Grade B on fixed firmware (after adding median filter).

See also `docs/03-QUICKSTART.md` 10-min version.
