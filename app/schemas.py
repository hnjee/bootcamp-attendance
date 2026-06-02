from pydantic import BaseModel
from datetime import date, datetime
from typing import Optional
import uuid
from enum import Enum


# Enum 정의
class LeaveRequestStatus(str, Enum):
    PENDING = "신청"
    CONFIRMED = "확인"
    DOCS_SUBMITTED = "서류제출"
    DOCS_APPROVED = "서류승인"
    DOCS_REJECTED = "서류반려"
    CANCELLED = "신청취소"

class LeaveRequestType(str, Enum):
    LATE = "지각"
    OUT = "외출"
    EARLY_LEAVE = "조퇴"
    ABSENT = "결석"

class LeaveRequestReason(str, Enum):
    ILLNESS = "질병/입원"
    MILITARY = "예비군/민방위훈련"
    JOB_INTERVIEW = "입사시험/면접"
    CERTIFICATION = "자격증시험"
    WEDDING = "결혼"
    BEREAVEMENT = "사망"
    CHILDBIRTH = "출산"

class StudentStatus(str, Enum):
    BEFORE = "수강 전"
    ACTIVE = "수강 중"
    COMPLETED = "수료"
    CANCELLED = "수강 취소"

class CourseStatus(str, Enum):
    BEFORE = "시작 전"
    ACTIVE = "진행 중"
    ENDED = "종료"

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
    status: CourseStatus

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
    status: StudentStatus
    created_at: datetime

    class Config:
        from_attributes = True


# 출결 신고
class LeaveRequestCreate(BaseModel):
    student_id: uuid.UUID
    date: date
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    type: LeaveRequestType
    official: bool = False
    reason: Optional[LeaveRequestReason] = None

class LeaveRequestResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    date: date
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    type: LeaveRequestType
    official: bool
    reason: Optional[LeaveRequestReason] = None
    status: LeaveRequestStatus
    document_url: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

# 공가 서류 AI 분석 결과
class DocumentAnalysisResponse(BaseModel):
    is_valid: bool          # 승인 가능 여부
    reason: str             # 판단 이유

# QR 입퇴실
class QrCheckRecordCreate(BaseModel):
    student_id: uuid.UUID
    date: date
    checkin_time: Optional[datetime] = None
    checkout_time: Optional[datetime] = None
    result: str

class QrCheckRecordResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    date: date
    checkin_time: Optional[datetime] = None
    checkout_time: Optional[datetime] = None
    result: str

    class Config:
        from_attributes = True


# 교시별 수업 출석
class ClassAttendanceCreate(BaseModel):
    student_id: uuid.UUID
    date: date
    period: int
    present: bool

class ClassAttendanceResponse(BaseModel):
    id: uuid.UUID
    student_id: uuid.UUID
    date: date
    period: int
    present: bool

    class Config:
        from_attributes = True

# Zoom 출석 인식 결과
class ZoomParticipants(BaseModel):
    names: list[str]

class ZoomRecognizeResponse(BaseModel):
    extracted_names: list[str]  # AI가 인식한 전체 이름
    matched: list[str]          # DB와 매칭된 이름
    unmatched: list[str]        # 매칭 안된 이름

class ZoomSaveRequest(BaseModel):
    course_id: uuid.UUID
    date: date
    period: int
    matched_names: list[str]    # 튜터가 확인한 최종 출석자 이름

