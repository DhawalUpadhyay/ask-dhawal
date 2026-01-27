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

def get_chat_history(session_id: str, limit: int = 6):
    """
    Returns last N interactions as OpenAI-compatible messages
    """
    db = SessionLocal()

    rows = (
        db.query(Interaction)
        .filter(Interaction.session_id == session_id)
        .order_by(Interaction.created_at.desc())
        .limit(limit)
        .all()
    )

    db.close()

    history = []

    # reverse so oldest comes first
    for row in reversed(rows):
        history.append({"role": "user", "content": row.question})
        history.append({"role": "assistant", "content": row.answer})

    return history