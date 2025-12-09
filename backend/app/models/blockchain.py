from sqlalchemy import Column, Integer, String, DateTime, JSON
from sqlalchemy.sql import func
from backend.app.database import Base


class BlockchainRecord(Base):
    __tablename__ = "blockchain_records"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    transaction_hash = Column(String, unique=True)
    block_number = Column(Integer)
    contract_address = Column(String)
    data_hash = Column(String)  # Хеш данных для верификации
    data_type = Column(String)  # credit_report, user_consent, data_source
    transaction_data = Column(JSON)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
