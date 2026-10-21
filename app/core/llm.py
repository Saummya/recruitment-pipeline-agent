from langchain_ollama import ChatOllama

from app.core.config import LLM_MODEL, OLLAMA_URL


def get_llm(json_mode: bool = False) -> ChatOllama:
    return ChatOllama(
        model=LLM_MODEL,
        base_url=OLLAMA_URL,
        temperature=0,  # 0 = most predictable output, good for SQL
        format="json" if json_mode else None,
    )