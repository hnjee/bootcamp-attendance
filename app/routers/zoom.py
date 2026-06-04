import os
import base64
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app import models
from app.schemas import ZoomParticipants, ZoomRecognizeResponse, ZoomSaveRequest
from datetime import date
import uuid
from typing import Optional
#from openai import OpenAI
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage

router = APIRouter(
    prefix="/zoom",
    tags=["zoom"]
)

#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

llm = ChatOpenAI(
    model="gpt-4o",
    api_key=os.getenv("OPENAI_API_KEY")
)
zoom_llm = llm.with_structured_output(ZoomParticipants)


# 1. AI 인식만
@router.post("/recognize", response_model=ZoomRecognizeResponse)
async def recognize_zoom_capture(
    course_id: uuid.UUID,
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # 이미지 base64 변환
    image_data = await file.read()
    base64_image = base64.b64encode(image_data).decode("utf-8")

    # GPT Vision 호출 부분 교체
    response = zoom_llm.invoke([
        HumanMessage(content=[
            {
                "type": "image_url",
                "image_url": {
                    "url": f"data:image/png;base64,{base64_image}"
                }
            },
            {
                "type": "text",
                "text": """이 Zoom 화면에 표시된 모든 참가자 이름을 추출해주세요.
                        규칙:
                        1. 이름 앞에 [인프라 11기] 같은 기수 표시가 있는 사용자 이름만 추출
                        2. 단, 기수 표시는 제거하고 순수한 이름만 추출, 예: [인프라 11기] 지영기 -> 지영기)
                        3. 조건에 맞는 참가자 이름을 빠짐 없이 추출
                        """
            }
        ])
    ])

    extracted_names = response.names  # .parsed 없이 바로 접근!

    # DB에서 해당 강의 수강생과 매칭
    users = db.query(models.User).filter(
        models.User.course_id == course_id
    ).all()
    student_names = [s.name for s in users]

    matched = [name for name in extracted_names if name in student_names]
    unmatched = [name for name in extracted_names if name not in student_names]

    return ZoomRecognizeResponse(
        extracted_names=extracted_names,
        matched=matched,
        unmatched=unmatched
    )


# 2. DB 저장
@router.post("/save")
def save_zoom_attendance(
    request: ZoomSaveRequest,
    db: Session = Depends(get_db)
):
    # 해당 강의 전체 수강생 조회
    users = db.query(models.User).filter(
        models.User.course_id == request.course_id
    ).all()


    # matched된 학생 출석처리 
    for user in users:
        attendance = models.ClassAttendance(
            user_id=user.id,
            date=request.date,
            period=request.period,
            present=user.name in request.matched_names
        )
        db.add(attendance)

    db.commit()

    return {
        "message": "출석 저장 완료",
        "total": len(users),
        "present": len(request.matched_names),
        "absent": len(users) - len(request.matched_names)
    }