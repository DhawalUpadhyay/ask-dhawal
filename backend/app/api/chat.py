import json
import uuid
from typing import Generator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from backend.app.limiter import limiter
from backend.app.schemas.chat import ChatRequest
from backend.app.services.greeting import is_greeting, greeting_response
from backend.app.services.llm_responder import generate_llm_stream
from backend.app.services.utils import has_email_optional_name
from backend.app.state import get_history, save_history

MAX_HISTORY = 12
router = APIRouter(prefix="/api")


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


def _simple_stream(text: str, session_id: str = None) -> Generator:
    """Wrap a static text response as SSE."""
    if session_id:
        yield _sse({"type": "session", "session_id": session_id})
    yield _sse({"type": "token", "content": text})
    yield _sse({"type": "done"})


def _llm_stream(message: str, history: list, session_id: str) -> Generator:
    """Stream LLM tokens as SSE, then persist the completed reply."""
    yield _sse({"type": "session", "session_id": session_id})
    full_reply = ""
    for token in generate_llm_stream(message, history):
        full_reply += token
        yield _sse({"type": "token", "content": token})
    updated = history + [
        {"role": "user", "content": message},
        {"role": "assistant", "content": full_reply},
    ]
    save_history(session_id, updated[-MAX_HISTORY:])
    yield _sse({"type": "done"})


@router.post("/chat")
@limiter.limit("30/minute")
def chat(request: Request, req: ChatRequest):
    # --- No session yet: require email ---
    if not req.session_id:
        if not has_email_optional_name(req.message):
            print("Email not found in message.")
            return StreamingResponse(
                _simple_stream(
                    "To get started, please share your email address "
                    "(and optionally your name) in your message."
                ),
                media_type="text/event-stream",
            )
        new_session_id = str(uuid.uuid4())
        print(f"New session created: {new_session_id}")
        return StreamingResponse(
            _simple_stream(
                "Thank you! You can now ask me anything about my experience, "
                "skills, or projects.",
                session_id=new_session_id,
            ),
            media_type="text/event-stream",
        )

    session_id = req.session_id
    history = get_history(session_id)
    print(f"Session ID: {session_id}, history length: {len(history)}")

    # --- Greeting short-circuit ---
    if is_greeting(req.message):
        print("Detected greeting.")
        reply = greeting_response()
        updated = history + [
            {"role": "user", "content": req.message},
            {"role": "assistant", "content": reply},
        ]
        save_history(session_id, updated[-MAX_HISTORY:])
        return StreamingResponse(
            _simple_stream(reply, session_id=session_id),
            media_type="text/event-stream",
        )

    # --- LLM streaming response ---
    return StreamingResponse(
        _llm_stream(req.message, history, session_id),
        media_type="text/event-stream",
    )


@router.get("/health")
def health():
    return {"status": "ok"}
