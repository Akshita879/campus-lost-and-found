import datetime
import math
from typing import Optional, Tuple, List
from sqlalchemy.orm import Session
from sqlalchemy import or_, and_
from fastapi import HTTPException, status, UploadFile
from app.models.user import User
from app.models.report import Report, ReportType, ReportStatus
from app.schemas.report import ReportCreateRequest, ReportUpdateRequest
from app.utils.image_handler import save_uploaded_image, delete_uploaded_image


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

        report = Report(
            user_id=user.id,
            item_name=data.item_name.strip(),
            category=data.category.strip(),
            description=data.description.strip(),
            report_type=data.report_type,
            approximate_date=data.approximate_date,
            location=data.location.strip(),
            image_path=image_path,
            status=ReportStatus.ACTIVE
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        return report

    @staticmethod
    def get_report_by_id(db: Session, report_id: int) -> Report:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Report with ID {report_id} not found"
            )
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
