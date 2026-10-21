from pathlib import Path

from app.core.config import PDF_DIR
from app.core.db import run_query
from app.tools.resume_parser import parse_resume

total = ok_years = ok_skills = 0
for pdf in sorted(PDF_DIR.glob("*.pdf"))[:10]:
    cid = int(pdf.stem.split("_")[1])
    parsed = parse_resume(pdf)
    _, row = run_query(f"SELECT years_experience FROM candidates WHERE id={cid}")
    _, skill_rows = run_query(f"SELECT skill FROM skills WHERE candidate_id={cid}")
    true_skills = {r[0].lower() for r in skill_rows}

    years_match = parsed.years_experience == row[0][0]
    skills_match = {s.lower() for s in parsed.skills} == true_skills
    total += 1
    ok_years += years_match
    ok_skills += skills_match
    print(f"{pdf.stem}: years {'OK' if years_match else 'WRONG'}, skills {'OK' if skills_match else 'WRONG'}")

print(f"\nYears correct: {ok_years}/{total}   Skills correct: {ok_skills}/{total}")