from fastapi import FastAPI

app = FastAPI(title="Recruitment Pipeline Agent")


@app.get("/health")
def health():
    return {"status": "ok"}