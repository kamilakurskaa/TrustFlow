import requests
import logging
from typing import Optional, Dict

# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RandomizerClient:
    def __init__(self, base_url: str = "http://localhost:8002"):
        self.base_url = base_url.rstrip("/")  # убираем слеш в конце

    def get_financial_data(self, user_id: str, has_history: bool) -> Optional[Dict]:
        """Получить 12 параметров от рандомайзера"""
        try:
            response = requests.post(
                f"{self.base_url}/api/generate",
                json={
                    "user_id": user_id,
                    "has_credit_history": has_history
                },
                timeout=5
            )
            response.raise_for_status()
            data = response.json()
            logger.info(f"Успешно получены данные для user_id={user_id}")
            return data["features"]

        except Exception as e:
            logger.error(f"Ошибка рандомайзера для user_id={user_id}: {e}")
            return None


# Создаём один экземпляр на всё приложение
randomizer_client = RandomizerClient()

# Тест только при прямом запуске
if __name__ == "__main__":
    # Для локальной проверки
    result = randomizer_client.get_financial_data('test_user', True)
    if result:
        print(f"✅ Клиент работает! Получено {len(result)} параметров:{result}")
    else:
        print("❌ Клиент не смог получить данные")