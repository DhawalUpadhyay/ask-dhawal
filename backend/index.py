from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.app.api.chat import router as chat_router
from backend.app.limiter import limiter

app = FastAPI(title="AskDhawal API")

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,  # wildcard origin + credentials=True is invalid per CORS spec
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
