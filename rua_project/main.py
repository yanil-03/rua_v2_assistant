from utils import LatencyTracker
from modules.wake_word import wait_for_wake_word
from modules.ear import listen_and_transcribe
from modules.brain import think_and_stream
from modules.voice import VoiceManager
from modules.memory import RUACognitiveHub

import warnings
# Suppress the harmless ONNX CPU fallback warning
warnings.filterwarnings("ignore", category=UserWarning, module="onnxruntime")

def main():
    print("🚀 RUA MICROSERVICES PIPELINE ONLINE")
    
    # Initialize Persistent Modules
    rua_brain = RUACognitiveHub()
    voice_manager = VoiceManager()

    while True:
        try:
            # STEP 1: Wait for Wake Word (Blocks until "Jarvis" is heard)
            with LatencyTracker("Wake Word Pipeline"):
                wait_for_wake_word()
            print("\n🔔 Woken up! Ready for command.")

            # STEP 2: Listen & Transcribe
            with LatencyTracker("Ear Pipeline (STT)"):
                user_text = listen_and_transcribe()
            
            if not user_text:
                print("No command heard. Going back to sleep.")
                continue
                
            print(f"\n👤 User: {user_text}")
            print(f"🤖 RUA: ", end="", flush=True)

            # STEP 3 & 4: Brain Processing & Voice Streaming
            with LatencyTracker("Brain + Voice Pipeline (LLM & TTS)"):
                memory_dump = rua_brain.get_brain_dump()
                sentence_buffer = ""
                
                # Stream tokens from LLM
                for chunk in think_and_stream(user_text, memory_dump):
                    sentence_buffer += chunk
                    # Send to voice queue if we hit punctuation
                    if any(p in sentence_buffer for p in [".", "!", "?", "\n"]):
                        voice_manager.speak(sentence_buffer.strip())
                        sentence_buffer = ""
                
                # Catch any remaining text
                if sentence_buffer.strip():
                    voice_manager.speak(sentence_buffer.strip())

                # Wait for RUA to finish speaking before listening for wake word again
                voice_manager.wait_until_done()
                print("\n") # formatting break

        except KeyboardInterrupt:
            print("\n🛑 Shutting down RUA pipeline.")
            break
        except Exception as e:
            print(f"\n❌ Error in pipeline: {e}")

if __name__ == "__main__":
    main()