from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import LeaveRequestCreate, LeaveRequestResponse, LeaveRequestStatus
from datetime import date as date_type
import uuid
from typing import Optional

router = APIRouter(
    prefix="/leave-request",
    tags=["leave-request"]
)

@router.post("", response_model=LeaveRequestResponse)
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

@router.get("/{student_id}", response_model=list[LeaveRequestResponse])
def get_leave_request(
    student_id: str,
    db: Session = Depends(get_db)
):
    request = db.query(models.LeaveRequest).filter(
        models.LeaveRequest.student_id == student_id
    ).all()

    return request

@router.get("", response_model=list[LeaveRequestResponse])
def get_leave_requests(
    course_id: uuid.UUID, # 필수 값 -> 리스트는 반드시 강의별로 
    name: Optional[str] = None,  # 학생명 검색 추가
    date: Optional[date_type] = None, # 날짜 검색 추가
    db: Session = Depends(get_db)
):
    query = db.query(models.LeaveRequest).join(models.Student).filter(
        models.Student.course_id == course_id
    )

    if name:
        query = query.filter(models.Student.name.contains(name))

    if date:
        query = query.filter(models.LeaveRequest.date == date)

    return query.all()

@router.patch("/{leave_request_id}/status")
def update_leave_request_status(
    leave_request_id: str,
    status: LeaveRequestStatus,  # Enum으로 제한!
    db: Session = Depends(get_db)
):
    leave_request = db.query(models.LeaveRequest).filter(
        models.LeaveRequest.id == leave_request_id
    ).first()

    if not leave_request:
        raise HTTPException(status_code=404, detail="신청을 찾을 수 없습니다")

    leave_request.status = status
    db.commit()
    db.refresh(leave_request)
    return leave_request