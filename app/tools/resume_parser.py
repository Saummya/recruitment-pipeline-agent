"""Resume PDF -> structured fields, using an LLM in JSON mode."""
import json
import sys
from pathlib import Path
import re

from pydantic import BaseModel, ValidationError
from pypdf import PdfReader

from app.core.llm import get_llm


class ParsedResume(BaseModel):
    name: str
    current_role: str
    years_experience: int
    skills: list[str]
    companies: list[str]


PARSE_PROMPT = """Extract information from this resume. Return ONLY a JSON object with
exactly these keys:
- name (string)
- current_role (string)
- years_experience (integer, total years of experience stated in the resume)
- skills (list of strings)
- companies (list of strings, employers mentioned)

Resume:
{text}
"""


def read_pdf(path: Path) -> str:
    return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)


def parse_resume(path: Path, retries: int = 1) -> ParsedResume:
    text = read_pdf(path)
    llm = get_llm(json_mode=True)
    for attempt in range(retries + 1):
        raw = llm.invoke(PARSE_PROMPT.format(text=text)).content
        try:
            parsed = ParsedResume(**json.loads(raw))
            break
        except (json.JSONDecodeError, ValidationError):
            if attempt == retries:
                raise

    # Deterministic check: trust an explicit "N years of experience" over the model
    match = re.search(r"(\d+)\s+years of experience", text, re.I)
    if match:
        parsed.years_experience = int(match.group(1))
    return parsed


if __name__ == "__main__":
    print(parse_resume(Path(sys.argv[1])).model_dump_json(indent=2))