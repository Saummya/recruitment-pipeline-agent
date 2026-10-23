"""Graph nodes. Each takes the state and returns the keys it changes."""
import json
import re

from langgraph.types import interrupt

from app.core.config import ROOT
from app.core.db import get_schema, run_query
from app.core.llm import get_llm
from app.graph.state import AgentState
from app.tools.rag import match_candidates
from app.tools.text_to_sql import (
    REPAIR_PROMPT,
    SQL_PROMPT,
    clean_sql,
    sql_to_text,
    validate_sql,
)

# ---------- router ----------

# Deterministic pre-check: messages that START with a write verb.
WRITE_PATTERN = re.compile(
    r"^\s*(please\s+)?(delete|remove|drop|update|insert|modify|edit|change)\b", re.I
)

ROUTER_PROMPT = """Classify the recruiter's message. Return ONLY a JSON object with keys:
- "intent": one of
    "sql"      = a factual question answered from database records: counts, lists,
                 filters, statuses, interviews, jobs, or who has a specific skill
    "match"    = find or rank the best-fitting candidates for a job description or role
    "outreach" = draft and send emails to candidates
    "chat"     = greetings, thanks, or anything not about recruitment data
- "min_years": integer minimum years of experience if the message states one, else 0

Examples:
Message: How many candidates are in each status?
JSON: {{"intent": "sql", "min_years": 0}}
Message: Who are the best fits for a backend role using Kafka and Python, at least 4 years?
JSON: {{"intent": "match", "min_years": 4}}
Message: Email the top 3 frontend candidates about our opening
JSON: {{"intent": "outreach", "min_years": 0}}
Message: Thanks, that was helpful!
JSON: {{"intent": "chat", "min_years": 0}}

Message: {question}
JSON:"""

VALID_INTENTS = {"sql", "match", "outreach", "chat"}


def router(state: AgentState):
    question = state["question"]
    if WRITE_PATTERN.search(question):
        return {"intent": "write"}
    try:
        out = json.loads(
            get_llm(json_mode=True).invoke(ROUTER_PROMPT.format(question=question)).content
        )
        intent = out.get("intent", "chat")
        min_years = int(out.get("min_years") or 0)
    except (json.JSONDecodeError, ValueError, TypeError):
        intent, min_years = "chat", 0
    if intent not in VALID_INTENTS:
        intent = "chat"
    return {"intent": intent, "min_years": min_years, "retries": 0, "error": None}


# ---------- SQL path ----------

def generate_sql(state: AgentState):
    prompt = SQL_PROMPT.format(schema=get_schema(), question=state["question"])
    return {"sql": clean_sql(get_llm().invoke(prompt).content)}


def run_sql(state: AgentState):
    try:
        safe_sql = validate_sql(state["sql"])      # guardrail layer 1
        columns, rows = run_query(safe_sql)        # read-only DB: layer 2
        return {"sql": safe_sql, "columns": columns, "rows": rows, "error": None}
    except Exception as exc:
        return {"error": str(exc)}


def repair_sql(state: AgentState):
    prompt = REPAIR_PROMPT.format(
        schema=get_schema(),
        question=state["question"],
        sql=state["sql"],
        error=state["error"],
    )
    return {
        "sql": clean_sql(get_llm().invoke(prompt).content),
        "retries": state.get("retries", 0) + 1,
    }


def explain(state: AgentState):
    return {
        "answer": sql_to_text(
            state["question"], state["sql"], state["columns"], state["rows"]
        )
    }


def give_up(state: AgentState):
    return {"answer": "I couldn't produce a valid query for that question."}


# ---------- match path ----------

def match_node(state: AgentState):
    matches = match_candidates(
        state["question"], k=5, min_years=state.get("min_years", 0)
    )
    if not matches:
        return {"matches": [], "answer": "No matching candidates found."}
    lines = []
    for i, m in enumerate(matches, 1):
        evidence = m["evidence"].replace("\n", " | ")[:140]
        lines.append(
            f"{i}. {m['name']} ({m['role']}, {m['years']} yrs, {m['status']}) "
            f"- score {m['score']}\n   evidence: {evidence}"
        )
    return {"matches": matches, "answer": "\n".join(lines)}


# ---------- refuse / chat ----------

def refuse(state: AgentState):
    return {
        "answer": "I can only read recruitment data, not change it. "
        "Ask me to look something up, rank candidates, or draft outreach."
    }


CHAT_PROMPT = """You are a recruiting assistant. In one or two sentences, reply to the
message below. If it is not about recruitment, briefly say you can help with: querying
candidate data, matching candidates to roles, and drafting outreach emails.

Message: {question}"""


def chat(state: AgentState):
    return {"answer": get_llm().invoke(CHAT_PROMPT.format(question=state["question"])).content.strip()}


# ---------- outreach path (used in 6F) ----------

EMAIL_PROMPT = """Write a short, friendly email (maximum 90 words) inviting {name}, a {role},
to a quick call about an opportunity. The recruiter's request was: "{request}".
Use ONLY this background about the candidate and invent nothing else:
{evidence}
Start with "Subject:" on the first line. Sign off as "The Recruiting Team"."""


def draft_outreach(state: AgentState):
    matches = match_candidates(
        state["question"], k=3, min_years=state.get("min_years", 0)
    )
    llm = get_llm()
    drafts = []
    for m in matches:
        _, rows = run_query(f"SELECT email FROM candidates WHERE id={int(m['candidate_id'])}")
        body = llm.invoke(
            EMAIL_PROMPT.format(
                name=m["name"], role=m["role"], request=state["question"], evidence=m["evidence"]
            )
        ).content.strip()
        drafts.append(
            {"candidate_id": m["candidate_id"], "name": m["name"], "email": rows[0][0], "body": body}
        )
    return {"matches": matches, "drafts": drafts}


def approval(state: AgentState):
    drafts = state.get("drafts", [])
    if not drafts:
        return {"answer": "No matching candidates to contact."}

    # PAUSE HERE. The graph stops and hands this payload to the caller.
    # When resumed, this node runs again from the top, and interrupt()
    # returns the human's decision instead of pausing.
    decision = interrupt({"type": "approve_emails", "drafts": drafts})

    if not decision.get("approved"):
        return {"answer": "Cancelled. No emails were sent."}

    # Side effects go AFTER the interrupt (the code above re-runs on resume).
    outbox = ROOT / "data" / "outbox.jsonl"
    with outbox.open("a") as f:
        for d in drafts:
            f.write(json.dumps(d) + "\n")
    return {"answer": f"Approved. {len(drafts)} emails queued in data/outbox.jsonl (mock send)."}