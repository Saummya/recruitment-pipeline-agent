import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]

DB_PATH = Path(os.getenv("DB_PATH", ROOT / "data" / "recruitment.db"))
PDF_DIR = ROOT / "data" / "resumes_pdf"
CHROMA_DIR = ROOT / "chroma_db"

LLM_MODEL = os.getenv("LLM_MODEL", "qwen2.5-coder:7b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = "sentence-transformers/all-MiniLM-L6-v2"