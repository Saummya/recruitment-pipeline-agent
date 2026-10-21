"""Text-to-SQL and SQL-to-Text for the recruitment database."""
import re
import sys

from app.core.db import get_schema, run_query
from app.core.llm import get_llm

ALLOWED_TABLES = {"candidates", "skills", "jobs", "applications", "interviews"}
FORBIDDEN = re.compile(
    r"\b(insert|update|delete|drop|alter|create|replace|attach|detach|pragma|vacuum)\b",
    re.I,
)

SQL_PROMPT = """You are an expert SQLite data analyst for a recruitment team.
Write ONE SQLite SELECT query that answers the question.

Database schema:
{schema}

Facts about the data:
- candidates.status is one of: new, screening, interview, offer, rejected
- candidates.domain is one of: backend, frontend, data, devops
- candidates.contacted_at is NULL when the candidate has not been contacted yet
- Dates are ISO text like 2026-10-25
- Each candidate has many rows in skills; skills.skill holds one skill name per row

Schema notes:
- The interviews table has NO stage column. A candidate's pipeline stage is candidates.status.
- "N years of experience" means candidates.years_experience >= N. It has nothing to do with how many skills someone has.
- jobs.min_experience is the number of years a job requires.

Style rules:
- Select only the columns the question asks for. For "which/who/list candidates" return just candidates.name, plus extra columns only if the question asks for them (for example interviewer or date).
- Do not use GROUP BY or HAVING unless the question asks for counts, or for candidates who have ALL of several skills.
- Return ONLY the SQL. No explanation, no markdown fences.
- Use only the tables and columns shown above. Never modify data.

Examples:
Question: Which frontend candidates have been contacted?
SQL: SELECT name FROM candidates WHERE domain = 'frontend' AND contacted_at IS NOT NULL

Question: Who knows both Docker and Kubernetes?
SQL: SELECT c.name FROM candidates c JOIN skills s ON s.candidate_id = c.id WHERE s.skill IN ('Docker', 'Kubernetes') GROUP BY c.id, c.name HAVING COUNT(DISTINCT s.skill) = 2

Question: Show the interviewer and date for candidates who got an offer
SQL: SELECT c.name, i.interviewer, i.scheduled_at FROM candidates c JOIN interviews i ON i.candidate_id = c.id WHERE c.status = 'offer'

Question: {question}
SQL:"""

REPAIR_PROMPT = """This SQLite query failed. Fix it and return ONLY the corrected SQL.

Database schema:
{schema}

Question: {question}
Failed SQL: {sql}
Error: {error}
Corrected SQL:"""

ANSWER_PROMPT = """You are a recruiting assistant. Answer the question using ONLY the
query result below. Be concise. If there are no rows, say no matching records were found.
Do not invent anything that is not in the result.

Question: {question}
SQL used: {sql}
Total rows: {total} (showing up to 20)
Result:
{result}

Answer:"""


def clean_sql(text: str) -> str:
    """Strip markdown fences and trailing semicolons the model may add."""
    text = re.sub(r"^```(?:sql)?|```$", "", text.strip(), flags=re.I | re.M).strip()
    return text.rstrip(";").strip()


def validate_sql(sql: str) -> str:
    """Guardrails. Raises ValueError if the query is unsafe."""
    lowered = sql.lower()
    if not lowered.startswith("select"):
        raise ValueError("Only SELECT queries are allowed.")
    if ";" in sql:
        raise ValueError("Only one statement is allowed.")
    if FORBIDDEN.search(sql):
        raise ValueError("Query contains a forbidden keyword.")
    used = set(re.findall(r"\b(?:from|join)\s+([a-z_]+)", lowered))
    unknown = used - ALLOWED_TABLES
    if unknown:
        raise ValueError(f"Unknown tables: {unknown}")
    if not re.search(r"\blimit\b", lowered):
        sql += " LIMIT 50"  # never return huge result sets
    return sql


def sql_to_text(question, sql, columns, rows, llm=None) -> str:
    llm = llm or get_llm()
    result = "\n".join(str(dict(zip(columns, r))) for r in rows[:20]) or "(no rows)"
    prompt = ANSWER_PROMPT.format(
        question=question, sql=sql, total=len(rows), result=result
    )
    return llm.invoke(prompt).content.strip()


def ask_database(question: str, max_retries: int = 2) -> dict:
    llm = get_llm()
    schema = get_schema()
    sql = clean_sql(llm.invoke(SQL_PROMPT.format(schema=schema, question=question)).content)

    for attempt in range(max_retries + 1):
        try:
            sql = validate_sql(sql)
            columns, rows = run_query(sql)
            break
        except Exception as exc:  # bad SQL or failed guardrail
            if attempt == max_retries:
                return {
                    "question": question, "sql": sql, "error": str(exc),
                    "columns": [], "rows": [],
                    "answer": "I couldn't produce a valid query for that question.",
                }
            sql = clean_sql(
                llm.invoke(
                    REPAIR_PROMPT.format(
                        schema=schema, question=question, sql=sql, error=str(exc)
                    )
                ).content
            )

    return {
        "question": question, "sql": sql, "error": None,
        "columns": columns, "rows": rows,
        "answer": sql_to_text(question, sql, columns, rows, llm),
    }


if __name__ == "__main__":
    q = " ".join(sys.argv[1:]) or "How many candidates are in each status?"
    out = ask_database(q)
    print("SQL   :", out["sql"])
    print("ROWS  :", out["rows"][:5])
    print("ANSWER:", out["answer"])