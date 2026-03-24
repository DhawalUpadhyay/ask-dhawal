import os
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parents[3] / ".env")

client = OpenAI()
_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def generate_summary(messages: list) -> str:
    if not messages:
        return "No messages were exchanged."

    transcript = "\n".join(
        f"{'Recruiter' if m['role'] == 'user' else 'Dhawal'}: {m['content']}"
        for m in messages
    )

    try:
        response = client.chat.completions.create(
            model=_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You summarise recruiter conversations with an AI resume chatbot. "
                        "Write 3-4 sentences covering: what the recruiter asked about, "
                        "what was discussed, and any notable points. Be concise and factual. "
                        "If the conversation was just a greeting or had no meaningful content, "
                        "explicitly state that — e.g. 'The recruiter logged in but did not ask any substantive questions.'"
                    ),
                },
                {"role": "user", "content": f"Summarise this conversation:\n\n{transcript}"},
            ],
            temperature=0.2,
            max_tokens=200,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"Summary generation error: {e}")
        return "Summary could not be generated."
