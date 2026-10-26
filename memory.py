from config import MAX_HISTORY_MESSAGES
from storage import ChatStorage

class ConversationMemory:
    def __init__(self, storage: ChatStorage = None, session_id: str = None):
        self.storage = storage or ChatStorage()
        self.session_id = session_id or self.storage.create_session()

        # Load previous messages from Chroma
        self.history = self.storage.get_session_messages(self.session_id)

        # Add system prompt if this is a new session
        if not self.history or self.history[0]["role"] != "system":
            system_msg = {
                "role": "system",
                "content": (
                    "You are a helpful, professional corporate voice assistant appliance. "
                    "The user input comes from a live microphone speech decoder. Ignore minor typos. "
                    "Crucial: Remember details, contexts, and names mentioned earlier in the chat "
                    "to hold a continuous conversation. "
                    "Keep your responses friendly, brief, and under two sentences."
                ),
            }
            self.history.insert(0, system_msg)
            self.storage.add_message(self.session_id, "system", system_msg["content"])

    def add_user(self, text: str):
        if text.strip():
            self.history.append({"role": "user", "content": text})
            self.storage.add_message(self.session_id, "user", text)
            self._trim()

    def add_assistant(self, text: str):
        if text.strip():
            self.history.append({"role": "assistant", "content": text})
            self.storage.add_message(self.session_id, "assistant", text)
            self._trim()

    def get_messages(self):
        return self.history

    def _trim(self):
        if len(self.history) > MAX_HISTORY_MESSAGES:
            system = self.history[0]
            self.history = [system] + self.history[-(MAX_HISTORY_MESSAGES - 1):]
