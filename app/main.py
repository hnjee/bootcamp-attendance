from fastapi import FastAPI
from app.database import engine
from app import models
from app.routers import attendance, course, student, qr

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.include_router(course.router)
app.include_router(student.router)
app.include_router(attendance.router)
app.include_router(qr.router)

@app.get("/")
def root():
    return {"message": "출결 관리 시스템 작동 중!"}