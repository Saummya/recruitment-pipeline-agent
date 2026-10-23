from typing import TypedDict

from langgraph.graph import END, START, StateGraph


class State(TypedDict):
    text: str
    log: list[str]


def clean(state: State):
    return {"text": state["text"].strip(), "log": state["log"] + ["clean"]}


def shout(state: State):
    return {"text": state["text"].upper() + "!", "log": state["log"] + ["shout"]}


def whisper(state: State):
    return {"text": state["text"].lower() + "...", "log": state["log"] + ["whisper"]}


def pick(state: State) -> str:
    # a conditional edge function: returns the NAME of the next path
    return "shout" if len(state["text"]) < 10 else "whisper"


g = StateGraph(State)
g.add_node("clean", clean)
g.add_node("shout", shout)
g.add_node("whisper", whisper)

g.add_edge(START, "clean")
g.add_conditional_edges("clean", pick, {"shout": "shout", "whisper": "whisper"})
g.add_edge("shout", END)
g.add_edge("whisper", END)

app = g.compile()
print(app.invoke({"text": "  hello  ", "log": []}))
print(app.invoke({"text": "  this is a much longer sentence  ", "log": []}))