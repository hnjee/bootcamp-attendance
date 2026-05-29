from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import CourseCreate, CourseResponse
from typing import Optional

router = APIRouter(
    prefix="/course",
    tags=["course"]
)

@router.post("", response_model=CourseResponse)
def create_course(
    course: CourseCreate,
    db: Session = Depends(get_db)
):
    new_course = models.Course(**course.model_dump())
    db.add(new_course)
    db.commit()
    db.refresh(new_course)
    return new_course


@router.get("/{course_id}", response_model=CourseResponse)
def get_course(
    course_id: str,
    db: Session = Depends(get_db)
):
    course = db.query(models.Course).filter(
        models.Course.id == course_id
    ).first()

    if not course:
        raise HTTPException(status_code=404, detail="강의를 찾을 수 없습니다")

    return course

@router.get("", response_model=list[CourseResponse])
def get_courses(
    name: Optional[str] = None,  # 강의 이름 검색 추가
    teacher: Optional[str] = None,  # 강사 이름 검색 추가
    db: Session = Depends(get_db)
):
    query = db.query(models.Course)

    if name:
        query = query.filter(models.Course.name.contains(name))
    if teacher: 
        query = query.filter(models.Course.teacher.contains(teacher)) # AND 

    return query.all()