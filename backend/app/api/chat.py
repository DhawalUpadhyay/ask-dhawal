from fastapi import APIRouter
from backend.app.schemas.chat import ChatRequest, ChatResponse
from backend.app.services.llm_responder import generate_llm_reply as generate_reply
from backend.app.services.greeting import is_greeting, greeting_response
from backend.app.state import conversation_store

import uuid

router = APIRouter(prefix="/api")

@router.post("/chat", response_model=ChatResponse)
def chat(req: ChatRequest):
    try:
        session_id = req.session_id or str(uuid.uuid4())
        print("Session ID:", session_id)
        conversation_store[session_id].append({
            "role": "user",
            "content": req.message
        })
        if is_greeting(req.message):
            print("Detected greeting message.")
            reply = greeting_response()
            print("Greeting reply:", reply)
            conversation_store[session_id].append({
                "role": "assistant",
                "content": reply
            })
            print("Logged greeting interaction.")
            return ChatResponse(
                reply=reply,
                session_id=session_id
            )

        # history = get_chat_history(session_id)
        context = conversation_store[session_id][:-1]  # all but last message
        reply = generate_reply(req.message, context)

        conversation_store[session_id].append({
            "role": "assistant",
            "content": reply
        })

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
