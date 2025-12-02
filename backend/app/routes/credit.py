from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from ..database.database import get_db
from ..models.user import User
from ..models.credit import CreditReport, ParserJob
from ..schemas.credit import CreditScoreRequest, CreditScoreResponse, ParserJobResponse
from ..auth.security import get_current_user
import uuid
from datetime import datetime

router = APIRouter()


# Заглушка для ML модели
def calculate_credit_score(user_data: dict) -> dict:
    # Здесь будет интеграция с ML моделью
    # Пока возвращаем mock данные
    return {
        "score": 720,
        "score_category": "good",
        "factors": {
            "payment_history": "positive",
            "credit_utilization": "good",
            "credit_history_length": "average",
            "recent_inquiries": "low"
        }
    }


# Заглушка для парсера
def run_data_parser(job_id: int, user_id: int, data_sources: dict, db: Session):
    try:
        # Имитация работы парсера
        import time
        time.sleep(5)  # Имитация долгой работы

        # Обновляем статус job
        job = db.query(ParserJob).filter(ParserJob.id == job_id).first()
        job.status = "completed"
        job.completed_at = datetime.utcnow()

        # Mock данные от парсера
        parsed_data = {
            "bank_accounts": ["Tinkoff", "Sberbank"],
            "credit_cards": 2,
            "loan_history": "positive",
            "income_sources": 1
        }
        job.result_data = parsed_data

        # Рассчитываем кредитный score
        score_data = calculate_credit_score(parsed_data)

        # Сохраняем кредитный отчет
        report = CreditReport(
            user_id=user_id,
            score=score_data["score"],
            score_category=score_data["score_category"],
            report_data=parsed_data,
            factors=score_data["factors"]
        )
        db.add(report)
        db.commit()

    except Exception as e:
        job = db.query(ParserJob).filter(ParserJob.id == job_id).first()
        job.status = "failed"
        job.error_message = str(e)
        db.commit()


@router.post("/request-score")
def request_credit_score(
        request_data: CreditScoreRequest,
        background_tasks: BackgroundTasks,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # Создаем задачу парсинга
    job = ParserJob(
        user_id=current_user.id,
        status="pending",
        data_sources=request_data.data_sources
    )
    db.add(job)
    db.commit()
    db.refresh(job)

    # Запускаем парсер в фоне
    background_tasks.add_task(
        run_data_parser,
        job.id,
        current_user.id,
        request_data.data_sources,
        db
    )

    return {"job_id": job.id, "status": "processing"}


@router.get("/score", response_model=CreditScoreResponse)
def get_credit_score(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    report = db.query(CreditReport).filter(
        CreditReport.user_id == current_user.id
    ).order_by(CreditReport.created_at.desc()).first()

    if not report:
        raise HTTPException(status_code=404, detail="Credit report not found")

    return report


@router.get("/job-status/{job_id}", response_model=ParserJobResponse)
def get_job_status(
        job_id: int,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    job = db.query(ParserJob).filter(
        ParserJob.id == job_id,
        ParserJob.user_id == current_user.id
    ).first()

    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    return job