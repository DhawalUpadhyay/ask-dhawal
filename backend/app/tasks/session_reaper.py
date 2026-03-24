import threading
import time

from backend.app.state import get_history, get_idle_sessions, mark_summary_sent
from backend.app.services.notify import send_summary_email
from backend.app.services.summariser import generate_summary

_CHECK_INTERVAL_SECONDS = 60       # check every 1 minute
_IDLE_THRESHOLD_MINUTES = 2


def _reaper_loop() -> None:
    while True:
        time.sleep(_CHECK_INTERVAL_SECONDS)
        try:
            idle = get_idle_sessions(idle_minutes=_IDLE_THRESHOLD_MINUTES)
            for session in idle:
                session_id = session["session_id"]
                messages = session["messages"] or get_history(session_id)

                # Mark sent first to avoid double-sending if summary fails mid-way
                mark_summary_sent(session_id)

                if not messages:
                    print(f"Reaper: session {session_id} had no messages — skipping summary.")
                    continue

                transcript = "\n".join(
                    f"{'Recruiter' if m['role'] == 'user' else 'Dhawal'}: {m['content']}"
                    for m in messages
                )
                summary = generate_summary(messages)
                send_summary_email(
                    name=session["recruiter_name"],
                    email=session["recruiter_email"],
                    transcript=transcript,
                    summary=summary,
                )
                print(f"Reaper: summary sent for session {session_id}")
        except Exception as e:
            print(f"Reaper error: {e}")


def start_reaper() -> None:
    threading.Thread(target=_reaper_loop, daemon=True).start()
    print("Session reaper started.")
