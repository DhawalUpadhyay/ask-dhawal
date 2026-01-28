# backend/app/state.py

from collections import defaultdict

# session_id -> list of messages
conversation_store = defaultdict(list)
