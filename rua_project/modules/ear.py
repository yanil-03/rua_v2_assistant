import speech_recognition as sr
import numpy as np
from faster_whisper import WhisperModel

# Initialize models globally so they don't reload every time
STT_MODEL = WhisperModel("tiny.en", device="cpu", compute_type="int8")
recognizer = sr.Recognizer()
recognizer.pause_threshold = 0.2 
recognizer.non_speaking_duration = 0.1

def listen_and_transcribe():
    with sr.Microphone(sample_rate=16000) as source:
        recognizer.adjust_for_ambient_noise(source, duration=0.2)
        print("👂 Listening for command...", end="", flush=True)
        
        try:
            audio = recognizer.listen(source, timeout=5, phrase_time_limit=8)
            audio_np = np.frombuffer(audio.get_raw_data(), dtype=np.int16).astype(np.float32) / 32768.0
            segments, _ = STT_MODEL.transcribe(audio_np, beam_size=1)
            text = "".join([s.text for s in segments]).strip()
            return text
        except sr.WaitTimeoutError:
            print("\nTimed out waiting for command.")
            return ""