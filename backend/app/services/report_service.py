import datetime
import math
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException, status, UploadFile
from app.models.user import User
from app.models.report import Report, ReportType, ReportStatus
from app.schemas.report import ReportCreateRequest, ReportUpdateRequest
from app.services.notification_service import NotificationService
from app.utils.image_handler import save_uploaded_image, delete_uploaded_image


def _norm_answer(value: Optional[str]) -> str:
    return " ".join((value or "").strip().lower().split())


class ReportService:
    @staticmethod
    async def create_report(
        db: Session,
        user: User,
        data: ReportCreateRequest,
        image_file: Optional[UploadFile] = None
    ) -> Report:
        image_path = None
        if image_file and image_file.filename:
            image_path = await save_uploaded_image(image_file)

        related_lost = None
        verification_question = data.verification_question.strip() if data.verification_question else None
        verification_answer = data.verification_answer.strip() if data.verification_answer else None

        if data.related_lost_report_id is not None:
            if data.report_type != ReportType.FOUND:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="related_lost_report_id can only be set on FOUND reports",
                )
            related_lost = db.query(Report).filter(Report.id == data.related_lost_report_id).first()
            if not related_lost or related_lost.report_type != ReportType.LOST:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Related lost report not found",
                )
            if related_lost.user_id == user.id:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="You cannot mark your own lost report as found by yourself this way",
                )
            if not related_lost.verification_question:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="This lost listing has no verification question set by the owner",
                )
            if _norm_answer(verification_answer) != _norm_answer(related_lost.verification_answer):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Verification answer does not match the owner's answer. Check the item and try again.",
                )
            # Copy question onto found listing for display; never store owner's secret answer there
            verification_question = related_lost.verification_question
            verification_answer = None

        report = Report(
            user_id=user.id,
            item_name=data.item_name.strip(),
            category=data.category.strip(),
            description=data.description.strip(),
            report_type=data.report_type,
            approximate_date=data.approximate_date,
            location=data.location.strip(),
            image_path=image_path,
            verification_question=verification_question,
            verification_answer=verification_answer if data.report_type == ReportType.LOST else None,
            related_lost_report_id=related_lost.id if related_lost else None,
            status=ReportStatus.ACTIVE,
        )
        db.add(report)
        db.flush()

        if related_lost is not None:
            # Lost owner (A) is prompted to send meetup details — no second verification / claim step
            NotificationService.create(
                db,
                related_lost.user_id,
                title="Someone found your item",
                body=(
                    f"{user.name} verified and reported finding “{related_lost.item_name}” "
                    f"(found listing #{report.id}). Share where/when you can meet so they can hand it over."
                ),
                kind="found_linked",
                report_id=report.id,
                commit=False,
            )

        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def set_meetup_for_found(db: Session, user: User, found_report_id: int, meetup_message: str) -> Report:
        """Lost owner sends meetup details to the finder after a verified linked find."""
        found = db.query(Report).filter(Report.id == found_report_id).first()
        if not found or found.report_type != ReportType.FOUND:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Found report not found")
        if not found.related_lost_report_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Meetup details are only for finds linked to a lost report",
            )
        lost = db.query(Report).filter(Report.id == found.related_lost_report_id).first()
        if not lost or lost.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only the owner of the related lost report can set meetup details",
            )
        message = meetup_message.strip()
        if len(message) < 10:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Meetup details must be at least 10 characters",
            )

        found.meetup_message = message
        found.updated_at = datetime.datetime.utcnow()

        # Owner's prompt becomes a confirmation (no second form / re-verify)
        from app.models.notification import Notification

        owner_notes = (
            db.query(Notification)
            .filter(
                Notification.user_id == user.id,
                Notification.kind == "found_linked",
                Notification.report_id == found.id,
            )
            .all()
        )
        for note in owner_notes:
            note.kind = "meetup_sent"
            note.title = "Meetup details sent"
            note.body = (
                f"You told the finder where to meet for “{found.item_name}”:\n\n{message}"
            )
            note.is_read = True

        # Finder (B) gets info only — no reply / approve actions
        NotificationService.create(
            db,
            found.user_id,
            title="Got it — meetup details from the owner",
            body=(
                f"Thanks for finding “{found.item_name}”. "
                f"You can meet them here:\n\n{message}"
            ),
            kind="meetup_shared",
            report_id=found.id,
            commit=False,
        )
        db.commit()
        db.refresh(found)
        return found

    @staticmethod
    def get_report_by_id(db: Session, report_id: int) -> Report:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report with ID {report_id} not found"
            )
        # For FOUND items linked to a LOST report, always surface the owner's question
        if (
            report.report_type == ReportType.FOUND
            and report.related_lost_report_id
            and not report.verification_question
        ):
            lost = db.query(Report).filter(Report.id == report.related_lost_report_id).first()
            if lost and lost.verification_question:
                report.verification_question = lost.verification_question
        return report

    @staticmethod
    def get_user_reports(db: Session, user_id: int) -> List[Report]:
        return db.query(Report).filter(Report.user_id == user_id).order_by(Report.created_at.desc()).all()

    @staticmethod
    async def update_report(
        db: Session,
        user: User,
        report_id: int,
        data: ReportUpdateRequest,
        image_file: Optional[UploadFile] = None
    ) -> Report:
        report = ReportService.get_report_by_id(db, report_id)

        # Ownership validation
        if report.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to modify this report"
            )

        # Status transition check
        if data.status is not None:
            # Users can close their report, but cannot arbitrarily mark it resolved/active without workflow
            if data.status not in [ReportStatus.ACTIVE, ReportStatus.CLOSED]:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid status change to {data.status}. Users may only set ACTIVE or CLOSED."
                )
            report.status = data.status

        if data.item_name is not None:
            report.item_name = data.item_name.strip()
        if data.category is not None:
            report.category = data.category.strip()
        if data.description is not None:
            report.description = data.description.strip()
        if data.approximate_date is not None:
            report.approximate_date = data.approximate_date
        if data.location is not None:
            report.location = data.location.strip()

        if image_file and image_file.filename:
            # Delete old image if exists
            if report.image_path:
                delete_uploaded_image(report.image_path)
            report.image_path = await save_uploaded_image(image_file)

        report.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def close_report(db: Session, user: User, report_id: int) -> Report:
        report = ReportService.get_report_by_id(db, report_id)

        # Ownership validation
        if report.user_id != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have permission to close this report"
            )

        report.status = ReportStatus.CLOSED
        report.updated_at = datetime.datetime.utcnow()
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def search_reports(
        db: Session,
        keyword: Optional[str] = None,
        category: Optional[str] = None,
        report_type: Optional[ReportType] = None,
        location: Optional[str] = None,
        date_from: Optional[datetime.date] = None,
        date_to: Optional[datetime.date] = None,
        status: Optional[ReportStatus] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[Report], int, int]:
        """
        Database-level filtering for reports.
        Returns: (items, total_count, total_pages)
        """
        query = db.query(Report)

        # Default: exclude CLOSED and RESOLVED from active browsing unless explicitly requested
        if status:
            query = query.filter(Report.status == status)
        else:
            query = query.filter(Report.status.in_([ReportStatus.ACTIVE, ReportStatus.CLAIM_PENDING]))

        if report_type:
            query = query.filter(Report.report_type == report_type)

        if category:
            query = query.filter(Report.category.ilike(f"%{category.strip()}%"))

        if location:
            query = query.filter(Report.location.ilike(f"%{location.strip()}%"))

        if date_from:
            query = query.filter(Report.approximate_date >= date_from)

        if date_to:
            query = query.filter(Report.approximate_date <= date_to)

        if keyword:
            kw = f"%{keyword.strip()}%"
            query = query.filter(
                or_(
                    Report.item_name.ilike(kw),
                    Report.description.ilike(kw)
                )
            )

        total_count = query.count()
        total_pages = math.ceil(total_count / page_size) if total_count > 0 else 0

        offset = (page - 1) * page_size
        items = query.order_by(Report.approximate_date.desc(), Report.created_at.desc()).offset(offset).limit(page_size).all()

        return items, total_count, total_pages
