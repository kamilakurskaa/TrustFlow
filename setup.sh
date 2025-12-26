#!/bin/bash

echo "🚀 Настройка TrustFlow..."

# Проверка Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker не установлен!"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose не установлен!"
    exit 1
fi

# Создаем необходимые директории
mkdir -p backend/uploads
mkdir -p backend/app/contracts

# Создаем пустой contract файл если его нет
if [ ! -f backend/app/contracts/CreditProfile.json ]; then
    echo '{"abi": [], "contractName": "CreditProfile"}' > backend/app/contracts/CreditProfile.json
fi

# Останавливаем старые контейнеры
echo "🛑 Остановка старых контейнеров..."
docker-compose down

# Останавливаем локальные сервисы
echo "🔧 Освобождение портов..."
sudo systemctl stop postgresql 2>/dev/null || true
sudo systemctl stop apache2 2>/dev/null || true
sudo systemctl stop nginx 2>/dev/null || true

# Собираем и запускаем
echo "🔨 Сборка образов..."
docker-compose build --no-cache

echo "▶️  Запуск контейнеров..."
docker-compose up -d

# Ждем запуска БД
echo "⏳ Ожидание запуска базы данных..."
sleep 15

# Проверка статуса
echo ""
echo "📊 Статус сервисов:"
docker-compose ps

echo ""
echo "✅ TrustFlow запущен!"
echo ""
echo "🌐 Доступные адреса:"
echo "   Frontend:  http://localhost"
echo "   Backend:   http://localhost:8000"
echo "   API Docs:  http://localhost:8000/docs"
echo "   Credit Service: http://localhost:8002"
echo ""
echo "📝 Логи можно посмотреть командой:"
echo "   docker-compose logs -f [service_name]"
echo ""
echo "🔧 Для остановки используйте:"
echo "   docker-compose down"
