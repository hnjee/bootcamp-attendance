from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
import uuid


# 출결 신고 생성 (수강생이 신고할 때 보내는 데이터)
class LeaveRequestCreate(BaseModel):
    student_id: uuid.UUID
    date: date
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    type: str
    official: bool = False
    reason: Optional[str] = None


# 출결 신고 응답 (API가 돌려주는 데이터)
class LeaveRequestResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    date: date
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    type: str
    official: bool
    reason: Optional[str] = None
    status: str
    document_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# Course
class CourseCreate(BaseModel):
    name: str
    teacher: str
    start_date: date
    end_date: date
    total_periods: int

class CourseResponse(BaseModel):
    id: uuid.UUID
    name: str
    teacher: str
    start_date: date
    end_date: date
    total_periods: int

    class Config:
        from_attributes = True


# Student
class StudentCreate(BaseModel):
    course_id: uuid.UUID
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None

class StudentResponse(BaseModel):
    id: uuid.UUID
    course_id: uuid.UUID
    name: str
    phone: Optional[str] = None
    email: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True