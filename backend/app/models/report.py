import enum
import datetime
from sqlalchemy import Column, Integer, String, Text, Date, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base


class ReportType(str, enum.Enum):
    LOST = "LOST"
    FOUND = "FOUND"


class ReportStatus(str, enum.Enum):
    ACTIVE = "ACTIVE"
    CLAIM_PENDING = "CLAIM_PENDING"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    item_name = Column(String(255), nullable=False, index=True)
    category = Column(String(100), nullable=False, index=True)
    description = Column(Text, nullable=False)
    report_type = Column(SQLEnum(ReportType, native_enum=False, length=20), nullable=False, index=True)
    approximate_date = Column(Date, nullable=False, index=True)
    location = Column(String(255), nullable=False, index=True)
    image_path = Column(String(500), nullable=True)
    status = Column(SQLEnum(ReportStatus, native_enum=False, length=20), nullable=False, default=ReportStatus.ACTIVE, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    user = relationship("User", back_populates="reports", foreign_keys=[user_id])
    claims = relationship("Claim", back_populates="report", foreign_keys="Claim.report_id", cascade="all, delete-orphan")
    linked_claims = relationship("Claim", back_populates="lost_report", foreign_keys="Claim.lost_report_id")
