cat > .claude/skills/explain-project/reference/story.md <<'EOF'
# The story of the Recruitment Pipeline Agent
(Numbers below were true when this file was written. Re-check docs/learning-log.md.)

## Chapter 1: The problem
A recruiter gets hundreds of resumes for one job. They read PDFs, copy details into spreadsheets, decide who to shortlist, write emails, schedule interviews, and chase interviewers for feedback. It is slow, repetitive, and things get lost between steps.
This project is an assistant that does the repetitive parts, while a human keeps the final say.

## Chapter 2: The idea in one line
You talk or type to it like a colleague ("show me backend candidates with 3+ years who have not been contacted", "who fits this role?", "email the top three"). It figures out what you mean, does the work, and explains the answer in plain English.

## Chapter 3: The practice data
Real resumes are private, so we generated 60 fake candidates with a script (data/generate_data.py). They live in a small database with five tables, like five spreadsheet tabs: candidates, skills, jobs, applications, interviews. Each candidate also has a fake resume, later turned into PDF.
Why it matters: you can safely show the project to anyone, and the data is repeatable so tests are fair.

## Chapter 4: The brain, running on your own laptop
The assistant uses an AI language model (an LLM) that runs locally through a tool called Ollama, so no resume data leaves the machine. Other open models from Hugging Face handle specialist jobs: one turns text into numbers that capture meaning (embeddings), one listens (Whisper), one speaks.
Limit: small local models make more mistakes than giant cloud models, which is why we built checks around them.

## Chapter 5: Asking the database in plain English (Text-to-SQL)
The database only understands a strict language called SQL. The assistant shows the AI the layout of the database, plus a few hints and examples, and the AI writes the SQL. The program then checks it is safe (only reading, only known tables, never more than 50 rows), runs it, and asks the AI to explain the rows in a sentence ("SQL to text").
If the SQL fails, the error is handed back and the AI tries again, up to two times.
Safety is layered: a code check AND a database opened in read-only mode, so even a mistake cannot delete anything. Files: app/tools/text_to_sql.py, app/core/db.py.

## Chapter 6: Reading resumes (parsing and RAG)
Parsing: the AI reads a resume PDF and fills a form (name, role, years, skills). A strict checker rejects badly shaped answers, and a simple rule overrides the AI where the resume states total years plainly.
RAG (retrieval-augmented generation) is the librarian. Each resume is cut into sections and turned into number-lists capturing meaning, stored in a special database called Chroma. To find good candidates, the job description is turned into numbers too and compared. "FastAPI" matches "built REST APIs" because the meanings are close, not because the words match.
Then plain database filters add hard facts the librarian is bad at (minimum years, not rejected). Each match comes with evidence: the resume text that matched. Files: app/tools/resume_parser.py, app/tools/rag.py.
Known limits: it can rank a data engineer in a backend search, and exact skill requirements are fuzzy.

## Chapter 7: The traffic controller (LangGraph)
A graph is a flowchart that the program follows. First the router reads the message and picks a path:
- a data question goes to the SQL path
- "who fits this role" goes to the matching path
- "email them" goes to the outreach path
- "delete anything" is refused immediately by a simple rule (a rule, not an AI opinion, because safety rules should not depend on a model behaving)
- anything else becomes friendly chat
The flowchart also has a loop for retrying bad SQL, and a pause button for human approval. Files: app/graph/state.py, nodes.py, graph.py. A picture is in docs/graph.png.

## Chapter 8: The manager's signature (human approval)
For outreach the assistant drafts emails, then the whole process pauses and waits. A person reads the drafts and clicks Approve or Cancel. Only after Approve does anything get "sent". Today sending is a mock: it writes to a file (data/outbox.jsonl) and skips anyone already emailed or rejected.
Why it matters: AI output going to real people should never skip a human check. (In testing the AI left "[Company Name]" in an email, which is exactly why.)

## Chapter 9: The face and the ears (API, UI and voice)
An API is a doorway that other programs knock on. FastAPI provides it (app/api/main.py): chat, approve, speech-to-text, text-to-speech, candidate lists, feedback. Streamlit provides the screen (ui/app.py) with four tabs: chat, candidates, voice feedback, daily briefing.
Voice feedback: an interviewer speaks, Whisper writes it down, the AI turns it into a structured note (strengths, weaknesses, hire/hold/reject, score), the person reviews and saves it. After that the chat can answer "who got a hire recommendation?". Speech became searchable data.

## Chapter 10: The security camera (Langfuse)
Langfuse records every step of every request: which path was taken, the exact prompt sent to the AI, the answer, and how long each step took. Without it the AI is a black box. Thumbs up or down buttons can attach a score to a request, and the bad ones become new test cases. It runs on the same laptop through Docker, so recruiting data stays local.

## Chapter 11: Practice exams (evals) and quality
Evals are test sets with known right answers. Examples: the SQL test went from 3 of 6 to 6 of 6 after we found the real causes (a too-strict test, an invented column, a misread question); the router test scored 10 of 10; resume parsing scored 10 of 10 on skills and 9 of 10 on years before a fix. The small size of these tests is itself a limit, and growing them is part of the plan. This discipline of measuring, finding failures, fixing and re-measuring is what "harness engineering" means in practice: building the guardrails, tests and monitoring around an AI so it can be trusted.

## Chapter 12: What happens to one real request
Example: "Show me backend candidates with 3+ years of experience who have not been contacted".
1. The screen sends the text to the API.
2. The router decides this is a data question.
3. The AI writes SQL using the database layout and examples.
4. The safety check approves it (only reading, known tables).
5. The read-only database returns the rows.
6. The AI turns them into a short answer.
7. The screen shows the answer, a table, and the SQL used.
8. Langfuse recorded every step, so anyone can inspect it later.

Example 2: "Email the top 3 backend candidates". Router picks outreach, matching finds candidates, the AI drafts emails from resume evidence, the process pauses, a person approves, the mock outbox records it.

## Chapter 13: Honest limits and what is next
- All data is fake. Emails are mock. It is a learning and portfolio project, not a production hiring system.
- The local model is small and imperfect; checks and retries exist because of that.
- The conversation memory is kept in the running program, so it resets on restart.
- Bias risk is real in resume screening: names should not influence scoring, and a human approves outreach.
- Planned or in progress (check the repo): MCP tool servers for real email and calendar, splitting work into separate agents that talk through the A2A protocol, a bigger test suite, and packaging everything with Docker Compose.
EOF