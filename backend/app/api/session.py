import re
import uuid
import random
from datetime import datetime, timezone, timedelta

from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.app.limiter import limiter
from backend.app.state import create_session, get_session_meta, verify_session
from backend.app.services.notify import send_otp_email

router = APIRouter(prefix="/api/session")

_EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$")
OTP_EXPIRY_MINUTES = 10


class StartRequest(BaseModel):
    name: str = ""
    email: str


class VerifyRequest(BaseModel):
    session_id: str
    otp: str


@router.post("/start")
@limiter.limit("10/minute")
def start_session(request: Request, req: StartRequest):
    if not _EMAIL_RE.match(req.email.strip()):
        return JSONResponse({"error": "Invalid email address."}, status_code=400)

    session_id = str(uuid.uuid4())
    otp = str(random.randint(100000, 999999))
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=OTP_EXPIRY_MINUTES)

    name = req.name.strip()
    email = req.email.strip().lower()

    create_session(
        session_id=session_id,
        name=name,
        email=email,
        otp=otp,
        otp_expires_at=expires_at,
    )

    send_otp_email(to_email=email, name=name, otp=otp)

    return {"session_id": session_id}


@router.post("/verify")
@limiter.limit("10/minute")
def verify_otp(request: Request, req: VerifyRequest):
    meta = get_session_meta(req.session_id)

    if not meta:
        return JSONResponse({"error": "Session not found."}, status_code=404)

    if meta.get("verified"):
        return {"status": "ok"}  # idempotent

    if datetime.now(timezone.utc) > meta["otp_expires_at"]:
        return JSONResponse({"error": "Code has expired. Please start again."}, status_code=400)

    if req.otp.strip() != meta["otp"]:
        return JSONResponse({"error": "Incorrect code. Please try again."}, status_code=400)

    verify_session(req.session_id)

    return {"status": "ok"}
