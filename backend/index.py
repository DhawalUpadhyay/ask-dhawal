from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from backend.app.api.chat import router as chat_router
from backend.app.api.session import router as session_router
from backend.app.limiter import limiter
from backend.app.tasks.session_reaper import start_reaper


@asynccontextmanager
async def lifespan(app: FastAPI):
    start_reaper()
    yield


app = FastAPI(title="AskDhawal API", lifespan=lifespan)

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(chat_router)
app.include_router(session_router)
