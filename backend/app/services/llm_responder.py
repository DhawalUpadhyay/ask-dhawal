import os
from typing import Generator
from openai import OpenAI
from backend.app.llm.system_prompt import build_system_prompt
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()
DEFAULT_MODEL = "gpt-4o-mini"


def generate_llm_reply(message: str, history: list | None = None) -> str:
    """Non-streaming reply — used for short-circuit responses (e.g. greetings)."""
    system_prompt = build_system_prompt()
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})

    model_name = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
    try:
        response = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.2,
            max_tokens=300,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print("LLM error:", e)
        return "I'm having trouble answering that right now. Please try again."


def generate_llm_stream(
    message: str, history: list | None = None
) -> Generator[str, None, None]:
    """Streaming reply — yields text tokens one by one."""
    system_prompt = build_system_prompt()
    messages = [{"role": "system", "content": system_prompt}]
    if history:
        messages.extend(history)
    messages.append({"role": "user", "content": message})

    model_name = os.getenv("OPENAI_MODEL", DEFAULT_MODEL)
    try:
        stream = client.chat.completions.create(
            model=model_name,
            messages=messages,
            temperature=0.2,
            max_tokens=300,
            stream=True,
        )
        for chunk in stream:
            content = chunk.choices[0].delta.content
            if content:
                yield content
    except Exception as e:
        print("LLM stream error:", e)
        yield "I'm having trouble answering that right now. Please try again."
