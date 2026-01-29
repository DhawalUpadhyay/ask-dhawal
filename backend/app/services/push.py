import requests
import os
from dotenv import load_dotenv

load_dotenv()

pushover_user = os.getenv("PUSHOVER_USER")
pushover_token = os.getenv("PUSHOVER_TOKEN")
pushover_url = "https://api.pushover.net/1/messages.json"

def push(message):
    print(f"Push: {message}")
    print(pushover_user, pushover_token, sep=", ")
    payload = {"user": pushover_user, "token": pushover_token, "message": message}
    res = requests.post(pushover_url, data=payload)
    print(f"Push response: {res.status_code}, {res.text}")
