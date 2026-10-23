## Text-to-SQL eval
- Run 1 (basic prompt, strict compare): 3/6
  - Failures: extra columns (eval too strict), invented column `interviews.stage`, misread "years" as "skills"
- Run 2 (schema notes + few-shot examples + fairer comparison): 6/6
- Next: grow to 15-20 questions with a held-out set

## RAG matching
- 240 chunks from 60 resumes (4 sections per resume)
- Top results for a backend JD were all backend engineers, with skill-chunk evidence
- Weaknesses found: ignores pipeline status, fuzzy skill ranking, no notion of years
- Fixes: status filter + min_years via SQL (hybrid); idea for later: rerank by exact skill overlap