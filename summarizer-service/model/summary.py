import uuid

from sqlalchemy.dialects.postgresql import UUID

from sqlalchemy import Column, Text, ForeignKey
from model import Base

class Summary(Base):
    __tablename__ = "summaries"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    transcript_id = Column(UUID(as_uuid=True), ForeignKey("transcripts.id"))
    content = Column(Text, nullable=False)

