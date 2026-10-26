import os
import asyncio
import edge_tts
from config import TEMP_MP3_PATH

# ====================== BEST NATURAL VOICES ======================
# Try these one by one (most natural first):
VOICE = "en-IN-NeerjaNeural"      # Female Indian English - usually the best
# VOICE = "en-IN-PrabhatNeural"   # Male Indian English
# VOICE = "en-US-JennyNeural"     # Very natural American female
# VOICE = "en-US-AriaNeural"      # Soft & natural
# VOICE = "en-GB-SoniaNeural"     # British female
# ================================================================

async def _generate_speech(text: str, output_file: str):
    communicate = edge_tts.Communicate(
        text,
        VOICE,
        rate="+0%",      # normal speed
        pitch="+0Hz"     # normal pitch
    )
    await communicate.save(output_file)

def speak(text: str):
    print(f"\n[AI Assistant]: {text}")

    if os.path.exists(TEMP_MP3_PATH):
        try:
            os.remove(TEMP_MP3_PATH)
        except:
            pass

    try:
        # Generate natural speech
        asyncio.run(_generate_speech(text, TEMP_MP3_PATH))

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
