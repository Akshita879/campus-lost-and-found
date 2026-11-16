import datetime
from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.models.report import Report, ReportType, ReportStatus
from app.models.claim import Claim, ClaimStatus
from app.schemas.claim import ClaimCreateRequest


class ClaimService:
    @staticmethod
    def create_claim(db: Session, user: User, data: ClaimCreateRequest) -> Claim:
        # 1. Target report must exist
        found_report = db.query(Report).filter(Report.id == data.report_id).first()
        if not found_report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report with ID {data.report_id} not found"
            )

        # 2. Must be a FOUND report
        if found_report.report_type != ReportType.FOUND:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Claims can only be filed against FOUND item reports"
            )

        # 3. Target report must be ACTIVE
        if found_report.status != ReportStatus.ACTIVE:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot claim an item with status '{found_report.status}'. Item must be ACTIVE."
            )

        # 4. User cannot claim their own found report
        if found_report.user_id == user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot submit a claim against an item you reported as found"
            )

        # 5. Validate linked lost_report_id if provided
        if data.lost_report_id is not None:
            lost_report = db.query(Report).filter(Report.id == data.lost_report_id).first()
            if not lost_report:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Linked lost report with ID {data.lost_report_id} does not exist"
                )
            if lost_report.user_id != user.id:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Linked lost report must belong to the claimant"
                )
            if lost_report.report_type != ReportType.LOST:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Linked report must be of type LOST"
                )

        # 6. Prevent duplicate active (PENDING) claims by the same claimant for the same found report
        existing_active_claim = (
            db.query(Claim)
            .filter(
                Claim.report_id == data.report_id,
                Claim.claimant_id == user.id,
                Claim.status == ClaimStatus.PENDING
            )
            .first()
        )
        if existing_active_claim:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="You already have an active pending claim for this item"
            )

        # 7. Create claim
        claim = Claim(
            report_id=data.report_id,
            claimant_id=user.id,
            lost_report_id=data.lost_report_id,
            verification_details=data.verification_details.strip(),
            status=ClaimStatus.PENDING
        )
        db.add(claim)
        db.commit()
        db.refresh(claim)
        return claim

    @staticmethod
    def get_user_claims(db: Session, user: User) -> List[Claim]:
        """Returns all claims submitted by the authenticated claimant."""
        return (
            db.query(Claim)
            .filter(Claim.claimant_id == user.id)
            .order_by(Claim.created_at.desc())
            .all()
        )

    @staticmethod
    def get_claim_by_id(db: Session, user: User, claim_id: int) -> Claim:
        """Retrieves a specific claim ensuring privacy restrictions."""
        claim = db.query(Claim).filter(Claim.id == claim_id).first()
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Claim with ID {claim_id} not found"
            )

        # Only the claimant can access their claim details in this MVP
        if claim.claimant_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: Verification details and claims are strictly private"
            )

        return claim

    @staticmethod
    def withdraw_claim(db: Session, user: User, claim_id: int) -> Claim:
        """Allows claimant to withdraw their pending claim."""
        claim = ClaimService.get_claim_by_id(db, user, claim_id)

        if claim.status != ClaimStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot withdraw claim with status '{claim.status}'. Only PENDING claims can be withdrawn."
            )

        claim.status = ClaimStatus.WITHDRAWN
        claim.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(claim)
        return claim
