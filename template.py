import os
from pathlib import Path
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='[%(asctime)s]: %(message)s:')

project_name = "rua_project"

# List of files outlining the project structure
list_of_files = [
    "research/01_wake_word.ipynb",
    "research/02_stt_streaming.ipynb",
    "research/03_llm_routing.ipynb",
    "research/04_tts_precision.ipynb",
    "research/05_integrations.ipynb",
    "src/__init__.py",
    "src/core/__init__.py",
    "src/core/pipeline.py",
    "src/core/logger.py",
    "src/modules/__init__.py",
    "src/modules/ear.py",
    "src/modules/brain.py",
    "src/modules/voice.py",
    "src/modules/hands.py",
    "src/main.py",
    "logs/system.log"
]

for filepath in list_of_files:
    filepath = Path(filepath)
    filedir, filename = os.path.split(filepath)

    # Create directories if they don't exist
    if filedir != "":
        os.makedirs(filedir, exist_ok=True)
        logging.info(f"Creating directory: {filedir} for the file: {filename}")

    # Create empty files if they don't exist or are empty
    if (not os.path.exists(filepath)) or (os.path.getsize(filepath) == 0):
        with open(filepath, "w") as f:
            pass
            logging.info(f"Creating empty file: {filepath}")
    else:
        logging.info(f"{filename} already exists")