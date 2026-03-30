# import asyncio
# import edge_tts
# import pygame
# import io
# import threading
# import queue
# import time
# import sys
# import nest_asyncio

# nest_asyncio.apply()
# pygame.mixer.init(frequency=24000)

# class VoiceManager:
#     def __init__(self):
#         self.voice_queue = queue.Queue()
#         self.worker_thread = threading.Thread(target=self._voice_worker, daemon=True)
#         self.worker_thread.start()

#     async def _stream_voice_to_mixer(self, text):
#         communicate = edge_tts.Communicate(text, "en-IN-NeerjaNeural", rate="+15%")
#         audio_data = b""
#         async for chunk in communicate.stream():
#             if chunk["type"] == "audio":
#                 audio_data += chunk["data"]
        
#         if audio_data:
#             sound_file = io.BytesIO(audio_data)
#             pygame.mixer.music.load(sound_file)
#             pygame.mixer.music.play()
            
#             words = text.split()
#             for word in words:
#                 sys.stdout.write(word + " ")
#                 sys.stdout.flush()
#                 time.sleep(0.18)
                
#             while pygame.mixer.music.get_busy():
#                 pygame.time.Clock().tick(60)

#     def _voice_worker(self):
#         loop = asyncio.new_event_loop()
#         asyncio.set_event_loop(loop)
#         while True:
#             text = self.voice_queue.get()
#             if text is None: break
#             loop.run_until_complete(self._stream_voice_to_mixer(text))
#             self.voice_queue.task_done()

#     def speak(self, text):
#         self.voice_queue.put(text)

#     def wait_until_done(self):
#         """Blocks execution until the voice queue is entirely empty and finished playing."""
#         self.voice_queue.join()

import asyncio
import edge_tts
import pygame
import io
import threading
import queue
import time
import sys
import nest_asyncio

nest_asyncio.apply()
pygame.mixer.init(frequency=24000)

class VoiceManager:
    def __init__(self):
        self.text_queue = queue.Queue()
        self.audio_queue = queue.Queue()
        
        # We now use TWO separate threads: one to download, one to play
        threading.Thread(target=self._download_worker, daemon=True).start()
        threading.Thread(target=self._playback_worker, daemon=True).start()

    def _download_worker(self):
        """Worker 1: Constantly downloads audio in the background."""
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while True:
            text = self.text_queue.get()
            if text is None: break
            loop.run_until_complete(self._generate_audio(text))
            self.text_queue.task_done()

    async def _generate_audio(self, text):
        """Fetches the TTS from Microsoft and stores it in the ready-queue."""
        communicate = edge_tts.Communicate(text, "en-IN-NeerjaNeural", rate="+15%")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        if audio_data:
            # Pass the fully downloaded audio buffer AND the text to the playback queue
            self.audio_queue.put((io.BytesIO(audio_data), text))

    def _playback_worker(self):
        """Worker 2: Plays whatever audio is ready without waiting for downloads."""
        while True:
            audio_buffer, text = self.audio_queue.get()
            if audio_buffer is None: break
            
            pygame.mixer.music.load(audio_buffer)
            pygame.mixer.music.play()
            
            # Typewriter effect for terminal
            words = text.split()
            for word in words:
                sys.stdout.write(word + " ")
                sys.stdout.flush()
                time.sleep(0.18)
                
            # Wait for this specific clip to finish playing before starting the next clip
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(60)
                
            self.audio_queue.task_done()

    def speak(self, text):
        self.text_queue.put(text)

    def wait_until_done(self):
        """Blocks until everything is downloaded AND played."""
        self.text_queue.join()
        self.audio_queue.join()