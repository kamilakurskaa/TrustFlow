from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import database
from .routes import auth, users, credit
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    database.Base.metadata.create_all(bind=database.engine)
    logger.info("Таблицы базы данных созданы успешно")
except Exception as e:
    logger.error(f"Ошибка при создании таблиц: {e}")

app = FastAPI(
    title="TrustFlow",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Подключаем роуты
app.include_router(auth.router, prefix="/api/auth", tags=["auth"])
app.include_router(users.router, prefix="/api/users", tags=["users"])
app.include_router(credit.router, prefix="/api/credit", tags=["credit"])

@app.get("/")
async def root():
    return {"message": "TrustFlow Credit Platform API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}