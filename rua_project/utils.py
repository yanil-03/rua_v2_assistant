import time
import logging

# Configure basic logging for the tracker
logging.basicConfig(level=logging.INFO, format='%(asctime)s - ⏱️ %(message)s', datefmt='%H:%M:%S')

class LatencyTracker:
    def __init__(self, step_name):
        self.step_name = step_name
        self.start_time = None

    def __enter__(self):
        self.start_time = time.perf_counter()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.perf_counter() - self.start_time
        logging.info(f"[{self.step_name}] completed in {elapsed:.4f} seconds.")