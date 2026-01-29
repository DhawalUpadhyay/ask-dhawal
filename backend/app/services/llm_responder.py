import os
from openai import OpenAI
from backend.app.llm.system_prompt import build_system_prompt
from dotenv import load_dotenv
load_dotenv()

client = OpenAI()

def rephrase_msg(message: str) -> str:
    """
    Rephrase the user message to be more polite and formal.
    """
    system_prompt = (
        "You are a helpful assistant that rephrases user messages "
        "to be more polite and formal."
        "return the rephrased message only."
    )

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": message}
    ]

    model_name = os.getenv("OPENAI_MODEL", "gpt-5-mini")
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.8,
        )
        return response.choices[0].message.content.strip()

    except Exception as e:
        print("LLM error:", e, "\nModel:", model_name)
        return message  # Fallback to original message on error

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
    model_name = os.getenv("OPENAI_MODEL", "gpt-5-nano")
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.2,
            max_tokens=300,
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print("LLM error:", e, "\nModel:", model_name)
        return (
            "I’m having trouble answering that right now. "
            "Please try again in a moment."
        )
