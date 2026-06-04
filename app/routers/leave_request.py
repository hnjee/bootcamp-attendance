from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import LeaveRequestCreate, LeaveRequestResponse, LeaveRequestStatus, DocumentAnalysisResponse
from datetime import date as date_type
import uuid
from typing import Optional
import os
import base64
import uuid
import aiofiles
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY")
)
document_llm = llm.with_structured_output(DocumentAnalysisResponse)

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
    user = db.query(models.User).filter(
        models.User.id == request.user_id
    ).first()

    if not user:
        raise HTTPException(status_code=404, detail="수강생을 찾을 수 없습니다")

    # DB에 저장
    leave_request = models.LeaveRequest(**request.model_dump())
    db.add(leave_request)
    db.commit()
    db.refresh(leave_request)

    return leave_request

@router.get("/{user_id}", response_model=list[LeaveRequestResponse])
def get_leave_request(
    user_id: str,
    db: Session = Depends(get_db)
):
    request = db.query(models.LeaveRequest).filter(
        models.LeaveRequest.user_id == user_id
    ).all()

    return request

@router.get("", response_model=list[LeaveRequestResponse])
def get_leave_requests(
    course_id: uuid.UUID, # 필수 값 -> 리스트는 반드시 강의별로 
    name: Optional[str] = None,  # 학생명 검색 추가
    date: Optional[date_type] = None, # 날짜 검색 추가
    db: Session = Depends(get_db)
):
    query = db.query(models.LeaveRequest).join(models.User).filter(
        models.User.course_id == course_id
    )

    if name:
        query = query.filter(models.User.name.contains(name))

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


# 공가 서류 업로드
@router.post("/{leave_request_id}/document")
async def upload_document(
    leave_request_id: str,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # leave_request 존재 여부 확인
    leave_request = db.query(models.LeaveRequest).filter(
        models.LeaveRequest.id == leave_request_id
    ).first()

    if not leave_request:
        raise HTTPException(status_code=404, detail="신청을 찾을 수 없습니다")

    # 파일 저장
    file_extension = file.filename.split(".")[-1]
    file_name = f"{uuid.uuid4()}.{file_extension}"
    file_path = f"uploads/{file_name}"

    async with aiofiles.open(file_path, "wb") as f:
        content = await file.read()
        await f.write(content)

    # document_url 업데이트
    leave_request.document_url = file_path
    leave_request.status = LeaveRequestStatus.DOCS_SUBMITTED
    db.commit()
    db.refresh(leave_request)

    return {"message": "서류 업로드 완료", "document_url": file_path}


# AI로 공가 서류 분석 -> 적합 판단
@router.post("/{leave_request_id}/analyze", response_model=DocumentAnalysisResponse)
async def analyze_document(
    leave_request_id: str,
    db: Session = Depends(get_db)
):
    # leave_request 조회
    leave_request = db.query(models.LeaveRequest).filter(
        models.LeaveRequest.id == leave_request_id
    ).first()

    if not leave_request:
        raise HTTPException(status_code=404, detail="신청을 찾을 수 없습니다")

    if not leave_request.document_url:
        raise HTTPException(status_code=400, detail="업로드된 서류가 없습니다")

    # 파일 읽어서 base64 변환
    async with aiofiles.open(leave_request.document_url, "rb") as f:
        content = await f.read()
    base64_image = base64.b64encode(content).decode("utf-8")

    response = document_llm.invoke([
        SystemMessage(content="""당신은 부트캠프 공가 서류를 검토하는 전문가입니다.
                아래 가이드라인에 따라 해당 건의 공가 사유에 맞는 서류가 제출되어 있는지 검토해주세요. 
                - 질병/입원: 진료확인서 또는 통원확인서 또는 입퇴원확인서 / 서류에 질병코드 필수
                - 자격증시험: 시험응시확인서 또는 수험표(감독관 도장 필수) / 접수확인서 불가
                - 입사시험/면접: 면접확인서 + 구인공고 또는 면접결과 통보 캡쳐
                - 예비군/민방위훈련: 소집필증 또는 훈련필증
                - 결혼: 청첩장 + 가족관계증명서
                - 사망: 사망진단서 + 가족관계증명서
                - 출산: 출생증명서 + 가족관계증명서"""),
        HumanMessage(content=[
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            },
            {
                "type": "text",
                "text": f"이 서류가 '{leave_request.reason}' 공가 사유의 처리 기준에 맞는지 판단해주세요."
            }
        ])
    ])

    return response  # 바로 DocumentAnalysisResponse 객체