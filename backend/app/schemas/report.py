import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict, model_validator
from app.models.report import ReportType, ReportStatus


class ReportCreateRequest(BaseModel):
    item_name: str = Field(..., min_length=2, max_length=255)
    category: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=5)
    report_type: ReportType
    approximate_date: datetime.date
    location: str = Field(..., min_length=2, max_length=255)
    verification_question: Optional[str] = Field(None, max_length=500)
    verification_answer: Optional[str] = Field(None, max_length=500)
    related_lost_report_id: Optional[int] = Field(
        None, description="When reporting FOUND for a specific LOST listing"
    )

    @model_validator(mode="after")
    def validate_verification_fields(self):
        if self.report_type == ReportType.LOST:
            q = (self.verification_question or "").strip() or None
            a = (self.verification_answer or "").strip() or None
            self.verification_question = q
            self.verification_answer = a
            self.related_lost_report_id = None
        elif self.related_lost_report_id is not None:
            a = (self.verification_answer or "").strip()
            if len(a) < 2:
                raise ValueError("Answer the owner's verification question (2+ characters)")
            self.verification_answer = a
            self.verification_question = None
        else:
            # Standalone FOUND reports do not use ownership Q&A
            self.verification_question = None
            self.verification_answer = None
        return self


class ReportUpdateRequest(BaseModel):
    item_name: Optional[str] = Field(None, min_length=2, max_length=255)
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, min_length=5)
    approximate_date: Optional[datetime.date] = None
    location: Optional[str] = Field(None, min_length=2, max_length=255)
    status: Optional[ReportStatus] = None


class MeetupDetailsRequest(BaseModel):
    meetup_message: str = Field(..., min_length=10, max_length=1000)


class ReportPublicResponse(BaseModel):
    id: int
    user_id: int
    item_name: str
    category: str
    description: str
    report_type: ReportType
    approximate_date: datetime.date
    location: str
    image_path: Optional[str] = None
    verification_question: Optional[str] = None
    related_lost_report_id: Optional[int] = None
    status: ReportStatus
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class ReportSearchResponse(BaseModel):
    total: int
    page: int
    page_size: int
    total_pages: int
    items: List[ReportPublicResponse]
