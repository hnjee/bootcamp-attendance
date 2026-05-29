from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import ClassAttendanceCreate, ClassAttendanceResponse

router = APIRouter(
    prefix="/class-attendance",
    tags=["class-attendance"]
)

@router.post("", response_model=ClassAttendanceResponse)
def create_class_attendance(
    attendance: ClassAttendanceCreate,
    db: Session = Depends(get_db)
):
    # 수강생 존재 여부 확인
    student = db.query(models.Student).filter(
        models.Student.id == attendance.student_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="수강생을 찾을 수 없습니다")

    new_attendance = models.ClassAttendance(**attendance.model_dump())
    db.add(new_attendance)
    db.commit()
    db.refresh(new_attendance)
    return new_attendance


@router.get("/{student_id}", response_model=list[ClassAttendanceResponse])
def get_class_attendance(
    student_id: str,
    db: Session = Depends(get_db)
):
    attendance = db.query(models.ClassAttendance).filter(
        models.ClassAttendance.student_id == student_id
    ).all()

    return attendance