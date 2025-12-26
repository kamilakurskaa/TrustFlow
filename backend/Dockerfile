FROM python:3.11-slim

WORKDIR /app

# Системные зависимости
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Копируем requirements.txt
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Копируем весь backend
COPY . .

# Создаем директории
RUN mkdir -p uploads

# Non-root пользователь
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

EXPOSE 8000

CMD ["python", "run.py"]
