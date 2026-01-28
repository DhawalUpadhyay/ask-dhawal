from fastapi import FastAPI
from fastapi import Request

print("FASTAPI BACKEND LOADED")
app = FastAPI(title="AskDhawal API", root_path="/api")

@app.get("/health")
def health():
    return {"status": "ok"}

@app.api_route("/{full_path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def catch_all(full_path: str, request: Request):
    return [
        {"path": r.path, "methods": list(r.methods)}
        for r in app.routes
    ]