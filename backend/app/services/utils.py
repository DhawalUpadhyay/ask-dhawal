import re
from backend.app.services.push import push

def has_email_optional_name(msg: str) -> bool:
    info = {}

    # Email (required)
    email_pattern = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"
    email_match = re.search(email_pattern, msg)

    if not email_match:
        return False

    info["email"] = email_match.group()

    # Name (optional): two capitalized words
    name_pattern = r"\b([A-Z][a-z]+)\s+([A-Z][a-z]+)\b"
    name_match = re.search(name_pattern, msg)

    if name_match:
        info["name"] = name_match.group()

    # info dict exists internally with:
    # {"email": "..."} OR {"email": "...", "name": "..."}
    push(str(info))
    return True
