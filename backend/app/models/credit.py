from sqlalchemy import Column, Float, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from backend.app.database import Base

class CreditReport(Base):
    __tablename__ = "credit_reports"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=False)
    score = Column(Integer)
    score_category = Column(String)
    reputation_score = Column(Float)
    report_data = Column(Text)  # Все собранные данные
    blockchain_hash = Column(String, nullable=True)  # Хеш в блокчейне
    transaction_hash = Column(String, nullable=True)  # Транзакция в блокчейне
    block_number = Column(Integer, nullable=True)  # Номер блока
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ParserJob(Base):
    __tablename__ = "parser_jobs"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=False)
    status = Column(String)  # pending, processing, completed, failed
    data_sources = Column(Text)  # Источники данных для парсинга
    result_data = Column(Text)  # Результаты парсинга
    error_message = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))


class CreditRequest(Base):
    __tablename__ = "credit_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    status = Column(String, default="pending")  # pending, processing, completed, failed
    blockchain_recorded = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())