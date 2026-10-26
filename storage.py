import chromadb
from datetime import datetime
from typing import List, Dict
import uuid
import pickle
import os

class ChatStorage:
    def __init__(self, path: str = "./chroma_db"):
        # Persistent Chroma database
        self.client = chromadb.PersistentClient(path=path)

        # Collection for all chat messages
        self.collection = self.client.get_or_create_collection(
            name="chat_history",
            metadata={"hnsw:space": "cosine"}
        )

    def create_session(self, title: str = "New Conversation") -> str:
        """Create a new session ID"""
        session_id = str(uuid.uuid4())
        return session_id

    def add_message(self, session_id: str, role: str, content: str):
        """Save a message into Chroma"""
        if not content.strip():
            return

        message_id = str(uuid.uuid4())
        timestamp = datetime.now().isoformat()

        self.collection.add(
            documents=[content],
            metadatas=[{
                "session_id": session_id,
                "role": role,
                "timestamp": timestamp
            }],
            ids=[message_id]
        )

        # Also update the pickle file every time a message is added
        self.export_to_pkl()

    def get_session_messages(self, session_id: str, limit: int = 50) -> List[Dict]:
        """
        Get all messages of a session, ordered by time.
        Returns list of {"role": "...", "content": "..."}
        """
        results = self.collection.get(
            where={"session_id": session_id},
            include=["documents", "metadatas"]
        )

        if not results["ids"]:
            return []

        # Combine and sort by timestamp
        messages = []
        for doc, meta in zip(results["documents"], results["metadatas"]):
            messages.append({
                "role": meta["role"],
                "content": doc,
                "timestamp": meta["timestamp"]
            })

        # Sort by time (oldest first)
        messages.sort(key=lambda x: x["timestamp"])

        # Keep only the last `limit` messages
        messages = messages[-limit:]

        # Return in LLM format
        return [{"role": m["role"], "content": m["content"]} for m in messages]

    def get_recent_messages(self, session_id: str, max_messages: int = 6) -> List[Dict]:
        """Get only the most recent messages"""
        return self.get_session_messages(session_id, limit=max_messages)

    def export_to_pkl(self, filename: str = "chat_history.pkl"):
        """Save all data from Chroma into a .pkl file for easy viewing"""
        results = self.collection.get(include=["documents", "metadatas"])

        data = {
            "ids": results["ids"],
            "documents": results["documents"],
            "metadatas": results["metadatas"]
        }

        with open(filename, "wb") as f:
            pickle.dump(data, f)

        print(f"[Storage] Exported to {filename}")

    def show_pkl(self, filename: str = "chat_history.pkl"):
        """Print what is inside the .pkl file"""
        if not os.path.exists(filename):
            print("No .pkl file found yet.")
            return

        with open(filename, "rb") as f:
            data = pickle.load(f)

        print("\n===== Content of chat_history.pkl =====")
        for i, (doc_id, doc, meta) in enumerate(zip(data["ids"], data["documents"], data["metadatas"])):
            print(f"\n[{i+1}] ID: {doc_id}")
            print(f"    Role     : {meta.get('role')}")
            print(f"    Session  : {meta.get('session_id')}")
            print(f"    Time     : {meta.get('timestamp')}")
            print(f"    Content  : {doc}")
        print("=======================================\n")
