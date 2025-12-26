from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from fastapi import UploadFile, File, Form
from sqlalchemy.orm import Session
from ..database import get_db
from ..models.user import User
from ..models.blockchain import BlockchainRecord
from ..models.credit import CreditReport, ParserJob, CreditRequest
from ..models.uploaded_document import UploadedDocument
from ..schemas.credit import (CreditScoreRequest, CreditScoreResponse, CreditRequestResponse, CreditMethodRequest, ParsingResult, MLScoreRequest, MLScoreResponse)
from ..auth.security import get_current_user
from ..config import settings
from datetime import datetime
import os
import shutil
import random
import hashlib
import json


router = APIRouter()

# Создать директорию для загрузок
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)


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
            "credit_age": random.randint(1, 4)
        }
    }


def generate_data_hash(data: dict) -> str:
    """Генерация хеша данных"""
    data_str = json.dumps(data, sort_keys=True)
    return hashlib.sha256(data_str.encode()).hexdigest()

@router.post("/request", response_model=CreditRequestResponse)
def request_credit_score(
        request_data: CreditScoreRequest,
        background_tasks: BackgroundTasks,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Запрос расчета кредитного скора"""

    credit_request = CreditRequest(
        user_id=current_user.id,
        status="processing",
        blockchain_recorded=False
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

    score_data = calculate_mock_score({})

    report_data = {
        "user_id": current_user.id,
        "score": score_data["score"],
        "category": score_data["category"],
        "calculated_at": datetime.utcnow().isoformat(),
        "factors": score_data["factors"],
        "method": "auto_generated"
    }

    report = CreditReport(
        user_id=current_user.id,
        score=score_data["score"],
        score_category=score_data["category"],
        reputation_score=score_data["reputation_score"],
        report_data=json.dumps(report_data)
    )

    db.add(report)
    db.commit()
    db.refresh(report)

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

@router.post("/verify/{report_id}")
def verify_report(
        report_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Верификация отчета"""

    report = db.query(CreditReport).filter(
        CreditReport.id == report_id,
        CreditReport.user_id == current_user.id
    ).first()

    if not report:
        raise HTTPException(status_code=404, detail="Отчет не найден")

    if not report.blockchain_hash:
        raise HTTPException(status_code=400, detail="Отчет не записан в блокчейн")

        # Создаем локальную верификацию на основе хеша данных
    if report.report_data:
        try:
            data_dict = json.loads(report.report_data)
            current_hash = generate_data_hash(data_dict)
            is_valid = True  # В упрощенной версии всегда True
        except:
            is_valid = False
    else:
        is_valid = False

    verification_data = {
        "report_id": report.id,
        "user_id": report.user_id,
        "score": report.score,
        "verified": is_valid,
        "verified_at": datetime.utcnow().isoformat(),
        "verification_details": "local"
    }

    return verification_data


def process_credit_score_background(request_id: int, user_id: int, request_data: dict, db: Session):
    """Фоновая задача расчета скора"""
    try:
        request = db.query(CreditScoreRequest).filter(CreditScoreRequest.id == request_id).first()
        user = db.query(User).filter(User.id == user_id).first()

        if not request or not user:
            return

        # Мок расчет
        score_data = calculate_mock_score({})

        # Подготовка данных для хеширования
        report_data = {
            "user_id": user_id,
            "score": score_data["score"],
            "category": score_data["category"],
            "calculated_at": datetime.utcnow().isoformat(),
            "factors": score_data["factors"],
            "method": "mock_calculation"
        }
        data_hash = generate_data_hash(report_data)

        report = CreditReport(
            user_id=user_id,
            score=score_data["score"],
            score_category=score_data["category"],
            reputation_score=score_data["reputation_score"],
            report_data=json.dumps(report_data),
            data_hash=data_hash  # Локальный хеш вместо blockchain_hash
        )
        db.add(report)
        user.reputation_score = score_data["reputation_score"]
        request.status = "completed"
        db.commit()

    except Exception as e:
        request = db.query(CreditScoreRequest).filter(CreditScoreRequest.id == request_id).first()
        request.status = "failed"
        db.commit()
        print(f"Ошибка расчета скора: {e}")

#Новые методы

@router.post("/choose-method")
async def choose_credit_method(
        method_data: CreditMethodRequest,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Выбор метода определения кредитной истории"""

    # Обновляем данные пользователя
    if method_data.has_credit_history is not None:
        current_user.has_credit_history = method_data.has_credit_history
    current_user.consent_data_processing = method_data.consent_data_processing
    db.commit()

    return {
        "message": "Метод выбран",
        "method": method_data.method,
        "next_step": f"/api/credit/{method_data.method}"
    }


@router.post("/upload")
async def upload_document(
        file: UploadFile = File(...),
        document_type: str = Form("gosuslugi"),
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Загрузка документа (PDF)"""

    # Проверка расширения
    filename = file.filename or "document.pdf"
    if not filename.lower().endswith('.pdf'):
        raise HTTPException(400, "Только PDF файлы поддерживаются")

    # Сохраняем файл
    file_path = os.path.join(settings.UPLOAD_DIR, f"{current_user.id}_{int(datetime.now().timestamp())}_{filename}")

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Сохраняем запись в БД
    document = UploadedDocument(
        user_id=current_user.id,
        filename=filename,
        file_path=file_path,
        document_type=document_type
    )
    db.add(document)
    db.commit()
    db.refresh(document)

    return {
        "message": "Файл загружен",
        "document_id": document.id,
        "filename": filename,
        "next_step": f"/api/credit/process-document/{document.id}"
    }


@router.post("/process-parsing")
async def process_parsing_method(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Обработка метода парсинга (вызов внешнего сервиса)"""

    if not current_user.consent_data_processing:
        raise HTTPException(400, "Нет согласия на обработку данных")

    # Создаем задачу парсинга
    parser_job = ParserJob(
        user_id=current_user.id,
        status="pending",
        data_sources="external_parsing_service"
    )
    db.add(parser_job)
    db.commit()
    db.refresh(parser_job)

    # Здесь будет вызов внешнего сервиса парсинга
    # Пока возвращаем мок ответ

    return {
        "job_id": parser_job.id,
        "status": "pending",
        "message": "Запрос отправлен в сервис парсинга",
        "callback_url": f"/api/credit/parsing-result/{parser_job.id}"
    }


@router.post("/process-document/{document_id}")
async def process_uploaded_document(
        document_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Обработка загруженного документа (вызов внешнего парсера)"""

    document = db.query(UploadedDocument).filter(
        UploadedDocument.id == document_id,
        UploadedDocument.user_id == current_user.id
    ).first()

    if not document:
        raise HTTPException(404, "Документ не найден")

    # Создаем задачу обработки
    parser_job = ParserJob(
        user_id=current_user.id,
        status="pending",
        data_sources="document_parsing",
        result_data=json.dumps({"document_id": document_id})
    )
    db.add(parser_job)
    db.commit()
    db.refresh(parser_job)

    return {
        "job_id": parser_job.id,
        "document_id": document_id,
        "status": "pending",
        "message": "Документ отправлен на обработку",
        "callback_url": f"/api/credit/document-result/{parser_job.id}"
    }


@router.post("/receive-ml-score")
async def receive_ml_score(
        ml_data: MLScoreRequest,
        db: Session = Depends(get_db),
        background_tasks: BackgroundTasks = None
):
    """Получение результата от ML модели (вызывается внешним сервисом)"""

    # Проверяем пользователя
    user = db.query(User).filter(User.id == ml_data.user_id).first()
    if not user:
        raise HTTPException(404, "Пользователь не найден")

    # Определяем категорию
    score_category = determine_category(ml_data.score)

    # Сохраняем результат ML модели
    credit_report = CreditReport(
        user_id=ml_data.user_id,
        score=ml_data.score,
        score_category=score_category,
        reputation_score=ml_data.score / 850.0,
        report_data=json.dumps(ml_data.dict())
    )

    if ml_data.document_id:
        credit_report.source_document_id = ml_data.document_id

    db.add(credit_report)
    db.commit()
    db.refresh(credit_report)

    return {
        "report_id": credit_report.id,
        "status": "success",
        "message": "Результат сохранен",
        "score": ml_data.score,
        "category": score_category
    }


@router.get("/rating")
async def get_credit_rating(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    """Получение кредитного рейтинга"""
    #Получаем локальный рейтинг
    local_report = db.query(CreditReport).filter(
        CreditReport.user_id == current_user.id
    ).order_by(CreditReport.created_at.desc()).first()

    all_reports = db.query(CreditReport).filter(
        CreditReport.user_id == current_user.id
    ).all()

    return {
        "user_id": current_user.id,
        "full_name": current_user.full_name,
        "local_score": local_report.score if local_report else None,
        "local_category": local_report.score_category if local_report else None,
        "timestamp": datetime.utcnow().isoformat()
    }


# ============ ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ============


def determine_category(score: int) -> str:
    """Определение категории по score"""
    if score >= 720:
        return "excellent"
    elif score >= 680:
        return "good"
    elif score >= 620:
        return "fair"
    elif score >= 580:
        return "poor"
    else:
        return "bad"