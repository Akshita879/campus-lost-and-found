from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models.user import User
from app.schemas.user import UserRegisterRequest, TokenResponse, UserResponse
from app.utils.security import hash_password, verify_password, create_access_token


class AuthService:
    @staticmethod
    def register_user(db: Session, data: UserRegisterRequest) -> User:
        # Check if email is already registered
        existing_user = db.query(User).filter(User.email == data.email.lower().strip()).first()
        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="An account with this email address already exists"
            )

        hashed = hash_password(data.password)
        new_user = User(
            name=data.name.strip(),
            email=data.email.lower().strip(),
            password_hash=hashed
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return new_user

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> User:
        user = db.query(User).filter(User.email == email.lower().strip()).first()
        if not user or not verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    @staticmethod
    def create_token_for_user(user: User) -> TokenResponse:
        token = create_access_token(subject=user.id)
        return TokenResponse(
            access_token=token,
            token_type="bearer",
            user=UserResponse.model_validate(user)
        )
