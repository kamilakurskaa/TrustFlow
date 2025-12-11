from sqlalchemy import Column, Integer, String, Boolean, DateTime, Float, JSON
from sqlalchemy.sql import func
from sqlalchemy.dialects.postgresql import JSON
from ..database import Base

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


    has_credit_history = Column(Boolean, nullable=True)  # Есть/нет кредитная история
    consent_data_processing = Column(Boolean, default=False)  # Согласие на обработку
    blockchain_user_id = Column(String, nullable=True)  # ID в блокчейне

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


class UploadedDocument(Base):
    __tablename__ = "uploaded_documents"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    filename = Column(String)
    file_path = Column(String)
    document_type = Column(String)  # gosuslugi, bank_statement, etc
    parsed_data = Column(JSON)  # Извлеченные данные
    is_verified = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())