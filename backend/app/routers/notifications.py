from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.notification import NotificationListResponse, NotificationResponse
from app.services.notification_service import NotificationService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/notifications", tags=["Notifications"])


@router.get(
    "",
    response_model=NotificationListResponse,
    summary="List notifications for the current user",
)
def list_notifications(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    notes = NotificationService.list_for_user(db, current_user)
    unread = sum(1 for n in notes if not n.is_read)
    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n) for n in notes],
        unread_count=unread,
    )


@router.post(
    "/read-all",
    response_model=NotificationListResponse,
    summary="Mark all notifications as read",
)
def mark_all_read(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    NotificationService.mark_all_read(db, current_user)
    notes = NotificationService.list_for_user(db, current_user)
    return NotificationListResponse(
        notifications=[NotificationResponse.model_validate(n) for n in notes],
        unread_count=0,
    )


@router.delete(
    "/{notification_id}",
    summary="Delete one notification",
)
def delete_notification(
    notification_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return NotificationService.delete_for_user(db, current_user, notification_id)
