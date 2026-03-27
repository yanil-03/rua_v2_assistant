import json
import os
from datetime import datetime

MEMORY_FILE = "rua_memory.json"

class RUACognitiveHub:
    def __init__(self, storage_path: str = MEMORY_FILE):
        self.storage_path = storage_path
        self.memory = self._load_from_disk()
        self.working_memory = {"buffer": {}, "last_search": None}

    def _load_from_disk(self):
        if os.path.exists(self.storage_path):
            with open(self.storage_path, "r") as f:
                return json.load(f)
        return {"critical_info": {}, "semantic_memory": {}, "episodic_memory": [], "created_at": datetime.now().strftime("%Y-%m-%d")}

    def save_to_disk(self):
        with open(self.storage_path, "w") as f:
            json.dump(self.memory, f, indent=4)

    def get_brain_dump(self) -> str:
        dump = "RUA Memory Dump: "
        if self.memory.get('critical_info'): dump += f"CRITICAL: {self.memory['critical_info']}. "
        if self.memory.get('semantic_memory'): dump += f"FACTS: {self.memory['semantic_memory']}. "
        if self.working_memory.get('buffer'): dump += f"ACTIVE TASK: {self.working_memory['buffer']}. "
        return dump