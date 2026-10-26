import os
from gtts import gTTS
from config import WAV_OUTPUT_PATH, TEMP_MP3_PATH

def speak(text: str):
    """Convert text to speech and play it through the system speakers."""
    print(f"\n[AI Assistant]: {text}")

    # Clean previous file
    if os.path.exists(WAV_OUTPUT_PATH):
        try:
            os.remove(WAV_OUTPUT_PATH)
        except Exception:
            pass

    try:
        # 1. Generate MP3 with Indian English accent
        tts = gTTS(text=text, lang="en", tld="co.in", slow=False)
        tts.save(TEMP_MP3_PATH)

        # 2. Convert to WAV (16 kHz mono PCM)
        os.system(
            f"ffmpeg -y -i {TEMP_MP3_PATH} -acodec pcm_s16le -ac 1 -ar 16000 "
            f"{WAV_OUTPUT_PATH} > /dev/null 2>&1"
        )

        if os.path.exists(TEMP_MP3_PATH):
            os.remove(TEMP_MP3_PATH)

        # 3. Play with PulseAudio, fall back to ALSA
        exit_status = os.system(f"paplay {WAV_OUTPUT_PATH} > /dev/null 2>&1")
        if exit_status != 0:
            os.system(f"aplay {WAV_OUTPUT_PATH} > /dev/null 2>&1")

    except Exception as e:
        print(f"[Audio System Notification]: Core audio routing failed: {e}")
        # Last-resort fallback
        clean = text.replace('"', '\\"').replace("'", "\\'")
        os.system(f'spd-say "{clean}"')
