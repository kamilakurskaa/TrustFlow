from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import logging
from sqlalchemy import text

from .database import engine
from .routes.auth import router as auth_router
from .routes.credit import router as credit_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="TrustFlow",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["Аутентификация"])
app.include_router(credit_router, prefix="/api/credit", tags=["Кредитный скоринг"])

@app.get("/")
async def root():
    return {"message": "TrustFlow Credit Platform API"}

@app.get("/health")
async def health_check():
    try:
        with engine.connect() as conn:
            # Проверяем существование таблицы users
            result = conn.execute(
                text("SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'users');")
            ).scalar()

            if result:
                # Пробуем получить количество пользователей
                count = conn.execute(text("SELECT COUNT(*) FROM users;")).scalar()
                return {
                    "status": "healthy",
                    "database": "connected",
                    "users_table": "exists",
                    "users_count": count
                }
            else:
                return {
                    "status": "unhealthy",
                    "database": "connected",
                    "users_table": "missing",
                    "message": "Таблица users не найдена. Создайте таблицы через SQL скрипт."
                }

    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Ошибка подключения к базе данных"
        }


@app.get("/tables")
async def get_tables():
    """Получение списка всех таблиц"""
    try:
        with engine.connect() as conn:
            result = conn.execute(
                text("""
                    SELECT table_name 
                    FROM information_schema.tables 
                    WHERE table_schema = 'public'
                    ORDER BY table_name;
                """)
            ).fetchall()

            tables = [row[0] for row in result]
            return {"tables": tables, "count": len(tables)}

    except Exception as e:
        return {"error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)