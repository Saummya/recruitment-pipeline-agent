mkdir -p .claude/skills/explain-project/reference
cat > .claude/skills/explain-project/SKILL.md <<'EOF'
---
name: explain-project
description: Explains the Recruitment Pipeline Agent project from start to finish in simple, non-technical language using everyday analogies. Use when the user asks to explain, walk through, present, summarise or describe this project, or wants help preparing for an interview, demo, viewer question or README about it.
---

# Explain the Recruitment Pipeline Agent

## Purpose
Help anyone understand this project, even with no technical background, from the problem it solves to how each piece works, how it is monitored, and what is still unfinished.

## Step 1: Check the real state first
The project keeps changing, so never rely only on the reference files. Before explaining:
- Read README.md and docs/learning-log.md for the latest status and numbers.
- List the app/, ui/, evals/ and docker/ folders to see what really exists.
- Treat anything not found in the repo as planned, not built. Say so plainly.
  (Typical late-stage items: MCP tool servers, A2A agents, a full Docker Compose of the whole app.)

## Step 2: Pick the audience and length
- If the user did not say, assume a complete beginner and ask one short question only if the choice really matters.
- Offer or infer one of three lengths:
  - 1 minute: the problem, the idea, one example, the result.
  - 5 minutes: the story in reference/story.md, one short paragraph per chapter.
  - Full walkthrough: every chapter in reference/story.md, with the worked examples.
- If the user is preparing for an interview, end with 5 likely questions and short honest answers.

## Step 3: Explain with a running analogy
Use ONE analogy throughout: the project is a small recruiting office staffed by specialists.
- Receptionist who decides who handles each request = the router
- Records clerk who looks things up in the filing cabinet = Text-to-SQL
- Librarian who reads resumes for meaning = RAG and embeddings
- Interpreter who listens and speaks = speech-to-text and text-to-speech
- Manager who must sign off before any email goes out = human approval step
- Security locks on the filing cabinet = guardrails and read-only database
- CCTV and logbook of everything that happened = Langfuse tracing
- Practice exams for the staff = evals

## Style rules
- Say what a thing does in everyday words BEFORE using its technical name.
- Define each technical term once, using reference/glossary.md for wording.
- Use short paragraphs and concrete examples. Avoid long lists of jargon.
- Always include at least one worked example following a single real request through the system.
- Name the real files (for example app/graph/nodes.py) so the reader can find things, but never make the file names the explanation.
- Use real numbers from the learning log (eval scores, parse accuracy), and say the date or state they are from.

## Honesty rules
- Never claim a feature is finished unless you saw it in the repo or log.
- Always include a short "limits and known issues" part. The project is a learning and portfolio build on fake data, not a production hiring tool.
- Mention the fairness caution: AI resume screening can be biased, which is why a human approves every email and names are not used for scoring.
- If asked something the files do not answer, say you do not know instead of guessing.

## Ending
Close by asking whether the user wants a simpler version, a deeper dive on one chapter, or interview practice.
EOF