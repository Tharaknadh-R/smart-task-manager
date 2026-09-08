from datetime import datetime

from pydantic import BaseModel

class AttachmentResponse(BaseModel):
    attachment_id: str
    filename: str
    task_id: int
    created_at: datetime