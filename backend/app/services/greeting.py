def is_greeting(message: str) -> bool:
    greetings = {
        "hi", "hello", "hey", "hii", "hiya",
        "good morning", "good afternoon", "good evening"
    }

    msg = message.lower().strip()
    return msg in greetings or msg.startswith(tuple(greetings))

def greeting_response() -> str:
    return "Hi 👋 I’m Dhawal’s AI resume. I am here to help you learn more about my experience and skills."