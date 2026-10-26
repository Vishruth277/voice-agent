import requests
from config import OLLAMA_URL, LLM_MODEL, LLM_OPTIONS
from memory import ConversationMemory

def query(user_message: str, memory: ConversationMemory) -> str:
    """Send the conversation history to Ollama and return the assistant reply."""
    if not user_message.strip():
        return ""

    memory.add_user(user_message)

    payload = {
        "model": LLM_MODEL,
        "messages": memory.get_messages(),
        "stream": False,
        "options": LLM_OPTIONS,
    }

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=15)
        response.raise_for_status()
        ai_reply = response.json().get("message", {}).get("content", "").strip()
        memory.add_assistant(ai_reply)
        return ai_reply
    except Exception:
        return "System error: I cannot reach my local server window."
