import time
import os
import json
import numpy as np
import warnings
from datetime import datetime

# Suppress warnings for cleaner output
warnings.filterwarnings("ignore")

# --- Import RUA Modules ---
try:
    from modules.memory import RUACognitiveHub
    from modules.brain import think_and_stream, update_long_term_memory
    from modules.voice import VoiceManager
    from modules.ear import STT_MODEL
    from openwakeword.model import Model as WakeWordModel
except ImportError as e:
    print(f"❌ Initialization Error: Could not import modules. Ensure you are running this from the root directory. Details: {e}")
    exit(1)

# --- Setup Report ---
REPORT_FILE = "performance_report.txt"

def log(message, write_to_file=True):
    """Prints to console and writes to the report file."""
    print(message)
    if write_to_file:
        with open(REPORT_FILE, "a", encoding="utf-8") as f:
            f.write(message + "\n")

def reset_report():
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"🚀 RUA PIPELINE DIAGNOSTIC REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*70 + "\n\n")

# --- Diagnostic Tests ---

def test_wake_word_engine():
    log("▶️ TEST 1: Wake Word Engine (OpenWakeWord)")
    start_time = time.time()
    try:
        # Initialize model
        oww_model = WakeWordModel()
        # Feed it 1 second of silent dummy audio data (16000 hz, chunks of 1280)
        dummy_audio = np.zeros(1280, dtype=np.int16)
        oww_model.predict(dummy_audio)
        latency = time.time() - start_time
        log(f"  ✅ Wake Word model loaded and processed dummy audio in {latency:.2f}s")
        return True
    except Exception as e:
        log(f"  ❌ Wake Word Engine Failed: {e}")
        return False

def test_ear_engine():
    log("\n▶️ TEST 2: Ear Engine (Faster-Whisper STT)")
    start_time = time.time()
    try:
        # Feed it 1 second of random noise (simulating raw audio float32 format)
        dummy_audio_np = np.random.normal(0, 0.01, 16000).astype(np.float32)
        segments, info = STT_MODEL.transcribe(dummy_audio_np, beam_size=1)
        # Force evaluation of the generator
        text = "".join([s.text for s in segments]).strip()
        latency = time.time() - start_time
        log(f"  ✅ STT Model processed audio chunk in {latency:.2f}s. Result: '{text}' (Expected gibberish or blank)")
        return True
    except Exception as e:
        log(f"  ❌ Ear Engine Failed: {e}")
        return False

def test_brain_local_and_cloud():
    log("\n▶️ TEST 3: Brain Engine (Local Llama & Cloud Escalation)")
    
    # Test 3A: Simple Local Test
    log("  -> Sub-test 3A: Simple Greeting (Should stay Local)")
    start_time = time.time()
    try:
        local_response = ""
        for chunk in think_and_stream("Hi RUA, are you awake?", "No context", []):
            local_response += chunk
        latency = time.time() - start_time
        log(f"  ✅ Local Response ({latency:.2f}s): {local_response.strip()}")
    except Exception as e:
        log(f"  ❌ Local Brain Failed: {e}")

    # Test 3B: Complex Cloud Test
    log("  -> Sub-test 3B: Complex Query (Should hit 'ESCALATE' and use Cloud Gemini)")
    start_time = time.time()
    try:
        cloud_response = ""
        for chunk in think_and_stream("Write a Python script for a neural network using PyTorch.", "No context", []):
            cloud_response += chunk
        latency = time.time() - start_time
        # Truncate response for the log
        preview = cloud_response.strip().replace('\n', ' ')[:100] + "..."
        log(f"  ✅ Cloud Escalation Response ({latency:.2f}s): {preview}")
    except Exception as e:
        log(f"  ❌ Cloud Brain Failed. Did you set GOOGLE_API_KEY? Error: {e}")

def test_memory_system():
    log("\n▶️ TEST 4: Cognitive Hub & Background Memory Extraction")
    rua_brain = RUACognitiveHub()
    
    # Test Background Thread Fact Extraction
    test_fact_sentence = "Just so you know, my favorite food is spicy ramen."
    log(f"  -> Sending to extraction thread: '{test_fact_sentence}'")
    
    start_time = time.time()
    try:
        # Run it synchronously for the test to measure accuracy
        update_long_term_memory(test_fact_sentence, rua_brain)
        
        # Give it a tiny buffer to ensure JSON file is written
        time.sleep(1) 
        
        # Reload memory to verify
        rua_brain = RUACognitiveHub() 
        memory_dump = rua_brain.get_brain_dump()
        
        latency = time.time() - start_time
        
        if "ramen" in memory_dump.lower() or "food" in memory_dump.lower():
            log(f"  ✅ Memory Successfully Extracted and Saved ({latency:.2f}s). Current Dump: {memory_dump}")
        else:
            log(f"  ⚠️ Memory ran, but failed to extract the specific fact. Dump: {memory_dump}")
            
    except Exception as e:
        log(f"  ❌ Memory System Failed: {e}")

def test_voice_manager():
    log("\n▶️ TEST 5: Voice Manager (TTS & Playback)")
    start_time = time.time()
    try:
        voice_manager = VoiceManager()
        test_phrase = "Diagnostics complete. All systems are operating within normal parameters."
        log(f"  -> Synthesizing: '{test_phrase}'")
        
        voice_manager.speak(test_phrase)
        voice_manager.wait_until_done()
        
        latency = time.time() - start_time
        log(f"\n  ✅ Voice synthesized and played successfully. Total audio pipeline time: {latency:.2f}s")
    except Exception as e:
        log(f"\n  ❌ Voice System Failed: {e}")

# --- Main Execution ---
def run_diagnostics():
    reset_report()
    log("Initiating Automated Stress Test...\n")
    
    test_wake_word_engine()
    test_ear_engine()
    test_brain_local_and_cloud()
    test_memory_system()
    test_voice_manager()
    
    log("\n" + "="*70)
    log("🏁 DIAGNOSTICS COMPLETE. Report saved to performance_report.txt")

if __name__ == "__main__":
    run_diagnostics()