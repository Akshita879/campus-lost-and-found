import enum
import datetime
from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.orm import relationship
from app.database import Base


class ClaimStatus(str, enum.Enum):
    PENDING = "PENDING"
    WITHDRAWN = "WITHDRAWN"


class Claim(Base):
    __tablename__ = "claims"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    report_id = Column(Integer, ForeignKey("reports.id", ondelete="CASCADE"), nullable=False, index=True)
    claimant_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    lost_report_id = Column(Integer, ForeignKey("reports.id", ondelete="SET NULL"), nullable=True, index=True)
    verification_details = Column(Text, nullable=False)
    status = Column(SQLEnum(ClaimStatus, native_enum=False, length=20), nullable=False, default=ClaimStatus.PENDING, index=True)
    created_at = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow, nullable=False)

    # Relationships
    report = relationship("Report", foreign_keys=[report_id], back_populates="claims")
    claimant = relationship("User", foreign_keys=[claimant_id], back_populates="claims")
    lost_report = relationship("Report", foreign_keys=[lost_report_id], back_populates="linked_claims")
