import os
import json
from datetime import datetime, timedelta

# Import RUA's memory hub
try:
    from modules.memory import RUACognitiveHub
except ImportError as e:
    print(f"❌ Could not import RUACognitiveHub. Ensure this is run from the root directory. Error: {e}")
    exit(1)

# Define paths matching your memory.py
MEMORY_DIR = "rua_memory"
CONVO_DIR = os.path.join(MEMORY_DIR, "conversation_data")
REPORT_FILE = "test_memory_retention_report.txt"

def log(msg, write_to_file=True):
    """Prints to console and appends to the report file."""
    print(msg)
    if write_to_file:
        with open(REPORT_FILE, "a", encoding="utf-8") as f:
            f.write(msg + "\n")

def run_retention_test():
    # Initialize Report
    with open(REPORT_FILE, "w", encoding="utf-8") as f:
        f.write(f"🧠 RUA MEMORY RETENTION & PRUNING TEST - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write("="*70 + "\n\n")

    os.makedirs(CONVO_DIR, exist_ok=True)
    today = datetime.now().date()

    # Define our test timeline
    test_timeline = [
        {"days_ago": 10, "should_delete": True},
        {"days_ago": 8,  "should_delete": True},
        {"days_ago": 7,  "should_delete": False}, # Exactly 7 days is the edge case, should be kept
        {"days_ago": 5,  "should_delete": False},
        {"days_ago": 1,  "should_delete": False},
        {"days_ago": 0,  "should_delete": False}  # Today
    ]

    log("▶️ STEP 1: Injecting Simulated Time-Travel Data into RUA's Memory...")
    created_files = []
    
    for item in test_timeline:
        past_date = today - timedelta(days=item["days_ago"])
        date_str = past_date.strftime("%Y-%m-%d")
        file_path = os.path.join(CONVO_DIR, f"{date_str}.json")
        
        # Create a fake conversation for that specific day
        dummy_data = [{
            "time": f"{date_str}T14:30:00",
            "user": f"Simulated user message from {item['days_ago']} days ago.",
            "rua": f"Simulated RUA response from {item['days_ago']} days ago."
        }]
        
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(dummy_data, f, indent=4)
            
        created_files.append((date_str, item["days_ago"], item["should_delete"]))
        log(f"  -> Generated: {date_str}.json (Age: {item['days_ago']} days)")

    log("\n▶️ STEP 2: Waking up Cognitive Hub (Triggers auto-prune)...")
    # Initializing this class automatically runs self.prune_episodes(days=7)
    hub = RUACognitiveHub()

    log("\n▶️ STEP 3: Verifying Pruning Accuracy...")
    remaining_files = os.listdir(CONVO_DIR)
    
    for date_str, age, should_delete in created_files:
        file_name = f"{date_str}.json"
        is_deleted = file_name not in remaining_files
        
        if should_delete and is_deleted:
            log(f"  ✅ SUCCESS: {file_name} (Age: {age} days) was successfully DELETED.")
        elif not should_delete and not is_deleted:
            log(f"  ✅ SUCCESS: {file_name} (Age: {age} days) was properly RETAINED.")
        else:
            state = "DELETED" if is_deleted else "RETAINED"
            log(f"  ❌ FAILED: {file_name} (Age: {age} days) was incorrectly {state}!")

    log("\n▶️ STEP 4: Verifying Data Extraction (get_brain_dump)...")
    dump = hub.get_brain_dump()
    
    log(f"  -> Raw Dump Output:\n     {dump}\n")
    
    # Check if the oldest deleted file leaked into the dump
    oldest_deleted_date = (today - timedelta(days=10)).strftime("%Y-%m-%d")
    if f"from 10 days ago" in dump:
        log("  ❌ FAILED: Dump contains data from a file that should have been deleted!")
    elif f"from 0 days ago" in dump:
        log("  ✅ SUCCESS: Brain dump successfully extracted history from valid recent files, ignoring old ones.")
    else:
        log("  ⚠️ WARNING: Brain dump did not contain today's expected history. Check 'get_brain_dump' logic.")

    log("\n" + "="*70)
    log(f"🏁 MEMORY RETENTION TEST COMPLETE. Report saved to {REPORT_FILE}")

if __name__ == "__main__":
    run_retention_test()