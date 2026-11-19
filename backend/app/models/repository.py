import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, DateTime, ForeignKey, Integer, JSON
from sqlalchemy.orm import relationship
from app.db.session import Base

class Repository(Base):
    __tablename__ = "repositories"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    project_id = Column(String(36), ForeignKey("projects.id", ondelete="CASCADE"), nullable=False, index=True)
    name = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    source = Column(String(50), default="github", nullable=False)  # github, upload, gitlab
    branch = Column(String(100), default="main", nullable=False)
    language = Column(String(50), default="Python", nullable=False)
    health_status = Column(String(50), default="healthy", nullable=False)  # healthy, warning, critical, unknown
    issue_count = Column(Integer, default=0)
    commit_count = Column(Integer, default=0)
    file_count = Column(Integer, default=0)
    url = Column(String(500), nullable=True)
    files_tree = Column(JSON, nullable=True)
    last_synced_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    project = relationship("Project", back_populates="repositories")
    bugs = relationship("Bug", back_populates="repository", cascade="all, delete-orphan")
