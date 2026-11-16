from fastapi import APIRouter, Depends, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from typing import Optional
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserRegisterRequest, UserLoginRequest, UserResponse, TokenResponse
from app.services.auth_service import AuthService
from app.utils.dependencies import get_current_user

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Register a new user account"
)
def register(
    data: UserRegisterRequest,
    db: Session = Depends(get_db)
):
    """
    Register a new student or staff user.
    - **name**: Full name (2-100 characters)
    - **email**: Valid campus email address
    - **password**: Secure password (minimum 8 characters)
    """
    user = AuthService.register_user(db, data)
    return user


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="Login and obtain a JWT access token"
)
async def login(
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Authenticate with email and password.
    Supports either JSON body (`{"email": "...", "password": "..."}`)
    or form data (`username`=email, `password`).
    """
    content_type = request.headers.get("content-type", "")
    if "application/json" in content_type:
        body = await request.json()
        email = body.get("email") or body.get("username")
        password = body.get("password")
    else:
        form = await request.form()
        email = form.get("username") or form.get("email")
        password = form.get("password")

    if not email or not password:
        from fastapi import HTTPException
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email/username and password are required"
        )

    user = AuthService.authenticate_user(db, str(email), str(password))
    return AuthService.create_token_for_user(user)


@router.get(
    "/me",
    response_model=UserResponse,
    summary="Get current authenticated user profile"
)
def get_me(current_user: User = Depends(get_current_user)):
    """Retrieve profile details of the currently authenticated user."""
    return current_user
