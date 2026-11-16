import datetime
from typing import List
from sqlalchemy.orm import Session, joinedload
from fastapi import HTTPException, status
from app.models.user import User
from app.models.report import Report, ReportType, ReportStatus
from app.models.claim import Claim, ClaimStatus
from app.schemas.claim import ClaimCreateRequest
from app.services.notification_service import NotificationService
from app.services.report_service import _norm_answer


class ClaimService:
    @staticmethod
    def _expected_answer_for_found(db: Session, found_report: Report) -> str | None:
        if found_report.related_lost_report_id:
            lost = db.query(Report).filter(Report.id == found_report.related_lost_report_id).first()
            if lost and lost.verification_answer:
                return lost.verification_answer
        if found_report.verification_answer:
            return found_report.verification_answer
        return None

    @staticmethod
    def create_claim(db: Session, user: User, data: ClaimCreateRequest) -> Claim:
        found_report = db.query(Report).filter(Report.id == data.report_id).first()
        if not found_report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report with ID {data.report_id} not found"
            )

        if found_report.report_type != ReportType.FOUND:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Claims can only be filed against FOUND item reports"
            )

        if found_report.status not in (ReportStatus.ACTIVE, ReportStatus.CLAIM_PENDING):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot claim an item with status '{found_report.status}'."
            )

        if found_report.user_id == user.id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You cannot submit a claim against an item you reported as found"
            )

        # Linked finds already verified on report create — owner uses /reports/{id}/meetup
        if found_report.related_lost_report_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="This find is already linked and verified. Share meetup details from Notifications.",
            )

        lost_report_id = data.lost_report_id
        if lost_report_id is None and found_report.related_lost_report_id:
            # Auto-link to the related lost report when the claimant owns it
            related = db.query(Report).filter(Report.id == found_report.related_lost_report_id).first()
            if related and related.user_id == user.id:
                lost_report_id = related.id

        if lost_report_id is not None:
            lost_report = db.query(Report).filter(Report.id == lost_report_id).first()
            if not lost_report:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Linked lost report with ID {lost_report_id} does not exist"
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

        expected = ClaimService._expected_answer_for_found(db, found_report)
        if expected is not None:
            if _norm_answer(data.verification_details) != _norm_answer(expected):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Verification answer does not match. Please answer the owner's question exactly."
                )

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

        claim = Claim(
            report_id=data.report_id,
            claimant_id=user.id,
            lost_report_id=lost_report_id,
            verification_details=data.verification_details.strip(),
            status=ClaimStatus.PENDING
        )
        db.add(claim)
        found_report.status = ReportStatus.CLAIM_PENDING
        db.flush()

        # Claimant shares meetup next; finder only receives info (no chat / reply)
        NotificationService.create(
            db,
            user.id,
            title="Claim matched — share meetup details",
            body=(
                f"Your answer matched for “{found_report.item_name}” (found report #{found_report.id}). "
                f"Add where/when you can meet so the finder knows how to hand it over."
            ),
            kind="claim_needs_meetup",
            claim_id=claim.id,
            report_id=found_report.id,
            commit=False,
        )

        db.commit()
        db.refresh(claim)
        return claim

    @staticmethod
    def set_meetup_message(db: Session, user: User, claim_id: int, meetup_message: str) -> Claim:
        claim = ClaimService.get_claim_by_id(db, user, claim_id)
        if claim.claimant_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the claimant can set meetup details",
            )
        if claim.status not in (ClaimStatus.PENDING, ClaimStatus.APPROVED):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot add meetup details when claim status is '{claim.status}'",
            )
        message = meetup_message.strip()
        if len(message) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Meetup details must be at least 10 characters",
            )

        claim.meetup_message = message
        claim.updated_at = datetime.datetime.utcnow()

        from app.models.notification import Notification

        owner_notes = (
            db.query(Notification)
            .filter(
                Notification.user_id == user.id,
                Notification.kind == "claim_needs_meetup",
                Notification.claim_id == claim.id,
            )
            .all()
        )
        for note in owner_notes:
            note.kind = "meetup_sent"
            note.title = "Meetup details sent"
            note.body = (
                f"You told the finder where to meet for “{claim.report.item_name}”:\n\n{message}"
            )
            note.is_read = True

        holder_id = claim.report.user_id if claim.report else None
        if holder_id:
            NotificationService.create(
                db,
                holder_id,
                title="Got it — meetup details from the owner",
                body=(
                    f"Thanks for finding “{claim.report.item_name}”. "
                    f"You can meet them here:\n\n{message}"
                ),
                kind="meetup_shared",
                claim_id=claim.id,
                report_id=claim.report_id,
                commit=False,
            )

        db.commit()
        db.refresh(claim)
        return claim

    @staticmethod
    def get_user_claims(db: Session, user: User) -> List[Claim]:
        return (
            db.query(Claim)
            .filter(Claim.claimant_id == user.id)
            .order_by(Claim.created_at.desc())
            .all()
        )

    @staticmethod
    def get_incoming_claims(db: Session, user: User) -> List[Claim]:
        """Claims on FOUND reports owned by the current user (holder reviews these)."""
        return (
            db.query(Claim)
            .join(Report, Claim.report_id == Report.id)
            .options(joinedload(Claim.report), joinedload(Claim.claimant))
            .filter(Report.user_id == user.id, Report.report_type == ReportType.FOUND)
            .order_by(Claim.created_at.desc())
            .all()
        )

    @staticmethod
    def get_claim_by_id(db: Session, user: User, claim_id: int) -> Claim:
        claim = (
            db.query(Claim)
            .options(joinedload(Claim.report), joinedload(Claim.lost_report), joinedload(Claim.claimant))
            .filter(Claim.id == claim_id)
            .first()
        )
        if not claim:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Claim with ID {claim_id} not found"
            )

        is_claimant = claim.claimant_id == user.id
        is_holder = claim.report and claim.report.user_id == user.id
        if not (is_claimant or is_holder):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied for this claim"
            )
        return claim

    @staticmethod
    def withdraw_claim(db: Session, user: User, claim_id: int) -> Claim:
        claim = ClaimService.get_claim_by_id(db, user, claim_id)
        if claim.claimant_id != user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the claimant can withdraw")
        if claim.status != ClaimStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot withdraw claim with status '{claim.status}'."
            )
        claim.status = ClaimStatus.WITHDRAWN
        claim.updated_at = datetime.datetime.utcnow()
        if claim.report and claim.report.status == ReportStatus.CLAIM_PENDING:
            claim.report.status = ReportStatus.ACTIVE
        db.commit()
        db.refresh(claim)
        return claim

    @staticmethod
    def approve_claim(db: Session, user: User, claim_id: int) -> Claim:
        claim = ClaimService.get_claim_by_id(db, user, claim_id)
        if not claim.report or claim.report.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the person who found/holds the item can approve this claim"
            )
        if claim.status != ClaimStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot approve claim with status '{claim.status}'"
            )

        claim.status = ClaimStatus.APPROVED
        claim.updated_at = datetime.datetime.utcnow()
        claim.report.status = ReportStatus.RESOLVED
        if claim.lost_report_id:
            lost = db.query(Report).filter(Report.id == claim.lost_report_id).first()
            if lost:
                lost.status = ReportStatus.RESOLVED

        NotificationService.create(
            db,
            claim.claimant_id,
            title="Claim approved — come collect your item",
            body=(
                f"{user.name} approved your claim for “{claim.report.item_name}” "
                f"(found report #{claim.report_id}). Arrange a campus meetup/pickup with them."
            ),
            kind="claim_approved",
            claim_id=claim.id,
            commit=False,
        )
        db.commit()
        db.refresh(claim)
        return claim

    @staticmethod
    def reject_claim(db: Session, user: User, claim_id: int) -> Claim:
        claim = ClaimService.get_claim_by_id(db, user, claim_id)
        if not claim.report or claim.report.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the person who found/holds the item can reject this claim"
            )
        if claim.status != ClaimStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Cannot reject claim with status '{claim.status}'"
            )

        claim.status = ClaimStatus.REJECTED
        claim.updated_at = datetime.datetime.utcnow()
        claim.report.status = ReportStatus.ACTIVE

        NotificationService.create(
            db,
            claim.claimant_id,
            title="Claim rejected",
            body=(
                f"Your claim for “{claim.report.item_name}” (found report #{claim.report_id}) "
                f"was rejected by the finder."
            ),
            kind="claim_rejected",
            claim_id=claim.id,
            commit=False,
        )
        db.commit()
        db.refresh(claim)
        return claim
