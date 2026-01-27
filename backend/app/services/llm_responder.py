import os
from openai import OpenAI
from app.llm.system_prompt import build_system_prompt

client = OpenAI()

def generate_llm_reply(message: str, history: list[str] | None = None) -> str:
    """
    message: current user message
    history: list of previous messages in the session (optional)
    """

    system_prompt = build_system_prompt()

    messages = [
        {"role": "system", "content": system_prompt}
    ]

    # Add chat history if available
    if history:
        for h in history:
            messages.append(h)

    # Add current user message
    messages.append({"role": "user", "content": message})

    try:
        response = client.chat.completions.create(
            model="gpt-5-mini",
            messages=messages,
            temperature=0.2,     # factual, not creative
            max_tokens=300,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("LLM error:", e)
        return (
            "I’m having trouble answering that right now. "
            "Please try again in a moment."
        )
