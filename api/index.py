from fastapi import FastAPI
from backend.app.api.chat import router as chat_router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="AskDhawal API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # safe for public resume
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/__routes")
def show_routes():
    return [
        {"path": r.path, "methods": list(r.methods)}
        for r in app.routes
    ]
