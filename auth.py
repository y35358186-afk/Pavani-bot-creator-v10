"""Authentication and Session Management"""
import hashlib, datetime, time, uuid
from typing import Optional, Dict, List
from collections import defaultdict
from config import Config

class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, dict] = {}
        self.login_attempts: Dict[str, List[float]] = defaultdict(list)
    
    def create_session(self, ip: str) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = {
            "created": datetime.datetime.now(),
            "ip": ip,
            "last_seen": datetime.datetime.now()
        }
        return session_id
    
    def verify_session(self, session_id: Optional[str]) -> bool:
        if not session_id or session_id not in self.sessions:
            return False
        session = self.sessions[session_id]
        age = datetime.datetime.now() - session["created"]
        if age.total_seconds() > Config.SESSION_TIMEOUT_HOURS * 3600:
            del self.sessions[session_id]
            return False
        session["last_seen"] = datetime.datetime.now()
        return True
    
    def check_rate_limit(self, ip: str, limit: int = 5, window: int = 300) -> bool:
        """Rate limiting for login attempts"""
        now = time.time()
        attempts = self.login_attempts[ip]
        attempts = [t for t in attempts if now - t < window]
        self.login_attempts[ip] = attempts
        if len(attempts) >= limit:
            return False
        attempts.append(now)
        return True
    
    def delete_session(self, session_id: str):
        self.sessions.pop(session_id, None)
