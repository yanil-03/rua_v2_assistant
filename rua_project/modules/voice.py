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
        self.voice_queue = queue.Queue()
        self.worker_thread = threading.Thread(target=self._voice_worker, daemon=True)
        self.worker_thread.start()

    async def _stream_voice_to_mixer(self, text):
        communicate = edge_tts.Communicate(text, "en-IN-NeerjaNeural", rate="+15%")
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        if audio_data:
            sound_file = io.BytesIO(audio_data)
            pygame.mixer.music.load(sound_file)
            pygame.mixer.music.play()
            
            words = text.split()
            for word in words:
                sys.stdout.write(word + " ")
                sys.stdout.flush()
                time.sleep(0.18)
                
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(60)

    def _voice_worker(self):
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        while True:
            text = self.voice_queue.get()
            if text is None: break
            loop.run_until_complete(self._stream_voice_to_mixer(text))
            self.voice_queue.task_done()

    def speak(self, text):
        self.voice_queue.put(text)

    def wait_until_done(self):
        """Blocks execution until the voice queue is entirely empty and finished playing."""
        self.voice_queue.join()