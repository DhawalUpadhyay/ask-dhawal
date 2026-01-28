from fastapi import APIRouter, Depends
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.logger import log_interaction, get_chat_history
from backend.app.services.llm_responder import generate_llm_reply as generate_reply
from backend.app.services.greeting import is_greeting, greeting_response
from backend.app.db.database import get_db

import uuid

router = APIRouter(prefix="/api")

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest, db=Depends(get_db)):
    try:
        session_id = req.session_id or str(uuid.uuid4())
        print("Session ID:", session_id)
        if is_greeting(req.message):
            print("Detected greeting message.")
            reply = greeting_response()
            print("Greeting reply:", reply)
            log_interaction(
                session_id=session_id,
                question=req.message,
                answer=reply,
                db=db
            )
            print("Logged greeting interaction.")
            return ChatResponse(
                reply=reply,
                session_id=session_id
            )

        history = get_chat_history(session_id)
        reply = generate_reply(req.message, history)

        log_interaction(
            session_id=session_id,
            question=req.message,
            answer=reply
        )

        return ChatResponse(
            reply=reply,
            session_id=session_id
        )
    except Exception as e:
        print(f"Error processing chat request: {e}")
        raise e

@router.get("/health")
def health():
    return {"status": "ok"}

@router.get("/__routes")
def show_routes():
    return [
        {"path": r.path, "methods": list(r.methods)}
        for r in router.routes
    ]