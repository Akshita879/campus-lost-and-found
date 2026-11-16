import datetime
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict
from app.models.report import ReportType, ReportStatus


class ReportCreateRequest(BaseModel):
    item_name: str = Field(..., min_length=2, max_length=255)
    category: str = Field(..., min_length=2, max_length=100)
    description: str = Field(..., min_length=5)
    report_type: ReportType
    approximate_date: datetime.date
    location: str = Field(..., min_length=2, max_length=255)


class ReportUpdateRequest(BaseModel):
    item_name: Optional[str] = Field(None, min_length=2, max_length=255)
    category: Optional[str] = Field(None, min_length=2, max_length=100)
    description: Optional[str] = Field(None, min_length=5)
    approximate_date: Optional[datetime.date] = None
    location: Optional[str] = Field(None, min_length=2, max_length=255)
    status: Optional[ReportStatus] = None


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
