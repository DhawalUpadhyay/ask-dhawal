from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.logger import log_interaction
from app.services.responder import generate_reply
import uuid

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    session_id = req.session_id or str(uuid.uuid4())
    reply = generate_reply(req.message)

    log_interaction(
        session_id=session_id,
        question=req.message,
        answer=reply
    )

    return ChatResponse(
        reply=reply,
        session_id=session_id
    )