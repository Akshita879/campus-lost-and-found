import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict
from app.models.claim import ClaimStatus
from app.schemas.report import ReportPublicResponse


class ClaimCreateRequest(BaseModel):
    report_id: int = Field(..., description="ID of the FOUND report being claimed")
    lost_report_id: Optional[int] = Field(None, description="Optional ID of claimant's LOST report")
    verification_details: str = Field(..., min_length=5, description="Private identifying details to prove ownership")


class ClaimResponse(BaseModel):
    id: int
    report_id: int
    claimant_id: int
    lost_report_id: Optional[int] = None
    verification_details: str
    status: ClaimStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class ClaimDetailResponse(ClaimResponse):
    found_item: Optional[ReportPublicResponse] = None
    lost_item: Optional[ReportPublicResponse] = None
