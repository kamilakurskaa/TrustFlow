import uvicorn
import os

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",  # Важно! Не 127.0.0.1
        port=8000,
        reload=False,  # В продакшене выключаем reload
        log_level="info"
    )
