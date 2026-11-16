import datetime
from typing import List, Optional
from pydantic import BaseModel, Field


class ScoreBreakdown(BaseModel):
    category: float = Field(..., description="Category similarity score (0-100)")
    item_name: float = Field(..., description="Item name similarity score (0-100)")
    description: float = Field(..., description="Description similarity score (0-100)")
    location: float = Field(..., description="Location similarity score (0-100)")
    date: float = Field(..., description="Date proximity score (0-100)")


class MatchCandidate(BaseModel):
    found_report_id: int
    item_name: str
    category: str
    description: str
    location: str
    approximate_date: datetime.date
    image_path: Optional[str] = None
    similarity_score: float = Field(..., description="Overall weighted similarity score (0-100)")
    match_status: str = "POTENTIAL_MATCH"
    score_breakdown: ScoreBreakdown


class ReportMatchesResponse(BaseModel):
    lost_report_id: int
    lost_item_name: str
    matches: List[MatchCandidate]
