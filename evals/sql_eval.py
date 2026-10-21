#harness engineering.

"""Execution-accuracy eval: does the generated SQL return the same rows as the gold SQL?"""
from app.core.db import run_query
from app.tools.text_to_sql import ask_database

CASES = [
    ("How many candidates are in each status?",
     "SELECT status, COUNT(*) FROM candidates GROUP BY status"),
    ("Which backend candidates with at least 3 years of experience have not been contacted?",
     "SELECT name FROM candidates WHERE domain='backend' AND years_experience>=3 AND contacted_at IS NULL"),
    ("List candidates in the interview stage with their interviewer and interview date",
     "SELECT c.name, i.interviewer, i.scheduled_at FROM candidates c "
     "JOIN interviews i ON i.candidate_id=c.id WHERE c.status='interview'"),
    ("Which candidates know Kafka?",
     "SELECT c.name FROM candidates c JOIN skills s ON s.candidate_id=c.id WHERE s.skill='Kafka'"),
    ("How many jobs require at least 3 years of experience?",
     "SELECT COUNT(*) FROM jobs WHERE min_experience>=3"),
    ("Which candidates have received an offer?",
     "SELECT name FROM candidates WHERE status='offer'"),
]


def normalize(rows):
    return sorted((tuple(r) for r in rows), key=str)

def same_answer(gold_cols, gold_rows, gen_cols, gen_rows):
    """If the generated query contains all the gold columns, compare only those
    columns (extra columns are fine). Otherwise compare rows as they are."""
    gen_lower = [c.lower() for c in gen_cols]
    gold_lower = [c.lower() for c in gold_cols]
    if all(c in gen_lower for c in gold_lower):
        idx = [gen_lower.index(c) for c in gold_lower]
        gen_rows = [tuple(r[i] for i in idx) for r in gen_rows]
    return normalize(gen_rows) == normalize(gold_rows)

def main():
    passed = 0
    for question, gold_sql in CASES:
        gold_cols, gold_rows = run_query(gold_sql)
        out = ask_database(question)
        ok = out["error"] is None and same_answer(
            gold_cols, gold_rows, out["columns"], out["rows"]
        )
        passed += ok
        print(("PASS" if ok else "FAIL"), "-", question)
        if not ok:
            print("   generated:", out["sql"])
            print("   error    :", out["error"])
            print("   gold     :", gold_sql)
    print(f"\nScore: {passed}/{len(CASES)}")


if __name__ == "__main__":
    main()