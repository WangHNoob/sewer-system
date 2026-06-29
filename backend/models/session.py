from typing import Optional, Dict
from datetime import datetime, timedelta


class Session:
    def __init__(self, session_id: str):
        self.session_id = session_id
        self.created_at = datetime.now()
        self.last_active = datetime.now()
        self.detection_cache: Dict = {}
        self.uploaded_image_path: Optional[str] = None
        self.message_history: list = []

    def touch(self):
        self.last_active = datetime.now()

    def is_expired(self, timeout_minutes: int = 30) -> bool:
        return datetime.now() - self.last_active > timedelta(minutes=timeout_minutes)
