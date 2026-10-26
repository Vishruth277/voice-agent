import time
from tts import speak
from asr import listen
from llm import query
from memory import ConversationMemory
from storage import ChatStorage

def main():
    storage = ChatStorage()
    memory = ConversationMemory(storage=storage)

    speak("Voice assistant engine online.")

    EXIT_TRIGGERS = ["exit application", "shutdown assistant", "goodbye"]

    while True:
        user_input = listen()

        if user_input:
            lower = user_input.lower()

            if any(trigger in lower for trigger in EXIT_TRIGGERS):
                speak("Exiting assistant pipeline. Goodbye.")
                
                # Optional: Show what was stored when exiting
                print("\n----- Chat History (from .pkl) -----")
                storage.show_pkl()
                print("------------------------------------\n")
                
                break

            ai_response = query(user_input, memory)
            if ai_response:
                speak(ai_response)

        time.sleep(0.2)

if __name__ == "__main__":
    main()
