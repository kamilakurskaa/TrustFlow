from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from backend.app.database import get_db
from ..models.user import User, UserProfile
from ..schemas.user import UserResponse, ProfileBase, ProfileResponse
from ..auth.security import get_current_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_info(current_user: User = Depends(get_current_user)):
    return current_user


@router.get("/profile", response_model=ProfileResponse)
def get_user_profile(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")
    return profile


@router.put("/profile", response_model=ProfileResponse)
def update_user_profile(
        profile_data: ProfileBase,
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    profile = db.query(UserProfile).filter(UserProfile.user_id == current_user.id).first()
    if not profile:
        profile = UserProfile(user_id=current_user.id, **profile_data.dict())
        db.add(profile)
    else:
        for field, value in profile_data.dict(exclude_unset=True).items():
            setattr(profile, field, value)

    db.commit()
    db.refresh(profile)
    return profile