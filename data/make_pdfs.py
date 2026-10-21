from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas

BASE = Path(__file__).parent
OUT = BASE / "resumes_pdf"
OUT.mkdir(exist_ok=True)

for txt in sorted((BASE / "resumes").glob("candidate_*.txt")):
    pdf = canvas.Canvas(str(OUT / f"{txt.stem}.pdf"), pagesize=A4)
    _, height = A4
    y = height - 50
    for line in txt.read_text().splitlines():
        pdf.setFont("Helvetica-Bold" if line.isupper() and line else "Helvetica", 10)
        pdf.drawString(50, y, line)
        y -= 14
    pdf.save()

print(f"Wrote PDFs to {OUT}")