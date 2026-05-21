import uuid
from sqlalchemy import Column, String, Boolean, Integer, Date, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.database import Base

class Course(Base):
    __tablename__ = "course"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String, nullable=False)
    teacher = Column(String, nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    total_periods = Column(Integer, nullable=False)


class Student(Base):
    __tablename__ = "student"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    course_id = Column(UUID(as_uuid=True), ForeignKey("course.id"), nullable=False)
    name = Column(String, nullable=False)
    phone = Column(String)
    email = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class AttendanceReport(Base):
    __tablename__ = "attendance_report"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student.id"), nullable=False)
    type = Column(String, nullable=False)
    date = Column(Date, nullable=False)
    reason = Column(String)
    created_at = Column(DateTime, server_default=func.now())


class CheckinRecord(Base):
    __tablename__ = "checkin_record"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student.id"), nullable=False)
    checkin_time = Column(DateTime)
    checkout_time = Column(DateTime)
    date = Column(Date, nullable=False)
    status = Column(String, nullable=False)


class ClassAttendance(Base):
    __tablename__ = "class_attendance"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student.id"), nullable=False)
    date = Column(Date, nullable=False)
    period = Column(Integer, nullable=False)
    present = Column(Boolean, nullable=False, default=False)


class LeaveRequest(Base):
    __tablename__ = "leave_request"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    student_id = Column(UUID(as_uuid=True), ForeignKey("student.id"), nullable=False)
    date = Column(Date, nullable=False)
    reason = Column(String)
    document_url = Column(String)
    approved = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())