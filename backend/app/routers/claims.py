from typing import List
from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.claim import ClaimCreateRequest, ClaimResponse, ClaimDetailResponse
from app.schemas.report import ReportPublicResponse
from app.services.claim_service import ClaimService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/claims", tags=["Claims"])


@router.post(
    "",
    response_model=ClaimResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Submit a claim for a found item"
)
def create_claim(
    data: ClaimCreateRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Submit a claim against an active FOUND report by providing private verification details.
    Optionally link the claimant's own LOST report.
    """
    return ClaimService.create_claim(db, current_user, data)


@router.get(
    "/my",
    response_model=List[ClaimResponse],
    summary="Get claims submitted by current user"
)
def get_my_claims(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Retrieve all claims submitted by the authenticated user."""
    return ClaimService.get_user_claims(db, current_user)


@router.get(
    "/{claim_id}",
    response_model=ClaimDetailResponse,
    summary="Get specific claim details (Claimant only)"
)
def get_claim(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Retrieve specific claim details.
    Access is strictly restricted to the user who filed the claim to preserve privacy.
    """
    claim = ClaimService.get_claim_by_id(db, current_user, claim_id)
    
    found_item_data = ReportPublicResponse.model_validate(claim.report) if claim.report else None
    lost_item_data = ReportPublicResponse.model_validate(claim.lost_report) if claim.lost_report else None

    return ClaimDetailResponse(
        id=claim.id,
        report_id=claim.report_id,
        claimant_id=claim.claimant_id,
        lost_report_id=claim.lost_report_id,
        verification_details=claim.verification_details,
        status=claim.status,
        created_at=claim.created_at,
        updated_at=claim.updated_at,
        found_item=found_item_data,
        lost_item=lost_item_data
    )


@router.post(
    "/{claim_id}/withdraw",
    response_model=ClaimResponse,
    summary="Withdraw a pending claim (Claimant only)"
)
def withdraw_claim(
    claim_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """Withdraw an active pending claim. Withdrawn claims cannot be reactivated."""
    return ClaimService.withdraw_claim(db, current_user, claim_id)
