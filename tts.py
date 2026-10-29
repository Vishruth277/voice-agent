import os
import asyncio
import edge_tts
from langdetect import detect, DetectorFactory
from config import TEMP_MP3_PATH

# Seed for consistent results
DetectorFactory.seed = 0

# ====================== BEST NATURAL VOICES ======================
# Indian language voice mapping
LANGUAGE_VOICES = {
    "en": "en-IN-NeerjaNeural",      # Indian English female
    "hi": "hi-IN-SwaraNeural",       # Hindi female
    "bn": "bn-IN-TanishaaNeural",    # Bengali (Indian) female
    "ta": "ta-IN-PallaviNeural",     # Tamil female
    "te": "te-IN-ShrutiNeural",      # Telugu female
    "mr": "mr-IN-AarohiNeural",      # Marathi female
    "gu": "gu-IN-AarohiNeural",      # Gujarati female
    "kn": "kn-IN-SapnaNeural",       # Kannada female
    "ml": "ml-IN-SobhanaNeural",     # Malayalam female
    "pa": "pa-IN-SimarNeural",       # Punjabi female
    "ur": "ur-IN-GulNeural",         # Urdu female
}

DEFAULT_VOICE = "en-IN-NeerjaNeural"
# ================================================================

def detect_language(text: str) -> str:
    """Detect language from the response text using langdetect."""
    try:
        lang = detect(text)
        # Map to Indian language voice if available, else default to English
        if lang in LANGUAGE_VOICES:
            return lang
        return "en"
    except:
        return "en"

async def _generate_speech(text: str, output_file: str, voice: str):
    communicate = edge_tts.Communicate(
        text,
        voice,
        rate="+0%",      # normal speed
        pitch="+0Hz"     # normal pitch
    )
    await communicate.save(output_file)

def speak(text: str, lang: str = None):
    print(f"\n[AI Assistant]: {text}")

    # Detect language from the response text itself
    detected = detect_language(text)
    voice = LANGUAGE_VOICES.get(detected, DEFAULT_VOICE)
    print(f"[TTS Voice]: {voice} (detected: {detected})")

    if os.path.exists(TEMP_MP3_PATH):
        try:
            os.remove(TEMP_MP3_PATH)
        except:
            pass

    try:
        # Generate natural speech
        asyncio.run(_generate_speech(text, TEMP_MP3_PATH, voice))

        # Play directly with highest quality (no conversion)
        # Try different players in order
        players = [
            f'ffplay -nodisp -autoexit -loglevel quiet "{TEMP_MP3_PATH}"',
            f'mpv --no-video --really-quiet "{TEMP_MP3_PATH}"',
            f'paplay "{TEMP_MP3_PATH}"',
            f'aplay "{TEMP_MP3_PATH}"'
        ]

        played = False
        for cmd in players:
            if os.system(cmd + " > /dev/null 2>&1") == 0:
                played = True
                break

        if not played:
            print("[Warning] Could not play audio. Install ffplay or mpv.")

    except Exception as e:
        print(f"[TTS Error]: {e}")
