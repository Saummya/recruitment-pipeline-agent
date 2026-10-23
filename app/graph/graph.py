from langgraph.graph import END, START, StateGraph

from app.graph import nodes
from app.graph.state import AgentState

MAX_RETRIES = 2


def route_by_intent(state: AgentState) -> str:
    return state["intent"]


def after_run_sql(state: AgentState) -> str:
    if state.get("error"):
        return "repair_sql" if state.get("retries", 0) < MAX_RETRIES else "give_up"
    return "explain"


def build_graph(checkpointer=None):
    g = StateGraph(AgentState)

    g.add_node("router", nodes.router)
    g.add_node("generate_sql", nodes.generate_sql)
    g.add_node("run_sql", nodes.run_sql)
    g.add_node("repair_sql", nodes.repair_sql)
    g.add_node("explain", nodes.explain)
    g.add_node("give_up", nodes.give_up)
    g.add_node("match_node", nodes.match_node)
    g.add_node("refuse", nodes.refuse)
    g.add_node("chat", nodes.chat)
    g.add_node("draft_outreach", nodes.draft_outreach)
    g.add_node("approval", nodes.approval)

    g.add_edge(START, "router")
    g.add_conditional_edges(
        "router",
        route_by_intent,
        {
            "sql": "generate_sql",
            "match": "match_node",
            "outreach": "draft_outreach", 
            "write": "refuse",
            "chat": "chat",
        },
    )

    # the SQL repair loop
    g.add_edge("generate_sql", "run_sql")
    g.add_conditional_edges(
        "run_sql",
        after_run_sql,
        {"repair_sql": "repair_sql", "give_up": "give_up", "explain": "explain"},
    )
    g.add_edge("repair_sql", "run_sql")

    # outreach path (wired up in 6F)
    g.add_edge("draft_outreach", "approval")

    for end_node in ("explain", "give_up", "match_node", "refuse", "chat", "approval"):
        g.add_edge(end_node, END)

    return g.compile(checkpointer=checkpointer)