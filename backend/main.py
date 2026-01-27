from fastapi import FastAPI

app = FastAPI(title="AskDhawal API")

@app.get("/health")
def health():
    return {"status": "ok"}