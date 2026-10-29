import time
from tts import speak
from asr import listen
from llm import query
from memory import ConversationMemory
from storage import ChatStorage

# Map Whisper language codes to full language names
LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "bn": "Bengali",
    "ta": "Tamil",
    "te": "Telugu",
    "mr": "Marathi",
    "gu": "Gujarati",
    "kn": "Kannada",
    "ml": "Malayalam",
    "pa": "Punjabi",
    "ur": "Urdu",
}

def main():
    storage = ChatStorage()

    # Calibrate: listen for the user's first input to detect their language
    print("[Calibration]: Please say a few words so I can detect your language...")
    calibrate_text, calibrate_lang = listen()
    language_name = LANGUAGE_NAMES.get(calibrate_lang, "English")
    print(f"[Calibration]: Detected language: {language_name}")

    memory = ConversationMemory(storage=storage, language=language_name)

    speak("Sam assistant engine online.")

    # If calibration captured actual speech, process it as the first input
    if calibrate_text:
        ai_response = query(calibrate_text, memory)
        if ai_response:
            speak(ai_response)

    EXIT_TRIGGERS = ["exit application", "shutdown assistant", "goodbye"]

    while True:
        user_input, detected_lang = listen()

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
