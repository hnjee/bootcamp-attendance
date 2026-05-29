from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import QrCheckRecordCreate, QrCheckRecordResponse

router = APIRouter(
    prefix="/qr",
    tags=["qr"]
)

@router.post("", response_model=QrCheckRecordResponse)
def create_qr_record(
    record: QrCheckRecordCreate,
    db: Session = Depends(get_db)
):
    # 수강생 존재 여부 확인
    student = db.query(models.Student).filter(
        models.Student.id == record.student_id
    ).first()

    if not student:
        raise HTTPException(status_code=404, detail="수강생을 찾을 수 없습니다")

    new_record = models.QrCheckRecord(**record.model_dump())
    db.add(new_record)
    db.commit()
    db.refresh(new_record)
    return new_record


@router.get("/{student_id}", response_model=list[QrCheckRecordResponse])
def get_qr_records(
    student_id: str,
    db: Session = Depends(get_db)
):
    records = db.query(models.QrCheckRecord).filter(
        models.QrCheckRecord.student_id == student_id
    ).all()

    return records