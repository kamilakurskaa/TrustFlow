from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None
    phone: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    wallet_address: Optional[str] = None

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    reputation_score: float
    wallet_address: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

class ProfileBase(BaseModel):
    date_of_birth: Optional[str] = None
    address: Optional[str] = None
    employment_status: Optional[str] = None
    monthly_income: Optional[int] = None

class ProfileResponse(ProfileBase):
    user_id: int
    created_at: datetime

    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse