import requests
import os
import threading
from dotenv import load_dotenv

load_dotenv()

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"


def _send(message: str) -> None:
    try:
        payload = {"user": pushover_user, "token": pushover_token, "message": message}
        res = requests.post(pushover_url, data=payload, timeout=5)
        print(f"Push response: {res.status_code}")
    except Exception as e:
        print(f"Push failed: {e}")


def push(message: str) -> None:
    """Fire-and-forget Pushover notification (non-blocking)."""
    threading.Thread(target=_send, args=(message,), daemon=True).start()
