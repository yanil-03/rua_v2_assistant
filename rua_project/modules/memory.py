# import json
# import os
# from datetime import datetime

# MEMORY_FILE = "rua_memory.json"

# class RUACognitiveHub:
#     def __init__(self, storage_path: str = MEMORY_FILE):
#         self.storage_path = storage_path
#         self.memory = self._load_from_disk()
#         self.working_memory = {"buffer": {}, "last_search": None}

#     def _load_from_disk(self):
#         if os.path.exists(self.storage_path):
#             with open(self.storage_path, "r") as f:
#                 return json.load(f)
#         return {"critical_info": {}, "semantic_memory": {}, "episodic_memory": [], "created_at": datetime.now().strftime("%Y-%m-%d")}

#     def save_to_disk(self):
#         with open(self.storage_path, "w") as f:
#             json.dump(self.memory, f, indent=4)

#     # ---> THE MISSING METHOD WE JUST RESTORED <---
#     def learn_fact(self, key: str, value: str, tier: str = "semantic"):
#         """Stores a fact directly into the single-user memory."""
#         if tier == "critical":
#             self.memory["critical_info"][key] = value
#         else:
#             self.memory["semantic_memory"][key] = value
#         self.save_to_disk()

#     def get_brain_dump(self) -> str:
#         dump = "RUA Memory Dump: "
#         if self.memory.get('critical_info'): dump += f"CRITICAL: {self.memory['critical_info']}. "
#         if self.memory.get('semantic_memory'): dump += f"FACTS: {self.memory['semantic_memory']}. "
#         if self.working_memory.get('buffer'): dump += f"ACTIVE TASK: {self.working_memory['buffer']}. "
#         return dump
    
#     def wipe_memory(self):
#         """Erases all saved facts and resets the memory."""
#         self.memory["semantic_memory"] = {}
#         self.memory["critical_info"] = {}
#         self.save_to_disk()

import json
import os
from datetime import datetime, timedelta

# Define the new folder structure
MEMORY_DIR = "rua_memory"
USER_FILE = os.path.join(MEMORY_DIR, "user_data.json")
CONVO_DIR = os.path.join(MEMORY_DIR, "conversation_data")

class RUACognitiveHub:
    def __init__(self):
        # Ensure the folders exist
        os.makedirs(CONVO_DIR, exist_ok=True)
        
        self.user_data = self._load_user_data()
        self.working_memory = {"buffer": {}, "last_search": None}
        
        # Run a file cleanup immediately on startup
        self.prune_episodes(days=7)

    def _load_user_data(self):
        """Loads permanent facts. Initializes if it doesn't exist."""
        if os.path.exists(USER_FILE):
            try:
                with open(USER_FILE, "r") as f:
                    return json.load(f)
            except json.JSONDecodeError:
                pass # Fallback to default if file is corrupted
                
        return {"critical_info": {}, "semantic_memory": {}, "created_at": datetime.now().strftime("%Y-%m-%d")}

    def save_user_data(self):
        """Saves permanent facts to the dedicated user file."""
        with open(USER_FILE, "w") as f:
            json.dump(self.user_data, f, indent=4)

    def learn_fact(self, key: str, value: str, tier: str = "semantic"):
        """Stores a fact into the user data file."""
        if tier == "critical":
            self.user_data["critical_info"][key] = value
        else:
            self.user_data["semantic_memory"][key] = value
        self.save_user_data()

    # ---------------------------------------------------------
    # DAILY CONVERSATION TRACKING
    # ---------------------------------------------------------
    def add_episode(self, user_text: str, rua_text: str):
        """Saves a conversation turn into today's specific JSON file."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        daily_file = os.path.join(CONVO_DIR, f"{today_str}.json")
        
        # Load today's existing chats, or start a new list
        daily_chats = []
        if os.path.exists(daily_file):
            with open(daily_file, "r") as f:
                daily_chats = json.load(f)
                
        # Append the new message
        timestamp = datetime.now().isoformat()
        daily_chats.append({
            "time": timestamp,
            "user": user_text,
            "rua": rua_text
        })
        
        # Save today's file
        with open(daily_file, "w") as f:
            json.dump(daily_chats, f, indent=4)
            
        # Trigger cleanup for old files
        self.prune_episodes(days=7)

    def prune_episodes(self, days: int = 7):
        """Scans the conversation folder and deletes any file older than 7 days."""
        cutoff_date = datetime.now().date() - timedelta(days=days)
        
        for filename in os.listdir(CONVO_DIR):
            if filename.endswith(".json"):
                # Extract the date from the filename (e.g., "2023-10-25")
                date_str = filename.replace(".json", "")
                try:
                    file_date = datetime.strptime(date_str, "%Y-%m-%d").date()
                    if file_date < cutoff_date:
                        # File is too old, delete it from the hard drive completely
                        file_path = os.path.join(CONVO_DIR, filename)
                        os.remove(file_path)
                except ValueError:
                    pass # Skip files that don't match the YYYY-MM-DD format

    # ---------------------------------------------------------
    # UTILITIES
    # ---------------------------------------------------------
    def wipe_memory(self):
        """Erases all saved facts and deletes all conversation logs."""
        # Wipe User Data
        self.user_data["semantic_memory"] = {}
        self.user_data["critical_info"] = {}
        self.save_user_data()
        
        # Wipe Conversation Files
        for filename in os.listdir(CONVO_DIR):
            os.remove(os.path.join(CONVO_DIR, filename))

    def get_brain_dump(self) -> str:
        """Assembles facts and recent chat history to feed into RUA's context."""
        dump = "RUA Memory Dump: "
        if self.user_data.get('critical_info'): dump += f"CRITICAL: {self.user_data['critical_info']}. "
        if self.user_data.get('semantic_memory'): dump += f"FACTS: {self.user_data['semantic_memory']}. "
        
        # Gather all available daily chat files, sort chronologically
        all_chats = []
        chat_files = sorted([f for f in os.listdir(CONVO_DIR) if f.endswith(".json")])
        
        # Load the raw chat data
        for filename in chat_files:
            with open(os.path.join(CONVO_DIR, filename), "r") as f:
                all_chats.extend(json.load(f))
                
        # Inject only the last 5 turns to keep API costs down and responses fast
        recent_eps = all_chats[-5:]
        if recent_eps:
            dump += "RECENT CHAT HISTORY: "
            for ep in recent_eps:
                dump += f"[User: {ep['user']} | RUA: {ep['rua']}] "

        if self.working_memory.get('buffer'): dump += f"ACTIVE TASK: {self.working_memory['buffer']}. "
        return dump