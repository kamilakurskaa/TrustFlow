from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.blockchain import BlockchainRecord
from ..models.credit import CreditReport, ParserJob

from ..schemas.credit import CreditScoreRequest, CreditScoreResponse, CreditRequestResponse
from ..auth.security import get_current_user
from ..config import settings
from datetime import datetime
import random
import hashlib
import json


router = APIRouter()


# Заглушка для ML модели
def calculate_mock_score(user_data: dict) -> dict:
    """Мок расчет кредитного скора"""
    base_score = random.randint(300, 850)

    if base_score >= 720:
        category = "excellent"
    elif base_score >= 680:
        category = "good"
    elif base_score >= 620:
        category = "fair"
    elif base_score >= 580:
        category = "poor"
    else:
        category = "bad"

    return {
        "score": base_score,
        "category": category,
        "reputation_score": base_score / 850,
        "factors": {
            "payment_history": random.choice(["excellent", "good", "fair", "poor"]),
            "credit_utilization": random.randint(10, 80),
            "credit_age": random.randint(1, 20)
        }
    }


def generate_blockchain_hash(data: dict) -> str:
    """Генерация хеша для блокчейна"""
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_str.encode()).hexdigest()


def mock_blockchain_transaction(data_hash: str, user_id: int) -> dict:
    """Мок транзакции в блокчейне"""
    # В реальности здесь будет вызов web3.eth.send_transaction()
    return {
        "transaction_hash": f"0x{hashlib.sha256(data_hash.encode()).hexdigest()[:64]}",
        "block_number": random.randint(1000000, 2000000),
        "success": True
    }


@router.post("/request", response_model=CreditRequestResponse)
def request_credit_score(
        request_data: CreditScoreRequest,
        background_tasks: BackgroundTasks,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Запрос расчета кредитного скора"""

    credit_request = CreditScoreRequest(
        user_id=current_user.id,
        status="processing",
        blockchain_recorded=request_data.use_blockchain
    )
    db.add(credit_request)
    db.commit()
    db.refresh(credit_request)

    background_tasks.add_task(
        process_credit_score_background,
        credit_request.id,
        current_user.id,
        request_data.dict(),
        db
    )

    return credit_request


@router.get("/score", response_model=CreditScoreResponse)
def get_credit_score(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Получение последнего кредитного отчета"""

    report = db.query(CreditReport).filter(
        CreditReport.user_id == current_user.id
    ).order_by(CreditReport.created_at.desc()).first()

    if not report:
        raise HTTPException(status_code=404, detail="Кредитный отчет не найден")

    return report


@router.get("/score/{report_id}")
def get_score_by_id(
        report_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Получение конкретного отчета по ID"""

    report = db.query(CreditReport).filter(
        CreditReport.id == report_id,
        CreditReport.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Отчет не найден")

    return report


@router.get("/history")
def get_credit_history(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """История всех отчетов"""

    reports = db.query(CreditReport).filter(
        CreditReport.user_id == current_user.id
    ).order_by(CreditReport.created_at.desc()).all()

    return reports


@router.get("/blockchain-records")
def get_blockchain_records(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Получение записей в блокчейне (будущая функциональность)"""

    # Пока возвращаем заглушку
    return {
        "message": "Блокчейн интеграция в разработке",
        "user_id": current_user.id,
        "wallet_address": current_user.wallet_address
    }


@router.post("/verify-on-blockchain/{report_id}")
def verify_on_blockchain(
        report_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Верификация отчета в блокчейне"""

    report = db.query(CreditReport).filter(
        CreditReport.id == report_id,
        CreditReport.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Отчет не найден")

    if not report.blockchain_hash:
        raise HTTPException(status_code=400, detail="Отчет не записан в блокчейн")

    # Мок верификация
    verification_data = {
        "report_id": report.id,
        "user_id": report.user_id,
        "score": report.score,
        "blockchain_hash": report.blockchain_hash,
        "transaction_hash": report.transaction_hash,
        "verified": True,
        "verified_at": datetime.utcnow().isoformat()
    }

    return verification_data


def process_credit_score_background(request_id: int, user_id: int, request_data: dict, db: Session):
    """Фоновая задача расчета скора"""
    try:
        request = db.query(CreditScoreRequest).filter(CreditScoreRequest.id == request_id).first()
        user = db.query(User).filter(User.id == user_id).first()

        # Мок расчет
        score_data = calculate_mock_score({})

        # Подготовка данных для хеширования
        report_data = {
            "user_id": user_id,
            "score": score_data["score"],
            "category": score_data["category"],
            "calculated_at": datetime.utcnow().isoformat(),
            "factors": score_data["factors"]
        }

        blockchain_hash = None
        transaction_hash = None
        block_number = None

        # Запись в блокчейн если требуется
        if request_data.get("use_blockchain", False) and user.wallet_address:
            try:
                # Генерируем хеш данных
                data_hash = generate_blockchain_hash(report_data)

                # Мок транзакция в блокчейне
                tx_result = mock_blockchain_transaction(data_hash, user_id)

                blockchain_hash = data_hash
                transaction_hash = tx_result["transaction_hash"]
                block_number = tx_result["block_number"]

                # Сохраняем запись о блокчейн-транзакции
                blockchain_record = BlockchainRecord(
                    user_id=user_id,
                    transaction_type="credit_report",
                    transaction_hash=transaction_hash,
                    block_number=block_number,
                    contract_address=settings.CONTRACT_ADDRESS or "0x0000000000000000000000000000000000000000",
                    data_hash=data_hash,
                    confirmed=True
                )
                db.add(blockchain_record)

                request.blockchain_recorded = True

            except Exception as e:
                print(f"Ошибка блокчейн-записи: {e}")
                # Продолжаем без блокчейна

        # Создаем отчет
        report = CreditReport(
            user_id=user_id,
            score=score_data["score"],
            score_category=score_data["category"],
            reputation_score=score_data["reputation_score"],
            report_data=report_data,
            blockchain_hash=blockchain_hash,
            transaction_hash=transaction_hash,
            block_number=block_number
        )
        db.add(report)

        # Обновляем репутационный счет пользователя
        user.reputation_score = score_data["reputation_score"]

        # Завершаем запрос
        request.status = "completed"
        db.commit()

    except Exception as e:
        request = db.query(CreditScoreRequest).filter(CreditScoreRequest.id == request_id).first()
        request.status = "failed"
        db.commit()
        print(f"Ошибка расчета скора: {e}")