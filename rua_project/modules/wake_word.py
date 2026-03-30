# import pyaudio
# import numpy as np
# from openwakeword.model import Model

# def wait_for_wake_word():
#     FORMAT = pyaudio.paInt16
#     CHANNELS = 1
#     RATE = 16000
#     CHUNK = 1280

#     audio = pyaudio.PyAudio()
#     oww_model = Model()
#     mic_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)

#     print("\n💤 RUA is sleeping. Say 'Jarvis' to wake...")
    
#     try:
#         while True:
#             audio_chunk = mic_stream.read(CHUNK, exception_on_overflow=False)
#             audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
#             oww_model.predict(audio_data)
            
#             for mdl in oww_model.prediction_buffer.keys():
#                 if "jarvis" in mdl.lower() and oww_model.prediction_buffer[mdl][-1] > 0.5:
#                     return True # Wake word detected, break the loop
#     finally:
#         # Crucial: Release the mic so the Ear module can use it
#         mic_stream.stop_stream()
#         mic_stream.close()
#         audio.terminate()

import pyaudio
import numpy as np
from openwakeword.model import Model
import time

# Import the new downtime logger
from utils_2 import log_downtime

def wait_for_wake_word():
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 16000
    CHUNK = 1280

    audio = pyaudio.PyAudio()
    
    try:
        oww_model = Model()
        mic_stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE, input=True, frames_per_buffer=CHUNK)
    except Exception as e:
        log_downtime(f"Failed to initialize microphone or Wake Word model: {e}")
        time.sleep(5) # Wait before crashing completely so the main loop can retry
        return False

    print("\n💤 RUA is sleeping. Say 'Jarvis' to wake...")
    
    try:
        while True:
            try:
                # exception_on_overflow=False prevents crashes if the mic gets overwhelmed
                audio_chunk = mic_stream.read(CHUNK, exception_on_overflow=False)
                audio_data = np.frombuffer(audio_chunk, dtype=np.int16)
                oww_model.predict(audio_data)
                
                for mdl in oww_model.prediction_buffer.keys():
                    if "jarvis" in mdl.lower() and oww_model.prediction_buffer[mdl][-1] > 0.5:
                        return True # Wake word detected
                        
            except IOError as e:
                # This catches if the microphone disconnects mid-stream
                log_downtime(f"Microphone stream dropped or overflowed: {e}")
                break 

    finally:
        # Crucial: Release the mic so the Ear module can use it, even if it crashed
        try:
            if mic_stream.is_active():
                mic_stream.stop_stream()
            mic_stream.close()
            audio.terminate()
        except Exception:
            pass # Failsafe cleanup