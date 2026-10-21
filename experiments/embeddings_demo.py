from sentence_transformers import SentenceTransformer, util

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

jd = "Backend engineer with Python, FastAPI and PostgreSQL experience"
resumes = [
    "Built REST APIs with FastAPI and PostgreSQL for a fintech startup",
    "Designed React dashboards and component libraries in TypeScript",
    "Managed Kubernetes clusters and CI/CD pipelines on AWS",
]

jd_vec = model.encode(jd)
resume_vecs = model.encode(resumes)
scores = util.cos_sim(jd_vec, resume_vecs)[0]

for text, score in sorted(zip(resumes, scores), key=lambda x: -x[1]):
    print(f"{score:.3f}  {text}")