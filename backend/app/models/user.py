from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float
from sqlalchemy.sql import func
from backend.app.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    full_name = Column(String)
    phone = Column(String, unique=True)
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)
    reputation_score = Column(Float, default=0.0)
    wallet_address = Column(String, nullable=True)  # Для блокчейна
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True)
    date_of_birth = Column(String)
    address = Column(String)
    employment_status = Column(String)
    monthly_income = Column(Integer)
    created_at = Column(DateTime(timezone=True), server_default=func.now())