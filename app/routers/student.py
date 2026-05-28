from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import StudentCreate, StudentResponse

router = APIRouter(
    prefix="/student",
    tags=["student"]
)

@router.post("", response_model=StudentResponse)
def create_student(
    student: StudentCreate,
    db: Session = Depends(get_db)
):
    # 강의 존재 여부 확인
    course = db.query(models.Course).filter(
        models.Course.id == student.course_id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="강의를 찾을 수 없습니다")

    new_student = models.Student(**student.model_dump())
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student


@router.get("/{student_id}", response_model=StudentResponse)
def get_student(
    student_id: str,
    db: Session = Depends(get_db)
):
    student = db.query(models.Student).filter(
        models.Student.id == student_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="수강생을 찾을 수 없습니다")

    return student