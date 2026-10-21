from app.core.llm import get_llm

print(get_llm().invoke("Write a SQL query that counts rows in a table named jobs.").content)