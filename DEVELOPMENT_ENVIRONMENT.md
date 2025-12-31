# BH2025 WOWU 개발 환경 요약

> **마지막 업데이트**: 2024-12-31  
> **버전**: 3.5  
> **브랜치**: `hun` (개발), `main` (프로덕션)

---

## 📋 목차
1. [프로젝트 개요](#프로젝트-개요)
2. [기술 스택](#기술-스택)
3. [프로젝트 구조](#프로젝트-구조)
4. [환경 구성](#환경-구성)
5. [개발 워크플로우](#개발-워크플로우)
6. [배포 환경](#배포-환경)
7. [주요 기능](#주요-기능)
8. [데이터베이스](#데이터베이스)
9. [파일 저장소](#파일-저장소)
10. [문서 관리](#문서-관리)

---

## 프로젝트 개요

### 기본 정보
- **프로젝트명**: BH2025 바이오헬스 교육관리 플랫폼
- **목적**: 보건복지부 K-디지털 트레이닝 교육 과정 통합 관리
- **주관**: 우송대학교산학협력단 바이오헬스아카데미
- **GitHub**: https://github.com/EmmettHwang/BH2025_WOWU

### 핵심 기능
1. **교육 관리**: 강사/학생/강의/상담 통합 관리
2. **RAG 시스템**: 문서 기반 지식 검색 (FAISS + LangChain)
3. **AI 문제 생성**: RAG 기반 시험 문제 자동 생성
4. **3D 채팅**: Three.js 기반 예진이 캐릭터 음성 대화

---

## 기술 스택

### Backend
```yaml
Framework: FastAPI 0.104.0+
Runtime: Python 3.11+ (3.14 호환)
Server: Uvicorn (ASGI)
Process Manager: PM2
```

### Frontend
```yaml
Framework: Vanilla JavaScript
UI: TailwindCSS, FontAwesome
HTTP: Axios
3D: Three.js (GLB 모델)
Chart: Chart.js (모바일)
```

### Database
```yaml
Type: MySQL 8.x
Driver: PyMySQL 1.1.0+
Host: bitnmeta2.synology.me:3307
Database: bh2025
Encoding: UTF-8 (한글 지원)
```

### AI & RAG
```yaml
LLM APIs:
  - GROQ Llama 3.3 70B
  - Google Gemini 2.0
  - OpenAI GPT-4o-mini

RAG Stack:
  - Vector DB: FAISS (CPU)
  - Embeddings: sentence-transformers (jhgan/ko-sroberta-multitask)
  - Framework: LangChain Core
  - Chunking: RecursiveCharacterTextSplitter (1000/200)
```

### File Storage
```yaml
Type: FTP
Host: bitnmeta2.synology.me:2121
Use: 이미지, PDF, 문서 업로드
```

---

## 프로젝트 구조

```
BH2025_WOWU/
├── backend/
│   ├── main.py                    # FastAPI 통합 API (7600+ lines)
│   ├── rag/                       # RAG 시스템
│   │   ├── rag_chain.py          # RAG 체인 (LangChain)
│   │   ├── simple_vector_store.py # FAISS 벡터 DB
│   │   └── document_loader.py     # 문서 로더
│   └── .env                       # 환경 변수 (Git 제외)
│
├── frontend/
│   ├── index.html                 # 메인 웹 (강사용)
│   ├── app.js                     # 메인 로직 (18000+ lines)
│   ├── aesong-3d-chat.html        # 예진이 3D 채팅
│   ├── student.html               # 학생 포털
│   └── config.js                  # 설정
│
├── documents/                     # RAG 문서 폴더
│   ├── README.md                  # 자동 로딩 가이드
│   └── manual/                    # 시스템 매뉴얼 (30개)
│       └── INDEX.md               # 문서 목차
│
├── migrations/                    # DB 마이그레이션
│   ├── 0001_initial_schema.sql
│   ├── 0002_exam_bank.sql
│   └── 0003_add_menu_permissions.sql
│
├── ecosystem.config.js            # PM2 설정
├── requirements.txt               # Python 의존성 (20개)
├── check_imports.py               # 패키지 검증 스크립트
└── README.md                      # 프로젝트 개요
```

### 코드 규모
| 파일 | 줄 수 | 설명 |
|------|-------|------|
| `backend/main.py` | 7,600+ | FastAPI 통합 API |
| `frontend/app.js` | 18,000+ | 메인 프론트엔드 로직 |
| `frontend/index.html` | 500+ | 메인 UI |
| 합계 | **26,000+ lines** | 전체 코드베이스 |

---

## 환경 구성

### 필수 환경 변수 (.env)

```bash
# 데이터베이스
DB_HOST=bitnmeta2.synology.me
DB_PORT=3307
DB_USER=iyrc
DB_PASSWORD=Dodan1004!
DB_NAME=bh2025

# FTP 서버
FTP_HOST=bitnmeta2.synology.me
FTP_PORT=2121
FTP_USER=ha
FTP_PASSWORD=dodan1004~

# AI API Keys
GROQ_API_KEY=your_groq_api_key_here
GOOGLE_CLOUD_TTS_API_KEY=your_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
```

### Python 의존성 (20개)

#### Core (4개)
```
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
python-multipart>=0.0.6
pymysql>=1.1.0
```

#### Config & HTTP (3개)
```
python-dotenv>=1.0.0
httpx>=0.25.0
requests>=2.31.0
```

#### Data & Document (4개)
```
pandas>=2.1.0
numpy>=1.24.0
reportlab>=4.0.0
pillow>=10.0.0
```

#### AI & LLM (2개)
```
openai>=1.3.0
google-generativeai>=0.3.0
```

#### RAG System (6개)
```
langchain-core>=0.1.0
langchain-text-splitters>=0.0.1
faiss-cpu>=1.8.0
sentence-transformers>=2.3.1
pypdf2>=3.0.1
python-docx>=1.1.0
tiktoken>=0.5.2
```

#### Utils (1개)
```
pydantic>=2.0.0
```

### 설치 방법

```bash
# Python 의존성 설치
pip install -r requirements.txt

# 개발 도구 (선택)
pip install pytest pytest-asyncio black flake8

# 패키지 검증
python check_imports.py
```

---

## 개발 워크플로우

### 1. 로컬 개발 (샌드박스)

#### 환경
- **위치**: `/home/user/webapp/`
- **Python**: 3.11+
- **Node.js**: 필요 없음 (Vanilla JS)

#### 서버 실행
```bash
# 백엔드 실행
cd /home/user/webapp
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 프론트엔드 접속
http://localhost:8000/
```

#### 개발 사이클
```bash
# 1. 코드 수정
vim backend/main.py
vim frontend/app.js

# 2. 테스트
curl http://localhost:8000/api/health

# 3. 커밋
git add .
git commit -m "feat: 새 기능 추가"

# 4. 푸시
git push origin hun
```

### 2. 배포 (Cafe24 서버)

#### 환경
- **위치**: `/root/BH2025_WOWU/`
- **프로세스**: PM2 관리
- **도메인**: bitnmeta2.synology.me

#### 배포 프로세스
```bash
# 1. SSH 접속
ssh iyrc@bitnmeta2.synology.me

# 2. 코드 업데이트
cd /root/BH2025_WOWU/
git pull origin hun

# 3. DB 마이그레이션 (필요시)
mysql -h bitnmeta2.synology.me -P 3307 -u iyrc -pDodan1004! bh2025 \
  < migrations/0003_add_menu_permissions.sql

# 4. PM2 재시작
pm2 restart wowu-backend

# 5. 상태 확인
pm2 status
pm2 logs wowu-backend --lines 50
```

### 3. Git 브랜치 전략

```
main (프로덕션)
  ↑
  └── hun (개발 브랜치)
        ↑
        └── feature/* (기능 개발)
```

#### 커밋 메시지 규칙
```
feat: 새로운 기능 추가
fix: 버그 수정
docs: 문서 수정
chore: 빌드/설정 변경
refactor: 코드 리팩토링
style: 코드 포맷팅
test: 테스트 추가
perf: 성능 개선
```

---

## 배포 환경

### Sandbox (개발)
```yaml
위치: /home/user/webapp/
용도: 개발 및 테스트
프론트엔드: localhost:8000
백엔드 API: localhost:8000/api
자동 재시작: --reload 옵션
```

### Cafe24 (프로덕션)
```yaml
위치: /root/BH2025_WOWU/
도메인: bitnmeta2.synology.me
프론트엔드: Port 3000 (PM2: bhhs-frontend)
백엔드 API: Port 8000 (PM2: bhhs-backend)
프로세스 관리: PM2
자동 재시작: PM2 watch
```

### PM2 관리 명령어
```bash
# 시작
pm2 start ecosystem.config.js

# 재시작
pm2 restart wowu-backend

# 상태 확인
pm2 status
pm2 list

# 로그 확인
pm2 logs wowu-backend --lines 100
pm2 logs --err

# 중지
pm2 stop wowu-backend
pm2 delete wowu-backend
```

---

## 주요 기능

### 1. 교육 관리 시스템
- **강사 관리**: CRUD, 권한 관리, 비밀번호 관리
- **학생 관리**: CRUD, Excel 업로드, 사진 관리
- **강의 관리**: 시간표, 교과목, 훈련일지
- **상담 관리**: 상담 기록, AI 생활기록부 자동 생성
- **팀 관리**: 팀 프로젝트, 팀 활동일지
- **공지사항**: 마크다운 지원, 게시 기간 설정

### 2. RAG 시스템
```yaml
벡터 DB: FAISS (CPU)
임베딩 모델: jhgan/ko-sroberta-multitask
LLM API: GROQ Llama 3.3 70B, Gemini 2.0
문서 포맷: PDF, DOCX, TXT
자동 로드: startup 시 documents/ 폴더 스캔
유사도 임계값: 0.008 (0.8%)
검색 문서 수: Top-K = 10
청킹: chunk_size=1000, overlap=200
```

#### RAG API 엔드포인트
```python
POST /api/rag/upload          # 문서 업로드
GET  /api/rag/documents       # 문서 목록
POST /api/rag/chat            # RAG 기반 채팅
POST /api/rag/search          # 문서 검색
DELETE /api/rag/clear         # 벡터 DB 초기화
GET  /api/rag/status          # RAG 시스템 상태
```

### 3. 문제은행 (AI 기반)
```yaml
위치: AI 메뉴 > 문제은행
기능:
  - RAG 기반 시험 문제 자동 생성
  - 객관식/주관식/단답형/서술형 지원
  - 난이도 설정 (쉬움/보통/어려움)
  - 정답 및 해설 자동 생성
  - 참고 문서 및 페이지 표시
  - 시험 관리 (생성/조회/수정/삭제)
```

#### 문제은행 DB 테이블
```sql
exam_bank (시험 정보)
  - exam_id (PK)
  - exam_name, subject, exam_date
  - total_questions, question_type, difficulty
  - instructor_code, description
  
exam_questions (문제 상세)
  - question_id (PK)
  - exam_id (FK)
  - question_number, question_text
  - question_type, options (JSON)
  - correct_answer, explanation
  - reference_page, reference_document
```

### 4. 예진이 3D 채팅
```yaml
파일: frontend/aesong-3d-chat.html
기술: Three.js + GLB 모델
모델: /aesong-bunny.glb
음성: Web Speech API (ko-KR)
TTS: Browser SpeechSynthesis
RAG: 토글 지원 (문서 기반 답변)
```

### 5. 문서 관리
```yaml
위치: 강의 메뉴 > 문서 관리 (RAG)
기능:
  - 문서 업로드 (PDF, DOCX, TXT, PPTX, XLSX)
  - 최대 파일 크기: 100 MB
  - 문서 목록 조회 (파일명, 크기, 수정일시)
  - 다운로드 및 삭제
  - 자동 RAG 인덱싱
저장 경로: /home/user/webapp/documents/
```

---

## 데이터베이스

### 연결 정보
```yaml
Host: bitnmeta2.synology.me
Port: 3307
Database: bh2025
User: iyrc
Password: Dodan1004!
Charset: utf8mb4
```

### 주요 테이블 (15개)

#### 인증 & 권한
```sql
instructor_codes  -- 강사 코드/권한 마스터 (menu_permissions)
instructors       -- 강사 정보
```

#### 교육 관리
```sql
students          -- 학생 정보
courses           -- 교과목
holidays          -- 공휴일
timetables        -- 시간표
training_logs     -- 훈련일지
consultations     -- 상담 기록
```

#### 팀 관리
```sql
teams             -- 팀 정보
team_projects     -- 팀 프로젝트
team_activity_logs -- 팀 활동일지
```

#### AI & 문제은행
```sql
exam_bank         -- 시험 정보
exam_questions    -- 문제 상세
```

#### 기타
```sql
class_notes       -- SSIRN 메모장
notices           -- 공지사항
system_settings   -- 시스템 설정
```

### 마이그레이션
```bash
# 마이그레이션 실행
mysql -h bitnmeta2.synology.me -P 3307 -u iyrc -pDodan1004! bh2025 \
  < migrations/0003_add_menu_permissions.sql

# 테이블 확인
mysql -h bitnmeta2.synology.me -P 3307 -u iyrc -pDodan1004! bh2025 \
  -e "SHOW TABLES;"

# 강사 코드 확인
mysql -h bitnmeta2.synology.me -P 3307 -u iyrc -pDodan1004! bh2025 \
  -e "SELECT code, name, menu_permissions FROM instructor_codes;"
```

---

## 파일 저장소

### FTP 서버
```yaml
Host: bitnmeta2.synology.me
Port: 2121
User: ha
Password: dodan1004~
Base Path: /bitnmeta2_ftp/
```

### 디렉토리 구조
```
/bitnmeta2_ftp/
├── students/         -- 학생 사진
├── instructors/      -- 강사 사진
├── consultations/    -- 상담 관련 파일
├── training_logs/    -- 훈련일지 파일
├── team_activities/  -- 팀 활동 파일
└── documents/        -- 일반 문서
```

### 파일 업로드 정책
```yaml
최대 크기: 100 MB
자동 압축: 20 MB 이상 이미지 자동 압축
  - 20MB+: 1280px, 60% 품질
  - 10-20MB: 1600px, 70% 품질
압축 방식: Canvas API (클라이언트 사이드)
지원 포맷: JPG, PNG, PDF, DOCX, XLSX, PPTX, TXT
```

---

## 문서 관리

### 시스템 매뉴얼 (30개)

#### 위치
```
documents/manual/
├── INDEX.md                            # 전체 목차
├── CAFE24_QUICK_DEPLOY.md              # 긴급 배포 (5분)
├── MENU_PERMISSION_FIX.md              # 메뉴 권한 문제 해결
└── ... (27개 더)
```

#### 카테고리 (11개)
1. **시작하기** (4개) - 로컬 개발, Conda 설정, 배포 가이드
2. **시스템 관리** (4개) - DB 마이그레이션, 권한 관리, 비밀번호 관리
3. **기능 구현** (6개) - 구현 요약, 로그인, API, 파일 업로드
4. **모바일** (2개) - 모바일 배포, PWA
5. **테스트 & 최적화** (3개) - 테스트, 성능 최적화, 캐시 문제
6. **UI/UX** (1개) - 애니메이션 개선
7. **완료 보고서** (3개) - 프로젝트 완료 요약
8. **배포 & 보안** (5개) - Cafe24 배포, 방화벽 설정
9. **설정 & 설치** (1개) - 업로드 용량 설정

#### 빠른 찾기
- **배포 문제**: [CAFE24_QUICK_DEPLOY.md](documents/manual/CAFE24_QUICK_DEPLOY.md)
- **메뉴 안 보임**: [MENU_PERMISSION_FIX.md](documents/manual/MENU_PERMISSION_FIX.md)
- **DB 마이그레이션**: [DB_MIGRATION_COMPLETE.md](documents/manual/DB_MIGRATION_COMPLETE.md)
- **로컬 개발**: [LOCAL_DEVELOPMENT.md](documents/manual/LOCAL_DEVELOPMENT.md)
- **API 목록**: [API_SUMMARY.md](documents/manual/API_SUMMARY.md)

---

## 주요 API 엔드포인트

### 인증
```
POST /api/login              -- 로그인
POST /api/logout             -- 로그아웃
```

### 강사/학생 관리
```
GET    /api/instructors      -- 강사 목록
POST   /api/instructors      -- 강사 추가
PUT    /api/instructors/:id  -- 강사 수정
DELETE /api/instructors/:id  -- 강사 삭제

GET    /api/students         -- 학생 목록
POST   /api/students         -- 학생 추가
POST   /api/students/upload-excel -- Excel 업로드
```

### RAG & 문서
```
POST   /api/rag/upload       -- 문서 업로드
GET    /api/rag/documents    -- 문서 목록
POST   /api/rag/chat         -- RAG 채팅
POST   /api/rag/search       -- 문서 검색
DELETE /api/rag/clear        -- 벡터 DB 초기화
GET    /api/rag/status       -- RAG 상태
```

### 문제은행
```
POST   /api/exam-bank/generate -- 문제 생성
POST   /api/exam-bank/save     -- 시험 저장
GET    /api/exam-bank/list     -- 시험 목록
GET    /api/exam-bank/:id      -- 시험 조회
DELETE /api/exam-bank/:id      -- 시험 삭제
PUT    /api/exam-bank/:id      -- 시험 수정
```

### 문서 관리
```
POST   /api/documents/upload          -- 문서 업로드
GET    /api/documents/list            -- 문서 목록
GET    /api/documents/download/:name  -- 문서 다운로드
DELETE /api/documents/:name           -- 문서 삭제
```

### Swagger UI
```
http://localhost:8000/docs
```

---

## 개발 도구

### 패키지 검증
```bash
# 실제 사용 중인 패키지 확인
python check_imports.py
```

### 코드 포맷팅 (선택)
```bash
pip install black flake8
black backend/
flake8 backend/
```

### 테스트 (선택)
```bash
pip install pytest pytest-asyncio
pytest backend/tests/
```

---

## 트러블슈팅

### 자주 발생하는 문제

#### 1. 메뉴가 보이지 않음
→ [MENU_PERMISSION_FIX.md](documents/manual/MENU_PERMISSION_FIX.md) 참고

#### 2. Git 잠금 파일 에러
```bash
del ".git\index.lock"  # Windows
rm .git/index.lock     # Linux/Mac
```

#### 3. RAG 유사도 낮음
→ documents/ 폴더에 문서 추가 후 재시작

#### 4. DB 연결 실패
→ .env 파일 확인, 방화벽 설정 확인

#### 5. PM2 재시작 안됨
```bash
pm2 delete all
pm2 start ecosystem.config.js
```

---

## 버전 정보

### 현재 버전: 3.5
- ✅ RAG 시스템 통합
- ✅ 문제은행 기능
- ✅ 예진이 3D 채팅 RAG 지원
- ✅ 문서 관리 시스템
- ✅ 메뉴 권한 관리

### 다음 버전: 3.6 (계획)
- [ ] RAG 성능 개선 (임베딩 재생성)
- [ ] 문제은행 다중 LLM 지원
- [ ] 실시간 알림 시스템
- [ ] 모바일 앱 PWA 개선

---

## 참고 자료

### 공식 문서
- [전체 매뉴얼 목차](documents/manual/INDEX.md)
- [README.md](README.md)
- [API 문서](http://localhost:8000/docs)

### GitHub
- **Repository**: https://github.com/EmmettHwang/BH2025_WOWU
- **Issues**: https://github.com/EmmettHwang/BH2025_WOWU/issues
- **Pull Requests**: https://github.com/EmmettHwang/BH2025_WOWU/pulls

### 문의
- GitHub Issues를 통한 버그 리포트 및 기능 제안

---

**마지막 업데이트**: 2024-12-31  
**문서 버전**: 1.0  
**작성자**: AI Assistant
