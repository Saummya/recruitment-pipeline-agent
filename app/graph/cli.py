import sys
import uuid

from langgraph.checkpoint.memory import InMemorySaver
from langgraph.types import Command

from app.graph.graph import build_graph


def main():
    question = " ".join(sys.argv[1:]) or "How many candidates are in each status?"
    graph = build_graph(checkpointer=InMemorySaver())
    config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    result = graph.invoke({"question": question}, config)

    # If the graph paused for human approval (6F), show the drafts and ask.
    if "__interrupt__" in result:
        payload = result["__interrupt__"][0].value
        for d in payload["drafts"]:
            print(f"\n--- To: {d['name']} <{d['email']}> ---\n{d['body']}")
        choice = input("\nSend these emails? (y/n): ").strip().lower()
        result = graph.invoke(Command(resume={"approved": choice == "y"}), config)

    print("INTENT:", result.get("intent"))
    if result.get("sql"):
        print("SQL   :", result["sql"])
    print("ANSWER:", result["answer"])


if __name__ == "__main__":
    main()