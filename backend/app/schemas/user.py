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

    has_credit_history: Optional[bool] = None  # Новое поле
    consent_data_processing: bool = Field(default=False)  # Новое поле

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserResponse(UserBase):
    id: int
    is_active: bool
    is_verified: bool
    reputation_score: float
    wallet_address: Optional[str]

    has_credit_history: Optional[bool]  # Новое поле
    blockchain_user_id: Optional[str]  # Новое поле

    created_at: datetime

    class Config:
        from_attributes = True

# Новые схемы
class CreditHistoryChoice(BaseModel):
    has_credit_history: bool
    consent_data_processing: bool = True


class DocumentUpload(BaseModel):
    document_type: str = "gosuslugi"


class UploadedDocumentResponse(BaseModel):
    id: int
    filename: str
    document_type: str
    is_verified: bool
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