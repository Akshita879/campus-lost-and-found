import datetime
from typing import Optional, List
from fastapi import APIRouter, Depends, status, Query, UploadFile, File, Form, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.models.report import ReportType, ReportStatus
from app.schemas.report import (
    ReportCreateRequest,
    ReportUpdateRequest,
    ReportPublicResponse,
    ReportSearchResponse
)
from app.schemas.matching import ReportMatchesResponse
from app.services.report_service import ReportService
from app.services.matching_service import MatchingService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.post(
    "",
    response_model=ReportPublicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new lost or found report (JSON)"
)
async def create_report(
    data: ReportCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new report using JSON body.
    Supports both LOST and FOUND items.
    """
    return await ReportService.create_report(db, current_user, data, image_file=None)


@router.post(
    "/upload",
    response_model=ReportPublicResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new lost or found report with optional image (Multipart Form)"
)
async def create_report_with_image(
    item_name: str = Form(..., min_length=2, max_length=255),
    category: str = Form(..., min_length=2, max_length=100),
    description: str = Form(..., min_length=5),
    report_type: ReportType = Form(...),
    approximate_date: datetime.date = Form(...),
    location: str = Form(..., min_length=2, max_length=255),
    image: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new report with an optional image file upload.
    Supports JPEG, PNG, WEBP files up to 5MB.
    """
    data = ReportCreateRequest(
        item_name=item_name,
        category=category,
        description=description,
        report_type=report_type,
        approximate_date=approximate_date,
        location=location
    )
    return await ReportService.create_report(db, current_user, data, image_file=image)


@router.get(
    "",
    response_model=ReportSearchResponse,
    summary="Browse active reports with pagination"
)
def list_reports(
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    report_type: Optional[ReportType] = Query(None, description="Filter by LOST or FOUND"),
    db: Session = Depends(get_db)
):
    """Browse active lost and found reports publicly."""
    items, total, total_pages = ReportService.search_reports(
        db,
        report_type=report_type,
        status=ReportStatus.ACTIVE,
        page=page,
        page_size=page_size
    )
    return ReportSearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=items
    )


@router.get(
    "/search",
    response_model=ReportSearchResponse,
    summary="Search and filter reports"
)
def search_reports(
    keyword: Optional[str] = Query(None, description="Search term in item name and description"),
    category: Optional[str] = Query(None, description="Filter by item category"),
    report_type: Optional[ReportType] = Query(None, description="Filter by LOST or FOUND"),
    location: Optional[str] = Query(None, description="Filter by campus location"),
    date_from: Optional[datetime.date] = Query(None, description="Start date filter"),
    date_to: Optional[datetime.date] = Query(None, description="End date filter"),
    status: Optional[ReportStatus] = Query(None, description="Filter by status (defaults to ACTIVE and CLAIM_PENDING)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(10, ge=1, le=100, description="Items per page"),
    db: Session = Depends(get_db)
):
    """
    Flexible database-level search and filtering with pagination.
    Excludes CLOSED and RESOLVED reports from default active browsing.
    """
    items, total, total_pages = ReportService.search_reports(
        db,
        keyword=keyword,
        category=category,
        report_type=report_type,
        location=location,
        date_from=date_from,
        date_to=date_to,
        status=status,
        page=page,
        page_size=page_size
    )
    return ReportSearchResponse(
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
        items=items
    )


@router.get(
    "/my",
    response_model=List[ReportPublicResponse],
    summary="Get reports created by current user"
)
def get_my_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all reports submitted by the authenticated user."""
    return ReportService.get_user_reports(db, current_user.id)


@router.get(
    "/{report_id}",
    response_model=ReportPublicResponse,
    summary="Get report by ID"
)
def get_report(
    report_id: int,
    db: Session = Depends(get_db)
):
    """Retrieve public details for a specific report."""
    return ReportService.get_report_by_id(db, report_id)


@router.put(
    "/{report_id}",
    response_model=ReportPublicResponse,
    summary="Update report details (Owner only)"
)
async def update_report(
    report_id: int,
    data: ReportUpdateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Update report metadata. Only the owner who created the report can update it."""
    return await ReportService.update_report(db, current_user, report_id, data, image_file=None)


@router.put(
    "/{report_id}/image",
    response_model=ReportPublicResponse,
    summary="Update report image (Owner only)"
)
async def update_report_image(
    report_id: int,
    image: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Upload or replace the image of an existing report."""
    return await ReportService.update_report(
        db, current_user, report_id, ReportUpdateRequest(), image_file=image
    )


@router.delete(
    "/{report_id}",
    response_model=ReportPublicResponse,
    summary="Close report (Owner only soft closure)"
)
def close_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Soft-close a report. Sets status to CLOSED so it no longer appears in active matches."""
    return ReportService.close_report(db, current_user, report_id)


@router.get(
    "/{report_id}/matches",
    response_model=ReportMatchesResponse,
    summary="Get ranked potential matches for a lost report"
)
def get_matches_for_report(
    report_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Computes explainable deterministic similarity scores between a LOST report
    and all ACTIVE FOUND reports. Excludes closed, resolved, or duplicate items.
    """
    return MatchingService.find_matches_for_lost_report(db, report_id)
