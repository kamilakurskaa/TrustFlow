from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func
from ..database.database import Base

class CreditReport(Base):
    __tablename__ = "credit_reports"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    score = Column(Integer)
    score_category = Column(String)
    report_data = Column(JSON)  # Все собранные данные
    factors = Column(JSON)  # Факторы влияния на score
    created_at = Column(DateTime(timezone=True), server_default=func.now())

class ParserJob(Base):
    __tablename__ = "parser_jobs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True, nullable=False)
    status = Column(String)  # pending, processing, completed, failed
    data_sources = Column(JSON)  # Источники данных для парсинга
    result_data = Column(JSON)  # Результаты парсинга
    error_message = Column(String)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    completed_at = Column(DateTime(timezone=True))