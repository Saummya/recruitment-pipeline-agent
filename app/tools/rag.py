"""RAG over resumes: chunk -> embed -> store in Chroma -> hybrid candidate matching."""
import re
import sys

import chromadb
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer

from app.core.config import CHROMA_DIR, EMBED_MODEL, PDF_DIR
from app.core.db import run_query

_model = None


def embedder() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL)
    return _model


def collection():
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    # cosine space: distance = 1 - cosine similarity
    return client.get_or_create_collection("resumes", metadata={"hnsw:space": "cosine"})


def read_pdf(path) -> str:
    return "\n".join(page.extract_text() or "" for page in PdfReader(path).pages)


def chunk_resume(text: str) -> list[str]:
    """Split by section headings; prefix each chunk with the resume header
    (name and role) so every chunk still says whose resume it is."""
    parts = re.split(r"(?m)^(?=(?:SUMMARY|SKILLS|EXPERIENCE|EDUCATION)\s*$)", text)
    header = parts[0].strip()
    return [f"{header}\n{p.strip()}" for p in parts[1:] if p.strip()]


def build_index() -> None:
    col = collection()
    ids, docs, metas = [], [], []
    for pdf in sorted(PDF_DIR.glob("*.pdf")):
        cid = int(pdf.stem.split("_")[1])
        for i, chunk in enumerate(chunk_resume(read_pdf(pdf))):
            ids.append(f"{cid}-{i}")
            docs.append(chunk)
            metas.append({"candidate_id": cid})
    embeddings = embedder().encode(docs).tolist()
    col.upsert(ids=ids, documents=docs, embeddings=embeddings, metadatas=metas)
    print(f"Indexed {len(docs)} chunks from {len(set(m['candidate_id'] for m in metas))} resumes")


def match_candidates(jd: str, k: int = 5, min_years: int = 0) -> list[dict]:
    """Vector search for meaning, then SQL for hard facts."""
    res = collection().query(query_embeddings=embedder().encode([jd]).tolist(), n_results=60)

    best = {}  # keep each candidate's best-matching chunk as "evidence"
    for doc, meta, dist in zip(res["documents"][0], res["metadatas"][0], res["distances"][0]):
        cid, score = meta["candidate_id"], 1 - dist
        if cid not in best or score > best[cid]["score"]:
            best[cid] = {"candidate_id": cid, "score": round(score, 3), "evidence": doc}
    if not best:
        return []

    id_list = ",".join(str(int(c)) for c in best)  # ints only, so safe to inline
    _, rows = run_query(
        f"SELECT id, name, current_role, years_experience, status FROM candidates "
        f"WHERE id IN ({id_list}) AND years_experience >= {int(min_years)}"
    )
    results = []
    for cid, name, role, years, status in rows:
        results.append({**best[cid], "name": name, "role": role, "years": years, "status": status})
    return sorted(results, key=lambda r: -r["score"])[:k]


if __name__ == "__main__":
    if sys.argv[1] == "index":
        build_index()
    else:
        jd = sys.argv[2]
        min_years = int(sys.argv[3]) if len(sys.argv) > 3 else 0
        for r in match_candidates(jd, k=5, min_years=min_years):
            print(f"{r['score']}  {r['name']} ({r['role']}, {r['years']} yrs, {r['status']})")
            print("   evidence:", r["evidence"].replace("\n", " | ")[:160])