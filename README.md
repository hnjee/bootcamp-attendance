# Bootcamp Attendance API
> 비대면 부트캠프 출결 관리를 위한 REST API 서버 + AI 자동화

## 🚨 Problem: 흩어진 툴, 반복되는 수작업

이 프로젝트는 비대면 부트캠프에서 학습 튜터로 일하면서 직접 경험한 문제에서 출발했습니다.

약 80명의 수강생 출결을 관리하는 데 Discord, HRD 시스템, 구글 스프레드시트 등
연결되지 않은 여러 툴을 오가며 매일 같은 데이터를 손으로 옮기는 작업이 반복됐습니다.

| 업무 | 기존 방식 |
|------|----------|
| 지각·외출·조퇴 신고 | Discord 채널에서 수동 확인 |
| QR 입실 데이터 | HRD → 구글시트 복붙 |
| 교시별 출석 체크 | Zoom 캡처 → 드라이브 → 시트 수동 기록 |
| 공가 처리 | 구글폼 → 전용 시트 + 드라이브 수동 이동 |


## ✅ Solution: 흩어진 툴을 하나의 서비스로 통합하고, AI로 수작업 제거

### 1. 통합 REST API 서버 구축
   - 출결 신고, 공가 처리, HRD QR 입퇴실 기록 확인, 교시별 출결 관리 모두 하나의 시스템에서 관리
   - Discord, HRD, 여러개의 구글 스프레드시트를 대체하는 통합 시스템 제공 
     
### 2. AI로 반복 업무 자동화
   - Zoom 캡처 AI 인식으로 교시별 출석 체크 자동화
   - 공가 서류 AI 자동 검토 

## 📋 주요 기능

### 1. 출결 신고 및 관리 API
- 출결 신고 생성/조회/상태 변경 API 제공
- Enum 기반 상태 관리 (`신청 → 확인 → 서류제출 → 승인/반려`)
- 강의별, 학생별, 날짜별 필터링 지원
- 공가 여부(`official`) 및 사유(`reason`) 관리

### 2. 공가 서류 AI 자동 검토 API
- 공가 서류 이미지 업로드 API 제공
- AI가 공가 사유별 가이드라인에 맞는 서류인지 자동 분석
- 가이드라인 예시 
  - 질병/입원: 진료확인서 또는 통원확인서 또는 입퇴원확인서 / 서류에 질병코드 필수
  - 자격증시험: 시험응시확인서 또는 수험표(감독관 도장 필수) / 접수확인서 불가 
- 승인/반려 여부, 판단 이유 자동 반환
- 튜터는 AI 분석 결과를 검토 후 최종 승인/반려
- 예시
<img width="400" alt="Gemini_Generated_Image_mm2u5xmm2u5xmm2u" src="https://github.com/user-attachments/assets/a6eee806-30c2-45bb-983b-3a886ad3981e" />
<img width="857" height="78" alt="스크린샷 2026-06-02 오후 5 14 44" src="https://github.com/user-attachments/assets/951948a8-112f-4779-9f1f-3a1ddf28986b" />

### 3. 교시 별 출석을 위한 Zoom 캡처 AI 출석 인식 API
- 교시 별 Zoom 학생 화면 캡처 이미지를 업로드하면 GPT Vision이 참가자 이름 자동 인식
- LangChain `with_structured_output`으로 안정적인 이름 추출
- 수강생 DB와 자동 매칭 후 교시별 출석 기록
- 기존 **3단계** (캡처 → 드라이브 업로드 → 수동 체크)를 **1단계**로 축소
- AI 인식(`/recognize`)과 DB 저장(`/save`) API 분리로 튜터 검토 후 저장 가능
- 예시
<img width="1559" height="576" alt="Gemini_Generated_Image_7mesuh7mesuh7mes" src="https://github.com/user-attachments/assets/f22e34b7-b4f7-4073-b47d-0e9f605de1e6" />
<img width="857" height="59" alt="스크린샷 2026-06-02 오후 5 07 14" src="https://github.com/user-attachments/assets/ca1ed9cd-38c8-45c3-ba57-8aff60df292d" />

