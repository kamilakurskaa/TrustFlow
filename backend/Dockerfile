FROM python:3.11-slim

WORKDIR /app

# Установка системных зависимостей
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Копируем зависимости из КОРНЯ проекта
COPY ../requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем ВСЮ папку Backend в /app
COPY . .

# Создание non-root пользователя
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Запуск приложения
EXPOSE 8000
CMD ["python", "run.py"]