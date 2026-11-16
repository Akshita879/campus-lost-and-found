from typing import List, Tuple
from sqlalchemy.orm import Session
from sqlalchemy import func
from fastapi import HTTPException, status

from app.models.user import User
from app.models.report import Report
from app.models.claim import Claim
from app.models.notification import Notification
from app.schemas.user import AdminUserResponse
from app.utils.image_handler import delete_uploaded_image


class AdminService:
    @staticmethod
    def list_users(db: Session) -> List[AdminUserResponse]:
        rows = (
            db.query(
                User,
                func.count(Report.id.distinct()).label("reports_count"),
                func.count(Claim.id.distinct()).label("claims_count"),
            )
            .outerjoin(Report, Report.user_id == User.id)
            .outerjoin(Claim, Claim.claimant_id == User.id)
            .group_by(User.id)
            .order_by(User.created_at.desc())
            .all()
        )
        result = []
        for user, reports_count, claims_count in rows:
            result.append(
                AdminUserResponse(
                    id=user.id,
                    name=user.name,
                    email=user.email,
                    is_admin=bool(user.is_admin),
                    created_at=user.created_at,
                    reports_count=int(reports_count or 0),
                    claims_count=int(claims_count or 0),
                )
            )
        return result

    @staticmethod
    def delete_user(db: Session, admin: User, user_id: int) -> dict:
        if user_id == admin.id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot delete your own admin account")
        user = db.query(User).filter(User.id == user_id).first()
        if not user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
        if user.is_admin:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot delete another admin account")

        # Clean uploaded images for their reports
        for report in db.query(Report).filter(Report.user_id == user_id).all():
            if report.image_path:
                delete_uploaded_image(report.image_path)

        db.delete(user)
        db.commit()
        return {"success": True, "deleted_user_id": user_id}

    @staticmethod
    def list_reports(db: Session) -> List[Report]:
        return db.query(Report).order_by(Report.created_at.desc()).limit(500).all()

    @staticmethod
    def delete_report(db: Session, report_id: int) -> dict:
        report = db.query(Report).filter(Report.id == report_id).first()
        if not report:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
        if report.image_path:
            delete_uploaded_image(report.image_path)
        db.delete(report)
        db.commit()
        return {"success": True, "deleted_report_id": report_id}

    @staticmethod
    def clear_all_reports(db: Session) -> dict:
        reports = db.query(Report).all()
        for report in reports:
            if report.image_path:
                delete_uploaded_image(report.image_path)
        deleted_reports = db.query(Report).delete()
        deleted_claims = db.query(Claim).delete()
        deleted_notes = db.query(Notification).delete()
        db.commit()
        return {
            "success": True,
            "deleted_reports": deleted_reports,
            "deleted_claims": deleted_claims,
            "deleted_notifications": deleted_notes,
        }
