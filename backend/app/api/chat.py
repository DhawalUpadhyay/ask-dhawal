from fastapi import APIRouter
from app.schemas.chat import ChatRequest, ChatResponse
from app.services.responder import generate_reply
import uuid

router = APIRouter()

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    reply = generate_reply(req.message)
    return ChatResponse(
        reply=reply,
        session_id=str(uuid.uuid4())
    )