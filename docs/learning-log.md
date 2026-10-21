## Text-to-SQL eval
- Run 1 (basic prompt, strict compare): 3/6
  - Failures: extra columns (eval too strict), invented column `interviews.stage`, misread "years" as "skills"
- Run 2 (schema notes + few-shot examples + fairer comparison): 6/6
- Next: grow to 15-20 questions with a held-out set