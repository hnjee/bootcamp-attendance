from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import UserCreate, UserResponse, StudentStatus
from typing import Optional
import uuid
from app.auth import require_role
from app.schemas import UserRole


router = APIRouter(
    prefix="/user",
    tags=["user"]
)

    
@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: str,
    db: Session = Depends(get_db)
):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    return user

@router.get("", response_model=list[UserResponse])
def get_users(
    course_id: uuid.UUID, # 필수 값 -> 학생 리스트는 반드시 강의별로 
    name: Optional[str] = None,  # 이름 검색 추가
    db: Session = Depends(get_db)
):
    query = db.query(models.User).filter(
        models.User.course_id == course_id
    )

    if name:
        query = query.filter(models.User.name.contains(name)) # WHERE name LIKE '%이름%'

    return query.all()

@router.patch("/{user_id}/status")
def update_user_status(
    user_id: str,
    status: StudentStatus,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.ADMIN))
):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")

    user.status = status
    db.commit()
    db.refresh(user)
    return user


@router.patch("/{user_id}/role")
def update_user_role(
    user_id: str,
    role: UserRole,
    db: Session = Depends(get_db),
    current_user = Depends(require_role(UserRole.ADMIN))
):
    user = db.query(models.User).filter(
        models.User.id == user_id
    ).first()
    
    if not user:
        raise HTTPException(status_code=404, detail="사용자를 찾을 수 없습니다")
    
    user.role = role
    db.commit()
    db.refresh(user)
    return user