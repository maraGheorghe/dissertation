from dataclasses import dataclass
from datetime import datetime
import uuid

@dataclass
class AudioFileUploadedEvent:
    id: uuid.UUID
    storage_key: str
    upload_time: datetime
