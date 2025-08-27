import os
import json
class SessionManager:
    """Handles session file storage & retrieval."""

    SESSIONS_DIR = "sessions"

    def __init__(self, session_id: str):
        os.makedirs(self.SESSIONS_DIR, exist_ok=True)
        self.history_file = os.path.join(self.SESSIONS_DIR, f"session_{session_id}.json")
    def load(self):
        if os.path.exists(self.history_file):
            with open(self.history_file, "r", encoding="utf-8") as f:
                return json.load(f).get("messages", [])
        return []

    def save(self, messages):
        with open(self.history_file, "w", encoding="utf-8") as f:
            json.dump({"messages": [m.to_dict() for m in messages]}, f, indent=2)
