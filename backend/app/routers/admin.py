from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.report import ReportPublicResponse
from app.schemas.user import AdminUserResponse
from app.services.admin_service import AdminService
from app.utils.dependencies import get_current_admin

router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users", response_model=List[AdminUserResponse], summary="List all users")
def admin_list_users(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return AdminService.list_users(db)


@router.delete("/users/{user_id}", summary="Delete a user account")
def admin_delete_user(
    user_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return AdminService.delete_user(db, admin, user_id)


@router.get("/reports", response_model=List[ReportPublicResponse], summary="List all reports")
def admin_list_reports(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return AdminService.list_reports(db)


@router.delete("/reports/{report_id}", summary="Delete any lost/found report")
def admin_delete_report(
    report_id: int,
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return AdminService.delete_report(db, report_id)


@router.post("/clear-reports", summary="Delete all reports, claims, and notifications")
def admin_clear_reports(
    admin: User = Depends(get_current_admin),
    db: Session = Depends(get_db),
):
    return AdminService.clear_all_reports(db)