### 4. QR 입퇴실 기록 관리 API
- HRD QR 입퇴실 데이터 기록 및 조회 API 제공
- 입실 시간, 퇴실 시간, 최종 출결 상태 관리

---

## 기술 스택

| 분류 | 기술 |
|------|------|
| Backend | FastAPI, Python 3.11 |
| Database | PostgreSQL, SQLAlchemy ORM |
| AI | LangChain, GPT-4o Vision, Structured Output |
| Package Manager | uv |
| API 문서 | Swagger UI (FastAPI 자동 생성) |


## ERD
<img width="587" height="637" alt="image" src="https://github.com/user-attachments/assets/071fa91d-53e9-4f59-9e5d-d7e3582634e8" />


## API 목록

### Course (강의)
| 메서드 | URL | 설명 |
|--------|-----|------|
| POST | `/course` | 강의 생성 |
| GET | `/course/{course_id}` | 강의 단건 조회 |
| GET | `/course` | 강의 목록 조회 (name, teacher 필터) |
| PATCH | `/course/{course_id}/status` | 강의 상태 변경 |

### Student (수강생)
| 메서드 | URL | 설명 |
|--------|-----|------|
| POST | `/student` | 수강생 생성 |
| GET | `/student/{student_id}` | 수강생 단건 조회 |
| GET | `/student` | 수강생 목록 조회 (course_id 필수, name 필터) |
| PATCH | `/student/{student_id}/status` | 수강생 상태 변경 |

### Leave Request (출결 신고)
| 메서드 | URL | 설명 |
|--------|-----|------|
| POST | `/leave-request` | 출결 신고 생성 |
| GET | `/leave-request/{id}` | 출결 신고 단건 조회 |
| GET | `/leave-request` | 출결 신고 목록 조회 (course_id 필수, name/date 필터) |
| PATCH | `/leave-request/{id}/status` | 출결 신고 상태 변경 |
| POST | `/leave-request/{id}/document` | 공가 서류 업로드 |
| POST | `/leave-request/{id}/analyze` | 공가 서류 AI 분석 |

### QR Check Record (QR 입퇴실)
| 메서드 | URL | 설명 |
|--------|-----|------|
| POST | `/qr` | QR 입퇴실 기록 생성 |
| GET | `/qr/{student_id}` | 수강생 입퇴실 단건 조회 |
| GET | `/qr` | QR 입퇴실 목록 조회 (course_id 필수, name/date 필터) |

### Class Attendance (교시별 출석 — 수동)
| 메서드 | URL | 설명 |
|--------|-----|------|
| POST | `/class-attendance` | 교시별 출석 수동 기록 |
| GET | `/class-attendance/{student_id}` | 수강생 교시별 출석 조회 |
| GET | `/class-attendance` | 교시별 출석 목록 조회 (course_id 필수, name/date/period 필터) |

### Zoom AI 출석 인식 (교시별 출석 — AI 자동화)
| 메서드 | URL | 설명 |
|--------|-----|------|
| POST | `/zoom/recognize` | Zoom 캡처 AI 이름 인식 |
| POST | `/zoom/save` | 인식 결과 출석 저장 |

---

## 실행 방법

### 1. 사전 준비
```bash
# PostgreSQL 설치 (Mac)
brew install postgresql@16
brew services start postgresql@16

# DB 생성
createdb attendance_db
```

### 2. 환경변수 설정
```bash
# .env 파일 생성
DATABASE_URL=postgresql://localhost/attendance_db
OPENAI_API_KEY=sk-...
```

### 3. 패키지 설치 및 실행
```bash
uv sync
uv run python -m uvicorn app.main:app --reload
```

### 4. API 문서 확인
```
http://localhost:8000/docs
```

---

## 향후 계획
- [ ] 구글 스프레드시트 연동 (HRD QR 데이터 자동 동기화)
- [ ] JWT 기반 로그인 및 역할별 권한 (수강생/튜터/운영진)
- [ ] 프론트엔드 대시보드 (React)
- [ ] Docker 컨테이너화 및 배포
