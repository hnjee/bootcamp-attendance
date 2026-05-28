from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import LeaveRequestCreate, LeaveRequestResponse

router = APIRouter(
    prefix="/attendance",
    tags=["attendance"]
)

@router.post("/leave", response_model=LeaveRequestResponse)
def create_leave_request(
    request: LeaveRequestCreate,
    db: Session = Depends(get_db)
):
    # 수강생 존재 여부 확인
    student = db.query(models.Student).filter(
        models.Student.id == request.student_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="수강생을 찾을 수 없습니다")

    # DB에 저장
    leave_request = models.LeaveRequest(**request.model_dump())
    db.add(leave_request)
    db.commit()
    db.refresh(leave_request)

    return leave_request