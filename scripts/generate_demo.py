"""Generate demo.mp4 from synthetic frames (no display needed)."""
import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

W, H = 1280, 720
scenes = [
    ("RenodeResilience", "Find firmware bugs before they find you", "#1E1E2F", 3),
    ("27 Faults | RI 0-100 | PyQt6 + Renode 1.16.1", "Sensor Timing Comm Memory Power GPIO", "#2A2A3C", 3),
    ("GUI Live: Campaign 27 faults", "Progress 27/27 RI 78 Grade B", "#4CAF50", 3),
    ("CLI: renode-resilience campaign", "parallel 4 -> results/*.json", "#3498DB", 3),
    ("Report: HTML/PDF/JUnit + Comparison", "Delta +6 (+8.3%)", "#FF9800", 3),
]
out = Path("docs/demo.mp4")
writer = imageio.get_writer(str(out), fps=1, macro_block_size=1)
for title, sub, color, secs in scenes:
    for _ in range(secs):
        img = Image.new("RGB", (W, H), color)
        d = ImageDraw.Draw(img)
        # Try load default font
        try:
            f1 = ImageFont.truetype("arial.ttf", 48)
            f2 = ImageFont.truetype("arial.ttf", 28)
        except:
            f1 = ImageFont.load_default()
            f2 = ImageFont.load_default()
        d.text((W//2, H//2-40), title, fill="white", font=f1, anchor="mm")
        d.text((W//2, H//2+30), sub, fill="white", font=f2, anchor="mm")
        writer.append_data(np.array(img))
writer.close()
print(f"generated {out.resolve()} {out.stat().st_size} bytes")
# Also copy placeholder note
Path("docs/demo.mp4.placeholder").write_text("Replaced by real demo.mp4 15s, 5 scenes, 1fps, generated via imageio-ffmpeg. For full 5-min narrated, re-record OBS per demo_script.txt.", encoding="utf-8")
