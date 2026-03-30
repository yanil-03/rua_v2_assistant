import time
import os
from datetime import datetime

LATENCY_LOG_FILE = "rua_performance_logs.csv"
DOWNTIME_LOG_FILE = "rua_downtime.log"

class LatencyTracker:
    def __init__(self, step_name):
        self.step_name = step_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.time()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        end_time = time.time()
        latency = end_time - self.start_time
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Determine if the step crashed
        status = "ERROR" if exc_type else "SUCCESS"
        
        # Create CSV headers if the file doesn't exist yet
        if not os.path.exists(LATENCY_LOG_FILE):
            with open(LATENCY_LOG_FILE, "w", encoding="utf-8") as f:
                f.write("Timestamp,Pipeline_Step,Latency_Seconds,Status\n")
        
        # Append the metric to the CSV
        with open(LATENCY_LOG_FILE, "a", encoding="utf-8") as f:
            f.write(f"{timestamp},{self.step_name},{latency:.4f},{status}\n")

def log_downtime(reason):
    """Call this when RUA's ears fail to log exactly when it went deaf."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    error_msg = f"[{timestamp}] 🔴 RUA WAKE WORD OFFLINE: {reason}"
    
    print(f"\n{error_msg}")
    with open(DOWNTIME_LOG_FILE, "a", encoding="utf-8") as f:
        f.write(error_msg + "\n")