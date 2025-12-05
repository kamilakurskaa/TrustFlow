import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database.database import Base, engine
from app.models.user import User, UserProfile
from app.models.credit import CreditReport, ParserJob


def init_database():
    """Инициализирует базу данных SQLite"""
    try:
        # Удаляем старый файл базы если существует
        if os.path.exists("trustflow.db"):
            os.remove("trustflow.db")
            print("Удален старый файл базы данных")

        # Создаем все таблицы
        Base.metadata.create_all(bind=engine)
        print("База данных успешно создана")
        print("Cозданные таблицы:")
        print("   - users")
        print("   - user_profiles")
        print("   - credit_reports")
        print("   - parser_jobs")

    except Exception as e:
        print(f"Ошибка при создании базы данных: {e}")
        sys.exit(1)


if __name__ == "__main__":
    print("Инициализация базы данных SQLite...")
    init_database()