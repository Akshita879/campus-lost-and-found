import datetime
import email_validator
from pydantic import BaseModel, EmailStr, Field, ConfigDict

# Disable DNS deliverability checks so validation is instantaneous and offline-compatible
email_validator.CHECK_DELIVERABILITY = False


class UserRegisterRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=100, description="Full name of user")
    email: EmailStr = Field(..., description="Valid campus email address")
    password: str = Field(..., min_length=8, max_length=128, description="Password with minimum 8 characters")


class UserLoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: int
    name: str
    email: EmailStr
    created_at: datetime.datetime

    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
