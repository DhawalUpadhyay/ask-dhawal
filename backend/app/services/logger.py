from app.db.database import SessionLocal
from app.db.models import Interaction

def log_interaction(session_id: str, question: str, answer: str):
    db = SessionLocal()
    interaction = Interaction(
        session_id=session_id,
        question=question,
        answer=answer
    )
    db.add(interaction)
    db.commit()
    db.close()
