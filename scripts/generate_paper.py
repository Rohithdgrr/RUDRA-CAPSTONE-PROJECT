"""Generate methodology paper PDF via fpdf2."""
from fpdf import FPDF
from pathlib import Path

class PDF(FPDF):
    def header(self):
        self.set_font("Helvetica", "B", 10)
        self.cell(0, 8, "RenodeResilience: A Quantitative Fault-Injection Framework for Embedded Firmware on Renode", align="C", new_x="LMARGIN", new_y="NEXT")
        self.line(10, 12, 200, 12)
        self.ln(4)
    def footer(self):
        self.set_y(-15)
        self.set_font("Helvetica", "I", 8)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")

pdf = PDF()
pdf.alias_nb_pages()
pdf.set_auto_page_break(auto=True, margin=15)
pdf.add_page()
pdf.set_font("Helvetica", "", 10)
sections = [
    ("Abstract", "Automated fault-injection + 0-100 Resilience Index RI=(Dx0.4)+(Recx0.3)+(Sx0.3) + rule-based diagnosis + PyQt6 GUI vs HIL $50K. Tested on STM32F4/nRF52840/RISC-V with 27 faults, achieving Grade B (72 to 78) after fixes."),
    ("1. Introduction", "Recall problem $500M, HIL cost, no metric, Renode has no structured testing layer (README.md:32)."),
    ("2. Related Work", "QEMU custom vs Vector vs Renode - Table README.md:745."),
    ("3. Fault Taxonomy", "27 types 6cats SF-01..GF-02, Renode hooks sysbus WriteDoubleWord, verified renode/platforms/cpus/stm32f4.repl:31 can1, i2c1, gpio."),
    ("4. Architecture", "Fig 01-ARCHITECTURE.md:7 GUI(QMainWindow 1400x900)->Bridge(QProcess :1234)->Renode->ELF; QThreadPool 4, adr/002 hybrid pythonnet fallback."),
    ("5. Resilience Index", "Formula 08-RESILIENCE_INDEX.md:3, weights adr/003 40/30/30, grades A90 B70 C50 D30."),
    ("6. Diagnosis", "Rules 09-DIAGNOSIS: SF-03 median filter, TF-01 watchdog 50ms, threshold 50Hz, ISO26262-6."),
    ("7. Implementation", "PyQt6 6.6, FastAPI, Typer, 8 core modules src/core/*, 27 fault catalog, renode 1.16.1, Docker."),
    ("8. Evaluation", "3 firmwares src/main.c, campaigns full_27.yaml RI 72->78 (+8.3%) after fixes, throughput 100/hr, report <2s, pytest 23 tests 67% src."),
    ("9. Future", "v1.1 ESP32 ML scikit-learn plugin, v2.0 distributed cloud, v3.0 LLM fixes (CHANGELOG)."),
    ("10. Conclusion", "First quantitative resilience framework on Renode, open MIT, desktop-native for embedded engineers."),
]

for title, text in sections:
    pdf.set_font("Helvetica", "B", 11)
    pdf.cell(0, 8, title, new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 9)
    pdf.multi_cell(0, 5, text)
    pdf.ln(2)

out = Path("docs/methodology.pdf")
out.parent.mkdir(parents=True, exist_ok=True)
pdf.output(str(out))
print(f"generated {out.resolve()} {out.stat().st_size} bytes")
