from typing import Any, TypedDict


class AgentState(TypedDict, total=False):
    question: str
    intent: str            # sql | match | outreach | write | chat
    min_years: int
    # SQL path
    sql: str
    columns: list[str]
    rows: list[Any]
    error: str | None
    retries: int
    # match / outreach path
    matches: list[dict]
    drafts: list[dict]
    # output
    answer: str