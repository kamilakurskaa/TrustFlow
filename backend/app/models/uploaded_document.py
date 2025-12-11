from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from sqlalchemy.sql import func
from ..database import Base


class UploadedDocument(Base):
    """Модель для загруженных документов (PDF с Госуслуг и т.д.)"""

    __tablename__ = "uploaded_documents"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    user_id = Column(Integer, index=True, nullable=False)

    # Информация о файле
    filename = Column(String, nullable=False)
    file_path = Column(String, nullable=False)  # Путь к файлу на диске
    file_size = Column(Integer)  # Размер в байтах
    mime_type = Column(String, default="application/pdf")

    # Тип документа
    document_type = Column(String, default="gosuslugi")  # gosuslugi, bank_statement, passport, etc

    # Данные из документа
    parsed_data = Column(JSON, nullable=True)  # Извлеченные данные (JSON)
    extracted_text = Column(Text, nullable=True)  # Текст из PDF
    is_parsed = Column(Boolean, default=False)  # Парсинг выполнен?
    parsing_error = Column(String, nullable=True)  # Ошибка парсинга

    # Верификация
    is_verified = Column(Boolean, default=False)  # Документ верифицирован?
    verification_method = Column(String)  # manual, automated, blockchain
    verified_by = Column(Integer, nullable=True)  # ID администратора/системы
    verification_date = Column(DateTime(timezone=True), nullable=True)

    # Блокчейн
    blockchain_hash = Column(String, nullable=True)  # Хеш документа в блокчейне
    transaction_hash = Column(String, nullable=True)  # Транзакция в блокчейне

    # Статус
    status = Column(String, default="pending")  # pending, processing, completed, failed, rejected

    # Метаданные
    document_metadata = Column(JSON, nullable=True)  # Дополнительные метаданные

    # Временные метки
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    deleted_at = Column(DateTime(timezone=True), nullable=True)  # Мягкое удаление

    def __repr__(self):
        return f"<UploadedDocument(id={self.id}, user_id={self.user_id}, filename='{self.filename}')>"