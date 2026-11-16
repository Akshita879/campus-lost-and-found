from typing import List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from app.models.notification import Notification
from app.models.user import User


class NotificationService:
    @staticmethod
    def create(
        db: Session,
        user_id: int,
        title: str,
        body: str,
        *,
        kind: Optional[str] = None,
        claim_id: Optional[int] = None,
        report_id: Optional[int] = None,
        commit: bool = True,
    ) -> Notification:
        note = Notification(
            user_id=user_id,
            title=title,
            body=body,
            is_read=False,
            kind=kind,
            claim_id=claim_id,
            report_id=report_id,
        )
        db.add(note)
        if commit:
            db.commit()
            db.refresh(note)
        else:
            db.flush()
        return note

    @staticmethod
    def list_for_user(db: Session, user: User) -> List[Notification]:
        return (
            db.query(Notification)
            .filter(Notification.user_id == user.id)
            .order_by(Notification.created_at.desc())
            .limit(50)
            .all()
        )

    @staticmethod
    def mark_all_read(db: Session, user: User) -> int:
        updated = (
            db.query(Notification)
            .filter(Notification.user_id == user.id, Notification.is_read.is_(False))
            .update({Notification.is_read: True}, synchronize_session=False)
        )
        db.commit()
        return updated

    @staticmethod
    def delete_for_user(db: Session, user: User, notification_id: int) -> dict:
        note = (
            db.query(Notification)
            .filter(Notification.id == notification_id, Notification.user_id == user.id)
            .first()
        )
        if not note:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Notification not found")
        db.delete(note)
        db.commit()
        return {"success": True, "deleted_id": notification_id}
