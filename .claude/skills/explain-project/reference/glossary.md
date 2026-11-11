cat > .claude/skills/explain-project/reference/glossary.md <<'EOF'
# Plain-language glossary

- LLM (large language model): an AI that reads and writes text, like the engine behind a chatbot.
- Prompt: the written instructions and context you give the AI.
- Few-shot examples: a few sample questions with correct answers placed in the prompt so the AI copies the pattern.
- Hallucination: the AI confidently making something up.
- Ollama: a free tool that runs AI models on your own computer.
- Hugging Face: a public library of AI models.
- Embedding: a list of numbers that captures the meaning of a text, so similar meanings sit close together.
- Vector database (Chroma): a database that finds the stored items whose meaning is nearest to a question.
- RAG: look up the relevant pieces from your own documents first, then let the AI answer using them.
- SQL: the strict language databases understand.
- Schema: the blueprint of a database (its tables and columns).
- JOIN: linking rows in two tables, like matching a candidate to their skills.
- Text-to-SQL: the AI turns a plain question into SQL. SQL-to-text: the AI turns the result rows into a sentence.
- Guardrail: a rule in code that blocks unsafe actions regardless of what the AI wants.
- Read-only: the database can be looked at but never changed.
- Pydantic: a checker that makes sure data has the right shape (a number is a number).
- LangGraph: a toolkit for building an AI program as a flowchart with steps, branches, loops and pauses.
- Node: one step in the flowchart. Edge: an arrow between steps. Conditional edge: an arrow that is chosen by a decision.
- State: the notebook carried from step to step holding the question, SQL, rows and answer.
- Router: the step that decides which path a request takes.
- Human in the loop: the process stops and waits for a person to decide.
- Checkpoint and thread id: a saved bookmark of the process so it can be paused and resumed for the same conversation.
- API: a doorway that programs use to talk to other programs. FastAPI builds it.
- Streamlit: a tool for building simple web screens in Python.
- Whisper: an AI that turns speech into text. TTS (text-to-speech): an AI that speaks text.
- Docker image / container: a sealed package of a program and everything it needs / a running copy of that package.
- Docker Compose: one file that starts several containers together.
- Langfuse: a logbook that records every step of every AI request. Trace: one request from start to finish. Score: a rating attached to a trace.
- Eval: a test set with known right answers, used to measure quality with a number.
- Harness engineering: building the tests, guardrails, retries and monitoring around an AI so it can be trusted.
- MCP (Model Context Protocol): a standard plug shape so any AI app can connect to tools like email or calendar.
- A2A (agent to agent): a standard way for separate AI agents to talk to each other.
- Skill: a folder of written know-how an AI loads only when a task needs it.
EOF