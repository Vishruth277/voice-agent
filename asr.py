import pyaudio
import numpy as np
from faster_whisper import WhisperModel
from config import (
    CHUNK, CHANNELS, RATE,
    SILENCE_THRESHOLD, PAUSE_LIMIT_SECONDS, MAX_RECORD_SECONDS,
    WHISPER_MODEL_SIZE, WHISPER_DEVICE, WHISPER_COMPUTE_TYPE
)

print("-> Loading Local Speech Engine (Faster-Whisper Tiny with Native VAD)...")
asr_model = WhisperModel(
    WHISPER_MODEL_SIZE,
    device=WHISPER_DEVICE,
    compute_type=WHISPER_COMPUTE_TYPE
)

def listen() -> str:
    """
    Capture speech from the microphone.
    Supports short pauses and stops after sustained silence or max duration.
    """
    p = pyaudio.PyAudio()
    FORMAT = pyaudio.paInt16

    try:
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
    except Exception as e:
        print(f"\n[ERROR] Could not access your microphone: {e}")
        p.terminate()
        return ""

    stream.start_stream()
    print("\n[Status]: Listening... Speak now (You can take pauses).")

    frames = []
    has_spoken = False
    silent_chunks = 0

    max_silent_chunks = int(PAUSE_LIMIT_SECONDS * RATE / CHUNK)
    max_total_chunks = int(MAX_RECORD_SECONDS * RATE / CHUNK)

    while len(frames) < max_total_chunks:
        data = stream.read(CHUNK, exception_on_overflow=False)
        frames.append(data)

        audio_data = np.frombuffer(data, dtype=np.int16)
        amplitude = np.std(audio_data) if len(audio_data) > 0 else 0

        if amplitude > SILENCE_THRESHOLD:
            if not has_spoken:
                print("[Status]: Recording speech...")
            has_spoken = True
            silent_chunks = 0
        else:
            if has_spoken:
                silent_chunks += 1

        if has_spoken and silent_chunks > max_silent_chunks:
            break

    stream.stop_stream()
    stream.close()
    p.terminate()

    if not has_spoken:
        print("[Status]: No speech detected.")
        return ""

    print("[Status]: Filtering noise and processing speech...")
    raw_audio = b"".join(frames)
    audio_np = np.frombuffer(raw_audio, dtype=np.int16).astype(np.float32) / 32768.0

    segments, _ = asr_model.transcribe(
        audio_np,
        beam_size=2,
        vad_filter=True,
        vad_parameters=dict(
            min_speech_duration_ms=200,
            max_speech_duration_s=20
        )
    )

    user_text = "".join(segment.text for segment in segments).strip()
    print(f"[You Said]: {user_text}")
    return user_text
