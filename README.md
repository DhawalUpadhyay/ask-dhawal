# Ask Dhawal — AI Interactive Resume

An AI-powered resume chatbot that lets recruiters have a real conversation instead of reading a PDF.
Recruiters verify their email via OTP, then chat with an AI that answers questions strictly based on curated resume data.
After the conversation ends, a summary is automatically emailed to the owner.

**Live:** (https://ask-dhawal.vercel.app/)

---

## Features

- **Email OTP login** — recruiter enters name + email, receives a 6-digit code, verified before accessing chat
- **Real-time streaming** — responses stream token by token via Server-Sent Events (SSE)
- **Conversation summary** — automatically emailed to owner 2 minutes after the recruiter goes idle
- **Session persistence** — PostgreSQL-backed with in-memory fallback for local dev
- **Greeting short-circuit** — greetings are handled without an LLM call
- **Rate limiting** — 30 requests/min per IP via slowapi
- **Prompt injection protection** — system prompt explicitly guards against persona override attempts
- **Mobile responsive** — full-viewport layout on small screens

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python, FastAPI |
| LLM | OpenAI GPT-4o-mini (streaming) |
| Frontend | React, Vite |
| Database | PostgreSQL (psycopg2), in-memory fallback |
| Email | Gmail SMTP (smtplib) |
| Rate limiting | slowapi |
| Deployment | Vercel |

---

## Project Structure

```
ask-dhawal/
├── backend/
│   ├── index.py                        # FastAPI app entry, CORS, rate limiter, lifespan
│   └── app/
│       ├── api/
│       │   ├── chat.py                 # POST /api/chat — SSE streaming endpoint
│       │   └── session.py              # POST /api/session/start, /api/session/verify
│       ├── data/
│       │   └── resume.py               # Resume content — update this to change AI knowledge
│       ├── llm/
│       │   └── system_prompt.py        # Builds system prompt from resume data
│       ├── schemas/
│       │   └── chat.py                 # ChatRequest pydantic model (max 2000 chars)
│       ├── services/
│       │   ├── greeting.py             # Greeting detection + static responses
│       │   ├── llm_responder.py        # generate_llm_stream() — yields tokens
│       │   ├── notify.py               # Gmail SMTP — OTP email, summary email
│       │   └── summariser.py           # OpenAI summary of completed conversation
│       ├── tasks/
│       │   └── session_reaper.py       # Background thread — sends summary after 2 min idle
│       ├── limiter.py                  # Shared slowapi Limiter instance
│       └── state.py                    # Session store: PostgreSQL + in-memory fallback
├── frontend/
│   └── src/
│       ├── App.jsx                     # Chat UI with login → otp → chat state machine
│       ├── Login.jsx                   # Name + email form
│       ├── OtpVerify.jsx               # 6-digit OTP entry
│       ├── App.css                     # Typing dots animation, mobile overrides
│       └── config/api.js               # API_BASE_URL from env
├── requirements.txt
└── vercel.json                         # /api/* → Python backend, /* → React build
```

---

## Request Flow

```
Recruiter visits site
    ↓
Login screen (name + email)
    ↓
POST /api/session/start
  → OTP generated, emailed to recruiter (synchronous — required for Vercel serverless)
    ↓
OTP screen (6-digit code)
    ↓
POST /api/session/verify
  → Session marked verified
    ↓
Chat opens
    ↓
POST /api/chat (SSE)
  → Verified session check
  → Greeting short-circuit or LLM stream
  → Tokens yielded as: {"type": "token", "content": "..."}
  → Session history saved after stream completes
    ↓
Recruiter goes idle for 2 minutes
    ↓
Background reaper fires
  → OpenAI generates conversation summary
  → Summary emailed to owner via Gmail SMTP
```

---

## SSE Event Protocol

All `/api/chat` responses are `text/event-stream`. Two event types:

```json
{"type": "token", "content": "..."}   // incremental LLM token
{"type": "done"}                       // stream complete
```

---

## Local Setup

### 1. Environment variables

Create `.env` at the project root:

```
OPENAI_API_KEY=your_key
OPENAI_MODEL=gpt-4o-mini
GMAIL_USER=your.email@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx
NOTIFY_EMAIL=your.email@gmail.com
DATABASE_URL=postgresql://...          # optional — falls back to in-memory
```

> `GMAIL_APP_PASSWORD` must be a Google App Password, not your regular Gmail password.
> Generate one at: Google Account → Security → 2-Step Verification → App Passwords.

### 2. Backend

```bash
source venv/bin/activate
pip install -r requirements.txt
uvicorn backend.index:app --reload
```

Runs at `http://localhost:8000`

### 3. Frontend

```bash
cd frontend
npm install
npm run dev
```

Runs at `http://localhost:5173`

---

## Deployment (Vercel)

Set the following in Vercel dashboard → Settings → Environment Variables:

```
OPENAI_API_KEY
OPENAI_MODEL
GMAIL_USER
GMAIL_APP_PASSWORD
NOTIFY_EMAIL
DATABASE_URL        # optional
```

> **Note:** The session reaper (background thread) does not persist on Vercel serverless.
> The OTP email is sent synchronously to work around this. Summary emails on Vercel
> require a Vercel Cron Job pointing to a `/api/reap` endpoint.

---

## Updating Resume Data

All AI responses are grounded in `backend/app/data/resume.py`.
Edit that file to change what the chatbot knows. The LLM has no knowledge outside of it.
