import os
from datetime import datetime
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# Define the new folder structure
MEMORY_DIR = "rua_memory"
TXT_DIR = os.path.join(MEMORY_DIR, "conversation_logs")
VECTOR_DB_DIR = os.path.join(MEMORY_DIR, "chroma_db")

class RUACognitiveHub:
    def __init__(self):
        # Ensure the folders exist
        os.makedirs(TXT_DIR, exist_ok=True)
        
        print("🧠 Initializing Neural RAG Memory... ", end="", flush=True)
        
        # 1. Initialize the Embedding Model (Runs locally, fast, downloads automatically the first time)
        self.embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        # 2. Initialize Chroma Vector Database
        self.vector_store = Chroma(
            collection_name="rua_core_memory",
            embedding_function=self.embeddings,
            persist_directory=VECTOR_DB_DIR
        )
        print("Done!")

    # ---------------------------------------------------------
    # DAILY CONVERSATION TRACKING (.txt + Vector Storage)
    # ---------------------------------------------------------
    def add_episode(self, user_text: str, rua_text: str):
        """Saves to a daily .txt file AND embeds into the Vector DB."""
        today_str = datetime.now().strftime("%Y-%m-%d")
        
        # 1. Save to raw .txt file for your own readability
        txt_file = os.path.join(TXT_DIR, f"{today_str}.txt")
        log_entry = f"[{datetime.now().strftime('%H:%M:%S')}] User: {user_text} | RUA: {rua_text}\n"
        
        with open(txt_file, "a", encoding="utf-8") as f:
            f.write(log_entry)
            
        # 2. Embed and Save to Vector DB for RAG Retrieval
        memory_string = f"User asked: '{user_text}'. RUA replied: '{rua_text}'"
        self.vector_store.add_texts(
            texts=[memory_string],
            metadatas=[{"date": today_str, "type": "chat_history"}]
        )

    def learn_fact(self, key: str, value: str, tier: str = "semantic"):
        """Embeds permanent user facts into the Vector DB."""
        self.vector_store.add_texts(
            texts=[f"IMPORTANT PERMANENT FACT ABOUT USER: {value}"],
            metadatas=[{"type": "fact", "tier": tier, "key": key}]
        )

    # ---------------------------------------------------------
    # RAG RETRIEVAL (The Magic)
    # ---------------------------------------------------------
    def get_brain_dump(self, current_user_prompt: str) -> str:
        """Searches the Vector DB for memories semantically related to the current prompt."""
        # Perform a similarity search to find the top 4 most relevant past interactions/facts
        results = self.vector_store.similarity_search(current_user_prompt, k=4)
        
        if not results:
            return "No relevant long-term memories."
            
        dump = "RELEVANT PAST MEMORIES (Use this context if it applies to the current query):\n"
        for doc in results:
            dump += f"- {doc.page_content}\n"
            
        return dump

    # ---------------------------------------------------------
    # UTILITIES
    # ---------------------------------------------------------
    def wipe_memory(self):
        """Erases all .txt files and destroys the Vector DB."""
        # Wipe Text Files
        for filename in os.listdir(TXT_DIR):
            if filename.endswith(".txt"):
                os.remove(os.path.join(TXT_DIR, filename))
                
        # Wipe and Reinitialize Chroma DB
        self.vector_store.delete_collection()
        self.vector_store = Chroma(
            collection_name="rua_core_memory",
            embedding_function=self.embeddings,
            persist_directory=VECTOR_DB_DIR
        )