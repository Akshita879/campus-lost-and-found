from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.claim import (
    ClaimCreateRequest,
    ClaimResponse,
    ClaimDetailResponse,
    MeetupMessageRequest,
)
from app.schemas.report import ReportPublicResponse
from app.services.claim_service import ClaimService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/claims", tags=["Claims"])


def _detail(claim) -> ClaimDetailResponse:
    found_item_data = ReportPublicResponse.model_validate(claim.report) if claim.report else None
    lost_item_data = ReportPublicResponse.model_validate(claim.lost_report) if claim.lost_report else None
    return ClaimDetailResponse(
        id=claim.id,
        report_id=claim.report_id,
        claimant_id=claim.claimant_id,
        lost_report_id=claim.lost_report_id,
        verification_details=claim.verification_details,
        meetup_message=claim.meetup_message,
        status=claim.status,
        created_at=claim.created_at,
        updated_at=claim.updated_at,
        found_item=found_item_data,
        lost_item=lost_item_data,
    )


@router.post(
    "",
    response_model=ClaimResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a claim for a found item",
)
def create_claim(
    data: ClaimCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ClaimService.create_claim(db, current_user, data)


@router.get(
    "/my",
    response_model=List[ClaimResponse],
    summary="Get claims submitted by current user",
)
def get_my_claims(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ClaimService.get_user_claims(db, current_user)


@router.get(
    "/incoming",
    response_model=List[ClaimDetailResponse],
    summary="Get claims on found items you reported (for approval)",
)
def get_incoming_claims(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return [_detail(c) for c in ClaimService.get_incoming_claims(db, current_user)]


@router.get(
    "/{claim_id}",
    response_model=ClaimDetailResponse,
    summary="Get specific claim details",
)
def get_claim(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return _detail(ClaimService.get_claim_by_id(db, current_user, claim_id))


@router.post(
    "/{claim_id}/meetup",
    response_model=ClaimResponse,
    summary="Claimant shares meetup where/when details with the finder",
)
def set_meetup(
    claim_id: int,
    data: MeetupMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ClaimService.set_meetup_message(db, current_user, claim_id, data.meetup_message)


@router.post(
    "/{claim_id}/withdraw",
    response_model=ClaimResponse,
    summary="Withdraw a pending claim (Claimant only)",
)
def withdraw_claim(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ClaimService.withdraw_claim(db, current_user, claim_id)


@router.post(
    "/{claim_id}/approve",
    response_model=ClaimResponse,
    summary="Approve a pending claim (Found-item holder only)",
)
def approve_claim(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ClaimService.approve_claim(db, current_user, claim_id)


@router.post(
    "/{claim_id}/reject",
    response_model=ClaimResponse,
    summary="Reject a pending claim (Found-item holder only)",
)
def reject_claim(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return ClaimService.reject_claim(db, current_user, claim_id)
