import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from rapidfuzz import fuzz

from app.models.report import Report, ReportType, ReportStatus
from app.schemas.matching import MatchCandidate, ReportMatchesResponse, ScoreBreakdown
from app.config import settings


class MatchingService:
    @staticmethod
    def calculate_category_score(lost_cat: str, found_cat: str) -> float:
        """Exact category match gives 100.0, mismatch gives 0.0."""
        if not lost_cat or not found_cat:
            return 0.0
        return 100.0 if lost_cat.strip().lower() == found_cat.strip().lower() else 0.0

    @staticmethod
    def calculate_name_score(lost_name: str, found_name: str) -> float:
        """Token set ratio fuzzy score for item names."""
        if not lost_name or not found_name:
            return 0.0
        return float(fuzz.token_set_ratio(lost_name.strip().lower(), found_name.strip().lower()))

    @staticmethod
    def calculate_description_score(lost_desc: str, found_desc: str) -> float:
        """Token set ratio fuzzy score for item descriptions."""
        if not lost_desc or not found_desc:
            return 0.0
        return float(fuzz.token_set_ratio(lost_desc.strip().lower(), found_desc.strip().lower()))

    @staticmethod
    def calculate_location_score(lost_loc: str, found_loc: str) -> float:
        """Campus location similarity using token set ratio."""
        if not lost_loc or not found_loc:
            return 0.0
        return float(fuzz.token_set_ratio(lost_loc.strip().lower(), found_loc.strip().lower()))

    @staticmethod
    def calculate_date_score(lost_date: Optional[datetime.date], found_date: Optional[datetime.date]) -> float:
        """
        Decay function based on difference in calendar days:
        - Same day: 100%
        - 1 day diff: 90%
        - 2 days diff: 80%
        - 3 days diff: 70%
        - 4 days diff: 60%
        - 5 days diff: 50%
        - 6 days diff: 40%
        - 7 days diff: 30%
        - 8-14 days diff: decay by 4% per day down to 0%
        - > 14 days diff: 0%
        """
        if not lost_date or not found_date:
            return 0.0

        days_diff = abs((lost_date - found_date).days)
        if days_diff == 0:
            return 100.0
        elif days_diff <= 7:
            return max(0.0, 100.0 - (days_diff * 10.0))
        elif days_diff <= 14:
            return max(0.0, 30.0 - ((days_diff - 7) * 4.0))
        else:
            return 0.0

    @classmethod
    def evaluate_pair(cls, lost: Report, found: Report) -> Optional[MatchCandidate]:
        """Calculates attribute scores, total similarity, and creates MatchCandidate."""
        cat_score = cls.calculate_category_score(lost.category, found.category)
        name_score = cls.calculate_name_score(lost.item_name, found.item_name)
        desc_score = cls.calculate_description_score(lost.description, found.description)
        loc_score = cls.calculate_location_score(lost.location, found.location)
        date_score = cls.calculate_date_score(lost.approximate_date, found.approximate_date)

        # Calculate weighted total (weights sum to 100)
        total_score = (
            (cat_score * (settings.WEIGHT_CATEGORY / 100.0)) +
            (name_score * (settings.WEIGHT_ITEM_NAME / 100.0)) +
            (desc_score * (settings.WEIGHT_DESCRIPTION / 100.0)) +
            (loc_score * (settings.WEIGHT_LOCATION / 100.0)) +
            (date_score * (settings.WEIGHT_DATE / 100.0))
        )
        total_score = round(total_score, 1)

        if total_score < settings.MATCH_MIN_SCORE_THRESHOLD:
            return None

        breakdown = ScoreBreakdown(
            category=round(cat_score, 1),
            item_name=round(name_score, 1),
            description=round(desc_score, 1),
            location=round(loc_score, 1),
            date=round(date_score, 1)
        )

        return MatchCandidate(
            found_report_id=found.id,
            item_name=found.item_name,
            category=found.category,
            description=found.description,
            location=found.location,
            approximate_date=found.approximate_date,
            image_path=found.image_path,
            similarity_score=total_score,
            match_status="POTENTIAL_MATCH",
            score_breakdown=breakdown
        )

    @classmethod
    def find_matches_for_lost_report(
        cls,
        db: Session,
        lost_report_id: int
    ) -> ReportMatchesResponse:
        """
        Retrieves a LOST report, queries all ACTIVE FOUND candidates,
        evaluates similarity scores, ranks them descending, and returns top matches.
        """
        lost_report = db.query(Report).filter(Report.id == lost_report_id).first()
        if not lost_report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report with ID {lost_report_id} not found"
            )

        if lost_report.report_type != ReportType.LOST:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Matches can only be computed for reports of type LOST against FOUND items"
            )

        # Retrieve active FOUND reports (excluding any closed or resolved)
        candidates = (
            db.query(Report)
            .filter(
                Report.report_type == ReportType.FOUND,
                Report.status == ReportStatus.ACTIVE,
                Report.id != lost_report.id
            )
            .all()
        )

        matches: List[MatchCandidate] = []
        for found in candidates:
            candidate = cls.evaluate_pair(lost_report, found)
            if candidate:
                matches.append(candidate)

        # Sort descending by similarity score
        matches.sort(key=lambda m: m.similarity_score, reverse=True)

        # Limit to configured maximum results
        matches = matches[:settings.MATCH_MAX_RESULTS]

        return ReportMatchesResponse(
            lost_report_id=lost_report.id,
            lost_item_name=lost_report.item_name,
            matches=matches
        )
