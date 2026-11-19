import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, Text, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    source_type = Column(String(50), default="documentation", nullable=False)  # readme, documentation, runbook, incident_report, architecture, code
    content = Column(Text, nullable=False)
    file_path = Column(String(500), nullable=True)
    content_hash = Column(String(64), index=True, nullable=True)
    file_size = Column(Integer, default=0, nullable=False)
    chunk_count = Column(Integer, default=1)
    status = Column(String(50), default="indexed", nullable=False)
    metadata_json = Column(JSON, nullable=True)
    indexed_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="documents")
