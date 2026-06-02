# Bootcamp Attendance API
> 비대면 부트캠프 출결 관리를 위한 REST API 서버 + AI 자동화

---

## 프로젝트 소개

비대면 부트캠프에서 학습 튜터로 일하면서 직접 경험한 문제에서 출발했습니다.

약 80명의 수강생 출결을 관리하는 데 매일 Discord, HRD 시스템, 구글 스프레드시트 등 여러 곳을 오가며 같은 데이터를 반복적으로 옮기는 비효율적인 작업이 이어졌습니다. 지각·외출·조퇴 신고는 Discord에서 받고, QR 입실 데이터는 HRD에서 가져오고, 시간별 출석은 별도의 구글시트에 기록, 공가 처리는 구글폼으로 받아 또 다른 시트와 드라이브에 옮기는 식이었습니다.

이 경험에서 **"흩어져 있는 창구들을 하나의 시스템으로 합치고, AI로 수작업까지 없애자"** 는 아이디어가 시작되었습니다.

> 본 프로젝트는 백엔드 REST API 서버로, 프론트엔드 없이 API만 개발되었습니다.
> API 문서는 FastAPI 자동 생성 Swagger UI(`/docs`)에서 확인할 수 있습니다.

---

## 해결한 문제

> **"흩어진 툴, 반복되는 수작업 — 출결 관리의 비효율"**

비대면 부트캠프의 튜터와 운영진은 연결되지 않은 여러 툴을 오가며 매일 같은 데이터를 손으로 옮기고 있습니다. 출결 현황 파악, 미입실자 독려, 공가 처리, 운영 채널 보고까지 모두 자동화될 수 있는 반복 업무임에도 사람이 하나하나 처리하고 있는 구조적 문제입니다.

---

## 주요 기능

### 1. 출결 신고 및 관리 API
- 출결 신고 생성/조회/상태 변경 API 제공
- Enum 기반 상태 관리 (`신청 → 확인 → 서류제출 → 승인/반려`)
- 강의별, 학생별, 날짜별 필터링 지원
- 공가 여부(`official`) 및 사유(`reason`) 관리

### 2. Zoom 캡처 AI 출석 인식 API
- Zoom 화면 캡처 이미지를 업로드하면 GPT Vision이 참가자 이름 자동 인식
- LangChain `with_structured_output`으로 안정적인 이름 추출
- 수강생 DB와 자동 매칭 후 교시별 출석 기록
- 기존 **3단계** (캡처 → 드라이브 업로드 → 수동 체크)를 **1단계**로 축소
- AI 인식(`/recognize`)과 DB 저장(`/save`) API 분리로 튜터 검토 후 저장 가능

### 3. 공가 서류 AI 자동 검토 API
- 공가 서류 이미지 업로드 API 제공
- AI가 공가 사유별 가이드라인에 맞는 서류인지 자동 분석
  - 질병/입원: 진료확인서 + 질병코드 확인
  - 예비군/민방위: 소집필증 확인
  - 입사시험/면접: 면접확인서 + 구인공고 확인 등
- 승인 가능 여부, 반려 사유, 보완 필요 항목 자동 반환
- 튜터는 AI 분석 결과를 검토 후 최종 승인/반려

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

---

## ERD

```
course
  └── student
        ├── leave_request
        ├── qr_check_record
        └── class_attendance
```

---

## 📡 API 목록

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

## ⚙️ 실행 방법

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

## 🔮 향후 계획

- [ ] JWT 기반 로그인 및 역할별 권한 (수강생/튜터/운영진)
- [ ] 구글 스프레드시트 연동 (HRD QR 데이터 자동 동기화 대체)
- [ ] 프론트엔드 대시보드 (React)
- [ ] Docker 컨테이너화 및 배포