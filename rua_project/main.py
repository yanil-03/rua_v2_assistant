import threading
from utils import LatencyTracker
from modules.wake_word import wait_for_wake_word
from modules.ear import listen_and_transcribe
from modules.brain import think_and_stream, update_long_term_memory
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
    # NEW: Short-term session memory
    session_history = []

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

            # ---> NEW: THE FORGET COMMAND INTERCEPTOR <---
            if "wipe memory" in user_text.lower() or "forget everything" in user_text.lower():
                rua_brain.wipe_memory()
                session_history.clear() # Wipe short-term memory too
                print("🤖 RUA: Memories erased. Starting fresh.")
                voice_manager.speak("My memory has been completely wiped. I am a blank slate.")
                voice_manager.wait_until_done()
                continue # Skip the brain entirely and go back to sleep
            # -----------------------------------------------

            print(f"🤖 RUA: ", end="", flush=True)
                
            print(f"\n👤 User: {user_text}")
            print(f"🤖 RUA: ", end="", flush=True)

            # STEP 3 & 4: Brain Processing & Voice Streaming
            with LatencyTracker("Brain + Voice Pipeline (LLM & TTS)"):
                memory_dump = rua_brain.get_brain_dump(user_text)
                sentence_buffer = ""
                full_rua_response = "" # NEW: Track the whole response for memory
                
                # Pass session_history to the brain
                for chunk in think_and_stream(user_text, memory_dump, session_history):
                    sentence_buffer += chunk
                    full_rua_response += chunk # Accumulate the full answer
                    
                    if any(p in sentence_buffer for p in [".", "!", "?", "\n"]):
                        voice_manager.speak(sentence_buffer.strip())
                        sentence_buffer = ""
                
                if sentence_buffer.strip():
                    voice_manager.speak(sentence_buffer.strip())

                # NEW: Save the interaction to short-term memory
                session_history.append({"role": "user", "content": user_text})
                session_history.append({"role": "assistant", "content": full_rua_response.strip()})
                
                # Keep memory from getting too large (last 10 interactions)
                if len(session_history) > 20: 
                    session_history = session_history[-20:]

                voice_manager.wait_until_done()

                # NEW: Spin up a silent background thread to save long-term facts
                threading.Thread(target=update_long_term_memory, args=(user_text, rua_brain), daemon=True).start()

                print("\n")

        except KeyboardInterrupt:
            print("\n🛑 Shutting down RUA pipeline.")
            break
        except Exception as e:
            print(f"\n❌ Error in pipeline: {e}")

if __name__ == "__main__":
    main()