from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import ClassAttendanceCreate, ClassAttendanceResponse
from datetime import date as date_type
import uuid
from typing import Optional

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

@router.get("", response_model=list[ClassAttendanceResponse])
def get_class_attendances(
    course_id: uuid.UUID, # 필수 값 -> 리스트는 반드시 강의별로 
    name: Optional[str] = None,  # 학생명 검색 추가
    date: Optional[date_type] = None, # 날짜 검색 추가
    db: Session = Depends(get_db)
):
    query = db.query(models.ClassAttendance).join(models.Student).filter(
        models.Student.course_id == course_id
    )

    if name:
        query = query.filter(models.Student.name.contains(name))

    if date:
        query = query.filter(models.ClassAttendance.date == date)

    return query.all()