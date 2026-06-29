from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class BatchTask:
    def __init__(
        self,
        task_id: str,
        status: str,
        total_images: int,
        processed: int,
        image_paths: List[str],
        results: List[dict],
        report_path: Optional[str] = None,
    ):
        self.task_id = task_id
        self.status = status
        self.total_images = total_images
        self.processed = processed
        self.image_paths = image_paths
        self.results = results
        self.report_path = report_path
        self.current_image: Optional[str] = None
        self.errors: List[dict] = []


class ChatMessage(BaseModel):
    role: str
    content: str
    image_base64: Optional[str] = None
    timestamp: Optional[datetime] = None


class ImageUploadResponse(BaseModel):
    session_id: str
    detection_result: Optional[dict] = None
    message: str = "Image uploaded successfully"


class BatchProgress(BaseModel):
    task_id: str
    status: str
    total: int
    processed: int
    current_image: Optional[str] = None
    errors: List[dict] = []
