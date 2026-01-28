from sqlalchemy.orm import Session
from backend.app.db.models import Interaction

def log_interaction(session_id: str, question: str, answer: str, db: Session):
    interaction = Interaction(
        session_id=session_id,
        question=question,
        answer=answer
    )
    db.add(interaction)
    db.commit()

def get_chat_history(session_id: str, db: Session, limit: int = 6):
    """
    Returns last N interactions as OpenAI-compatible messages
    """
    rows = (
        db.query(Interaction)
        .filter(Interaction.session_id == session_id)
        .order_by(Interaction.created_at.desc())
        .limit(limit)
        .all()
    )
    history = []

    # reverse so oldest comes first
    for row in reversed(rows):
        history.append({"role": "user", "content": row.question})
        history.append({"role": "assistant", "content": row.answer})

    return history