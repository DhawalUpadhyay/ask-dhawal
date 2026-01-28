from fastapi import FastAPI

print("FASTAPI BACKEND LOADED")
app = FastAPI(title="AskDhawal API")

@app.get("/health")
def health():
    return {"status": "ok"}