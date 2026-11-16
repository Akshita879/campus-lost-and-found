from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.schemas.matching import UserMatchesResponse
from app.services.matching_service import MatchingService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/matches", tags=["Matches"])


@router.get(
    "",
    response_model=UserMatchesResponse,
    summary="Get suggested matches for the current user's lost reports",
)
def get_my_matches(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    """
    Returns ranked LOST↔FOUND match pairs for every active lost report owned by
    the authenticated user. Uses the same deterministic matching engine as
    GET /reports/{id}/matches.
    """
    return MatchingService.find_matches_for_user(db, current_user.id)
