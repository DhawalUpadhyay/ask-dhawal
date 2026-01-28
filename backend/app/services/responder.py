from backend.app.data.resume import RESUME_DATA

def generate_reply(message: str) -> str:
    msg = message.lower()

    if "experience" in msg:
        return RESUME_DATA["summary"]

    if "skills" in msg or "tech stack" in msg:
        skills = RESUME_DATA["skills"]
        return (
            f"Backend: {', '.join(skills['backend'])}. "
            f"Frontend: {', '.join(skills['frontend'])}. "
            f"Databases: {', '.join(skills['databases'])}."
        )

    if "current" in msg or "working" in msg:
        return (
            f"I am currently working as a {RESUME_DATA['title']} "
            f"at {RESUME_DATA['current_company']}."
        )

    return (
        "I can answer questions about my experience, skills, "
        "projects, and current role. Please ask something specific."
    )
