import os
from datetime import datetime, timedelta
from jwt import decode, encode
from jwt.exceptions import PyJWTError
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

try:
    from jwt import encode, decode
    from jwt.exceptions import JWTError, ExpiredSignatureError, InvalidTokenError
    JWT_AVAILABLE = True
except ImportError:
    print("⚠️ PyJWT не установлен")
    JWT_AVAILABLE = False

from ..database.database import get_db
from ..models.user import User
from sqlalchemy.orm import Session



# Конфигурация
SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-here")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
    argon2__time_cost=2,  # Количество итераций
    argon2__memory_cost=65536,  # Память в KiB
    argon2__parallelism=2,  # Потоки
    argon2__hash_len=32,  # Длина хэша
    argon2__salt_len=16  # Длина соли
)
security = HTTPBearer()

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> dict:
    """Декодирует JWT токен"""
    if not JWT_AVAILABLE:
        return {"sub": "1", "exp": datetime.utcnow().timestamp() + 3600}

    try:
        return decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except (JWTError, InvalidTokenError):
        raise HTTPException(status_code=401, detail="Invalid token")


async def get_current_user(
        credentials: HTTPAuthorizationCredentials = Depends(security),
        db: Session = Depends(get_db)
) -> User:
    """Получает текущего пользователя"""
    token = credentials.credentials

    try:
        payload = decode_token(token)
        user_id_str = payload.get("sub")

        if not user_id_str:
            raise HTTPException(status_code=401, detail="Invalid token")

        user_id = int(user_id_str)
        user = db.query(User).filter(User.id == user_id).first()

        if not user:
            raise HTTPException(status_code=401, detail="User not found")

        if not user.is_active:
            raise HTTPException(status_code=400, detail="User inactive")

        return user

    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid user id")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Auth error: {str(e)}")

__all__ = [
    'hash_password',
    'verify_password',
    'create_access_token',
    'get_current_user',
    'security',
    'ACCESS_TOKEN_EXPIRE_MINUTES'
]