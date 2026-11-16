from app.routers.auth import router as auth_router
from app.routers.reports import router as reports_router
from app.routers.claims import router as claims_router
from app.routers.matches import router as matches_router

__all__ = [
    "auth_router",
    "reports_router",
    "claims_router",
    "matches_router",
]
