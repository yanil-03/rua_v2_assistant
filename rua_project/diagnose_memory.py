import os
import time
from datetime import datetime, timedelta
from modules.memory import RUACognitiveHub

def run_memory_diagnosis():
    print("🧠 RUA MEMORY SYSTEM DIAGNOSTIC")
    print("="*40)
    
    start_time = time.perf_counter()
    
    # 1. Initialization Test
    try:
        hub = RUACognitiveHub()
        print("✅ Hub Initialization: SUCCESS")
    except Exception as e:
        print(f"❌ Hub Initialization: FAILED ({e})")
        return

    # 2. Directory Structure Check
    mem_dir = "rua_memory"
    convo_dir = os.path.join(mem_dir, "conversation_data")
    
    dirs_ok = os.path.exists(mem_dir) and os.path.exists(convo_dir)
    print(f"{'✅' if dirs_ok else '❌'} Folder Structure: {'Verified' if dirs_ok else 'Missing'}")

    # 3. Permanent Fact Test
    test_key = f"test_fact_{int(time.time())}"
    hub.learn_fact(test_key, "Diagnostic test successful")
    
    with open(os.path.join(mem_dir, "user_data.json"), "r") as f:
        user_data = f.read()
        fact_saved = test_key in user_data
    print(f"{'✅' if fact_saved else '❌'} User Data Persistence: {'Saved' if fact_saved else 'Failed'}")

    # 4. 7-Day Pruning & Multi-File Test
    print("\n⏳ Testing 7-Day Rolling Logic...")
    
    # Create a "fake" old file (8 days ago)
    old_date = (datetime.now() - timedelta(days=8)).strftime("%Y-%m-%d")
    old_file_path = os.path.join(convo_dir, f"{old_date}.json")
    with open(old_file_path, "w") as f:
        f.write("[]")
    
    # Create today's file
    hub.add_episode("Diagnostic Query", "Diagnostic Response")
    
    # Trigger pruning
    hub.prune_episodes(days=7)
    
    old_file_exists = os.path.exists(old_file_path)
    today_file_exists = os.path.exists(os.path.join(convo_dir, f"{datetime.now().strftime('%Y-%m-%d')}.json"))
    
    if not old_file_exists and today_file_exists:
        print("✅ 7-Day Pruning: SUCCESS (Old file deleted, New file kept)")
    else:
        print(f"❌ 7-Day Pruning: FAILED (Old file exists: {old_file_exists})")

    # 5. Performance Metrics
    end_time = time.perf_counter()
    load_start = time.perf_counter()
    dump = hub.get_brain_dump()
    load_end = time.perf_counter()
    
    total_latency = end_time - start_time
    retrieval_latency = load_end - load_start

    print("\n📊 PERFORMANCE REPORT")
    print("-" * 20)
    print(f"Total Diagnostic Run:    {total_latency:.4f}s")
    print(f"Context Retrieval Speed: {retrieval_latency:.4f}s")
    print(f"Memory Directory Size:   {get_dir_size(mem_dir):.2f} KB")
    print("-" * 20)
    
    print("\n💡 Brain Dump Preview (What RUA sees):")
    print(f"> {dump[:150]}...")
    print("="*40)

def get_dir_size(path='.'):
    total = 0
    with os.scandir(path) as it:
        for entry in it:
            if entry.is_file():
                total += entry.stat().st_size
            elif entry.is_dir():
                total += get_dir_size(entry.path)
    return total / 1024

if __name__ == "__main__":
    run_memory_diagnosis()