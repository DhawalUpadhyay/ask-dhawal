import json
from typing import Generator

from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse

from backend.app.limiter import limiter
from backend.app.schemas.chat import ChatRequest
from backend.app.services.greeting import is_greeting, greeting_response
from backend.app.services.llm_responder import generate_llm_stream
from backend.app.state import get_history, save_history, get_session_meta, update_last_active

MAX_HISTORY = 12
router = APIRouter(prefix="/api")


def _sse(data: dict) -> str:
    return f"data: {json.dumps(data)}\n\n"


def _simple_stream(text: str) -> Generator:
    yield _sse({"type": "token", "content": text})
    yield _sse({"type": "done"})


def _llm_stream(message: str, history: list, session_id: str) -> Generator:
    """Stream LLM tokens as SSE, then persist the completed reply."""
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
    if not req.session_id:
        return StreamingResponse(
            _simple_stream("No session found. Please log in first."),
            media_type="text/event-stream",
        )

    meta = get_session_meta(req.session_id)
    if not meta or not meta.get("verified"):
        return StreamingResponse(
            _simple_stream("Session not verified. Please log in again."),
            media_type="text/event-stream",
        )

    update_last_active(req.session_id)

    session_id = req.session_id
    history = get_history(session_id)

    # --- Greeting short-circuit ---
    if is_greeting(req.message):
        reply = greeting_response()
        updated = history + [
            {"role": "user", "content": req.message},
            {"role": "assistant", "content": reply},
        ]
        save_history(session_id, updated[-MAX_HISTORY:])
        return StreamingResponse(
            _simple_stream(reply),
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
