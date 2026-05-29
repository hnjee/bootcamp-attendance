from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import course, student, leave_request, qr, class_attendance

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(course.router)
app.include_router(student.router)
app.include_router(leave_request.router)
app.include_router(qr.router)
app.include_router(class_attendance.router)

@app.get("/")
def root():
    return {"message": "출결 관리 시스템 작동 중!"}