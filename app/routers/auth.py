from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.auth import hash_password, verify_password, create_access_token
from app.schemas import UserCreate, UserResponse, UserRole

router = APIRouter(
    prefix="/auth",
    tags=["auth"]
)


# 회원가입
@router.post("/register", response_model=UserResponse)
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    # 이메일 중복 확인
    existing_user = db.query(models.User).filter(
        models.User.email == user.email
    ).first()

    if existing_user:
        raise HTTPException(status_code=400, detail="이미 사용 중인 이메일입니다")

    # 비밀번호 해시화
    user_data = user.model_dump()
    user_data["password"] = hash_password(user_data["password"])

    # role 고정
    user_data["role"] = UserRole.STUDENT

    new_user = models.User(**user_data)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


# 로그인
@router.post("/login")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    # 이메일로 유저 조회
    user = db.query(models.User).filter(
        models.User.email == form_data.username
    ).first()

    # 유저 없거나 비밀번호 틀리면
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="이메일 또는 비밀번호가 올바르지 않습니다"
        )

    # JWT 토큰 발급
    access_token = create_access_token(data={"sub": str(user.id)})

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }