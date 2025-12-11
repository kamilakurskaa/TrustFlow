from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from ..database import get_db, Base
from ..config import settings
from ..models.user import User, UserProfile
from ..schemas.user import UserCreate, UserLogin, Token, UserResponse
from ..auth.security import get_password_hash, verify_password, create_access_token, get_current_user
from ..services.blockchain_service import BlockchainService
router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    # Проверяем, существует ли пользователь
    db_user = db.query(User).filter(User.email == user_data.email).first()
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    if user_data.phone:
        phone_user = db.query(User).filter(User.phone == user_data.phone).first()
        if phone_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Номер телефона уже зарегистрирован"
            )
    # Создаем пользователя
    hashed_password = get_password_hash(user_data.password)
    user = User(
        email=user_data.email,
        password_hash=hashed_password,
        full_name=user_data.full_name,
        phone=user_data.phone,
        wallet_address=user_data.wallet_address,
        has_credit_history=getattr(user_data, 'has_credit_history', None),
        consent_data_processing=getattr(user_data, 'consent_data_processing', False)
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    # Создаем профиль на блокчейне (НОВОЕ ↓)
    if user.wallet_address:
        blockchain_service = BlockchainService()
        tx_hash = blockchain_service.create_user_profile(
            user_id=user.id,
            email=user.email,
            wallet_address=user.wallet_address
        )

        if tx_hash:
            user.blockchain_user_id = tx_hash
            db.commit()

    # Создаем пустой профиль
    profile = UserProfile(user_id=user.id)
    db.add(profile)
    db.commit()

    return user


@router.post("/login", response_model=Token)
def login(user_data: UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password"
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user"
        )

    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": user
    }

@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user