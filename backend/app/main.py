from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import logging
from sqlalchemy import text
import os
import sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from backend.app.database import engine, Base
from backend.app.routes.auth import router as auth_router
from backend.app.routes.credit import router as credit_router

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
logger.info("Инициализация базы данных...")
try:
    # Создаем все таблицы
    Base.metadata.create_all(bind=engine, checkfirst=True)
    logger.info("✅ Таблицы успешно созданы")
except Exception as e:
    logger.error(f"❌ Ошибка при создании таблиц: {e}")
    raise

app = FastAPI(
    title="TrustFlow",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8000",
        "http://127.0.0.1:8000",
        "http://localhost:5500",
        "http://127.0.0.1:5500",
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router, prefix="/api/auth", tags=["Аутентификация"])
app.include_router(credit_router, prefix="/api/credit", tags=["Кредитный скоринг"])

current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(os.path.dirname(current_dir))
frontend_path = os.path.join(project_root, "frontend")

print(f"🔍 Ищем фронтенд по пути: {frontend_path}")

if os.path.exists(frontend_path):
    print("✅ Фронтенд найден, монтируем статические файлы")
    
    # Монтируем статические файлы (CSS, JS, изображения)
    app.mount("/styles", StaticFiles(directory=os.path.join(frontend_path, "styles")), name="styles")
    app.mount("/scripts", StaticFiles(directory=os.path.join(frontend_path, "scripts")), name="scripts")
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_path, "assets")), name="assets")
    
    # Монтируем HTML файлы
    @app.get("/")
    async def serve_index():
        from fastapi.responses import FileResponse
        return FileResponse(os.path.join(frontend_path, "index.html"))
    
    @app.get("/{page_name}")
    async def serve_page(page_name: str):
        from fastapi.responses import FileResponse
        
        # Проверяем существование файла
        page_path = os.path.join(frontend_path, page_name)
        if os.path.exists(page_path):
            return FileResponse(page_path)
        
        # Если файл не найден, пробуем добавить .html
        html_path = os.path.join(frontend_path, f"{page_name}.html")
        if os.path.exists(html_path):
            return FileResponse(html_path)
        
        # Если страница не найдена, возвращаем 404
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Страница не найдена")
    
else:
    print("⚠️ Фронтенд не найден. Запускаем только API")
    
    @app.get("/")
    async def root():
        return {
            "message": "TrustFlow API запущен",
            "frontend": "не найден",
            "api_docs": "/api/docs",
            "api_endpoints": [
                "/api/auth/login",
                "/api/auth/register",
                "/api/users/me",
                "/api/credit/score"
            ]
        }
    

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, reload=True)