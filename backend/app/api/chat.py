from fastapi import APIRouter
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.logger import log_interaction, get_chat_history
from backend.app.services.llm_responder import generate_llm_reply as generate_reply
from backend.app.services.greeting import is_greeting, greeting_response

import uuid

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    if is_greeting(req.message):
        reply = greeting_response()
        log_interaction(
            session_id=session_id,
            question=req.message,
            answer=reply
        )
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