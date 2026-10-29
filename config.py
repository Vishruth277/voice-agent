import os

# Suppress TensorFlow / driver noise
os.environ["TF_CPP_MIN_LOG_LEVEL"] = "3"

# Ollama
OLLAMA_URL = "http://localhost:11434/api/chat"
LLM_MODEL = "llama3.2:1b"

# Audio paths
WAV_OUTPUT_PATH = "/tmp/assistant_voice.wav"
TEMP_MP3_PATH = "/tmp/temp_voice.mp3"

# Audio capture settings
CHUNK = 1024
FORMAT = None          # set in asr.py (pyaudio)
CHANNELS = 1
RATE = 16000
SILENCE_THRESHOLD = 130
PAUSE_LIMIT_SECONDS = 1.5
MAX_RECORD_SECONDS = 20.0

# ASR
WHISPER_MODEL_SIZE = "base"
WHISPER_DEVICE = "cpu"
WHISPER_COMPUTE_TYPE = "int8"

# LLM generation options
LLM_OPTIONS = {
    "num_ctx": 1024,
    "temperature": 0.3,
    "top_p": 0.8,
    "num_predict": 45,
    "num_thread": 4,
}

# History management
MAX_HISTORY_MESSAGES = 7   # system + last 6 turns
