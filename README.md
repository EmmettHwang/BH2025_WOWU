# BH2025 바이오헬스 교육관리 플랫폼

> **보건복지부(한국보건산업진흥원) K-디지털 트레이닝**
> 우송대학교산학협력단 바이오헬스아카데미 올인원테크 이노베이터

**통합 교육 관리 시스템 + RAG 기반 지식 검색 + AI 문제 생성**

## 🎓 프로젝트 개요

바이오헬스 분야 K-디지털 트레이닝 과정을 위한 **올인원 교육관리 플랫폼**입니다.
FastAPI 백엔드 + Vanilla JavaScript 프론트엔드 + RAG 시스템으로 구성된 통합 솔루션입니다.

- **완성일**: 2026년 01월 07일
- **버전**: v3.5.1
- **상태**: ✅ 프로덕션 배포 완료

### 개략적인 개발 환경
<img width="425" height="406" alt="image" src="https://github.com/user-attachments/assets/2ba34988-415f-4876-9a9f-000f1fa842ac" />

---

## 🚀 빠른 시작

### 개발 환경 실행
```bash
# 백엔드 실행
cd /home/user/webapp
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 프론트엔드 접속
http://localhost:8000/
```

### 배포 (Cafe24 서버)
```bash
# 최신 코드 받기
git pull origin main

# DB 마이그레이션 (필요시)
mysql -h [DB_HOST] -u [DB_USER] -p[DB_PASSWORD] minilms < migrations/0003_add_menu_permissions.sql

# 서비스 재시작
systemctl restart minilms
```

### 서비스 관리
```bash
systemctl start minilms    # 시작
systemctl stop minilms     # 중지
systemctl restart minilms  # 재시작
systemctl status minilms   # 상태 확인
journalctl -u minilms -f   # 로그 실시간 확인
```

---

## 📂 프로젝트 구조

```
BH2025_WOWU/
├── backend/
│   ├── main.py                 # FastAPI 통합 API (8,554 lines, 120+ endpoints)
│   ├── rag/                    # RAG 시스템
│   │   ├── rag_chain.py       # RAG 체인 (LangChain)
│   │   ├── simple_vector_store.py  # FAISS 벡터 DB
│   │   └── document_loader.py      # 문서 로더
│   ├── documents/              # 문서 저장소
│   ├── rag_documents/          # RAG 전용 문서
│   ├── uploads/                # 업로드 파일
│   └── .env                    # 환경 변수
├── frontend/
│   ├── index.html              # 메인 웹 (강사용 데스크톱)
│   ├── app.js                  # 메인 로직 (20,825 lines)
│   ├── aesong-3d-chat.html     # 예진이 3D 채팅
│   ├── student.html            # 학생용 페이지
│   ├── mobile/                 # 모바일 전용 UI
│   └── config.js               # 설정
├── documents/                  # RAG 문서 폴더
│   └── manual/                 # 시스템 매뉴얼 (39개 문서)
├── Deploy_Docs/                # 배포 가이드 (10개 문서)
├── migrations/                 # DB 마이그레이션
│   ├── 0001_initial_schema.sql
│   ├── 0002_exam_bank.sql
│   └── 0003_add_menu_permissions.sql
├── ecosystem.config.js         # PM2 설정 (프로덕션)
├── requirements.txt            # Python 의존성 (20개)
├── package.json                # Node.js 의존성
└── README.md                   # 이 파일
```

---

## ✨ 주요 기능

### 📚 교육 관리 시스템
- **강사/학생 관리**: CRUD, Excel 업로드, 사진 관리
- **강의 관리**: 시간표, 교과목, 훈련일지
- **상담 관리**: 상담 기록, AI 생활기록부 자동 생성
- **팀 관리**: 팀 프로젝트, 팀 활동일지
- **공지사항**: 마크다운 지원, 게시 기간 설정

### 🤖 AI 기능
- **RAG 지식 검색**: 문서 기반 질의응답 (GROQ Llama 3.3 70B, Gemini 2.0)
- **문제은행**: RAG 기반 시험 문제 자동 생성
- **AI 생활기록부**: OpenAI GPT 기반 자동 생성
- **예진이 3D 채팅**: Three.js 3D 캐릭터 + 음성 대화

### 🔍 RAG (Retrieval-Augmented Generation) 시스템
- **벡터 DB**: FAISS IndexFlatL2 (CPU)
- **임베딩 모델**: `jhgan/ko-sroberta-multitask` (한국어 특화, 768차원)
- **LLM API**: GROQ Llama 3.3 70B (기본), Google Gemini 2.0 Flash (대체)
- **문서 포맷**: PDF, DOCX, TXT
- **자동 문서 로드**: startup 시 `documents/` 폴더 스캔
- **청크 설정**: 1000자 (overlap 200자)
- **유사도 임계값**: 30% (min_similarity=0.3)
- **검색 문서 수**: Top-K = 5

---

## 🛠️ 기술 스택

### Backend
- **Framework**: FastAPI
- **DB**: MySQL 8.x, PyMySQL
- **RAG**: LangChain, FAISS, sentence-transformers
- **AI**: OpenAI API, GROQ API, Google Gemini API
- **파일 처리**: pypdf2, python-docx, Pillow

### Frontend
- **Framework**: Vanilla JavaScript
- **UI**: TailwindCSS, FontAwesome
- **3D**: Three.js
- **HTTP**: Axios
- **차트**: Chart.js (모바일)

### DevOps
- **프로세스 관리**: PM2
- **버전 관리**: Git, GitHub
- **배포**: Cafe24 리눅스 서버

---

## 🌟 프로젝트 핵심 특징

### 1. 올인원 통합 시스템
- 교육 관리 + RAG 지식 검색 + AI 문제 생성이 하나의 플랫폼에 통합
- 강사/학생/관리자 모든 역할 지원

### 2. 한국어 최적화
- 한국어 특화 임베딩 모델 (`jhgan/ko-sroberta-multitask`)
- 한글 폰트 지원 (PDF 생성)
- Windows 한글 경로 처리

### 3. 반응형 UI
- 데스크톱/모바일 자동 분기
- 디바이스 감지 후 적절한 UI로 리다이렉트
- PWA 지원

### 4. 권한 기반 메뉴 시스템
- JSON 기반 동적 메뉴 생성
- 강사 코드별 세부 권한 관리
- 역할 기반 접근 제어 (RBAC)

### 5. 성능 최적화
- 5분 캐시 + 백그라운드 업데이트
- FAISS CPU 벡터 DB (서버 친화적)
- PM2 멀티 워커 (4개)

---

## 📖 문서 가이드

### 🚀 시작하기
- **[개발 환경 종합 가이드](documents/manual/DEVELOPMENT_ENVIRONMENT.md)** ⭐ 신규 개발자 필독!
- [로컬 개발 환경 설정](documents/manual/LOCAL_DEVELOPMENT.md)
- [Cafe24 배포 가이드](documents/manual/DEPLOY_CAFE24.md)
- [긴급 배포 (5분)](documents/manual/CAFE24_QUICK_DEPLOY.md)

### 🔧 시스템 관리
- [데이터베이스 마이그레이션](documents/manual/DB_MIGRATION_COMPLETE.md)
- [강사 권한 관리](documents/manual/MENU_PERMISSION_FIX.md)
- [비밀번호 관리](documents/manual/INSTRUCTOR_PASSWORD_MANAGEMENT.md)

### 🎯 기능 구현
- [RAG 시스템 개요](documents/manual/IMPLEMENTATION_SUMMARY.md)
- [로그인 시스템](documents/manual/LOGIN_FEATURE.md)
- [파일 업로드 가이드](documents/manual/파일업로드_가이드.md)
- [음성 API 가이드](documents/manual/SPEECH_API_GUIDE.md)

### 📱 모바일
- [모바일 배포 가이드](documents/manual/MOBILE_DEPLOYMENT_GUIDE.md)
- [PWA 가이드](documents/manual/PWA_GUIDE.md)

### 🧪 테스트 & 최적화
- [테스트 가이드](documents/manual/TESTING_GUIDE.md)
- [성능 최적화](documents/manual/PERFORMANCE_OPTIMIZATION.md)
- [캐시 문제 해결](documents/manual/CACHE_FIX_GUIDE.md)

### 📊 완료 보고서
- [프로젝트 완료 요약](documents/manual/COMPLETION_SUMMARY.md)
- [구현 완료 보고서](documents/manual/COMPLETION_REPORT.md)
- [애니메이션 개선 요약](documents/manual/ANIMATION_ENHANCEMENT_SUMMARY.md)

### 🔐 보안 & 설정
- [Cafe24 방화벽 설정](documents/manual/CAFE24_FIREWALL_SETUP.md)
- [업로드 용량 정보](documents/manual/UPLOAD_CAPACITY_INFO.md)

### 📚 API 문서
- [API 요약](documents/manual/API_SUMMARY.md)
- **Swagger UI**: `http://localhost:8000/docs`

---

## 🔧 환경 설정

### 외부 시스템 접속 정보

#### 1. 데이터베이스 (MySQL/MariaDB)
| 항목 | 값 |
|------|-----|
| Host | `localhost` |
| Port | `3306` |
| User | `iyrc` |
| Password | `dodan1004` |
| Database | `minilms` |

#### 2. FTP 서버 (Synology NAS)
| 항목 | 값 |
|------|-----|
| Host | `bitnmeta2.synology.me` |
| Port | `2121` |
| User | `ha` |
| Password | `dodan1004~` |

**FTP 경로:**
| 용도 | 경로 |
|------|------|
| 상담일지 | `/homes/ha/camFTP/BH2025/guidance` |
| 훈련일지 | `/homes/ha/camFTP/BH2025/train` |
| 학생 | `/homes/ha/camFTP/BH2025/student` |
| 강사 | `/homes/ha/camFTP/BH2025/teacher` |
| 팀/프로젝트 | `/homes/ha/camFTP/BH2025/team` |

#### 3. AI API 엔드포인트
| 서비스 | URL | 모델 |
|--------|-----|------|
| GROQ | `https://api.groq.com/openai/v1/chat/completions` | `llama-3.3-70b-versatile`, `gemma2-9b-it` |
| Google Gemini | `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent` | `gemini-2.0-flash-exp` |
| OpenAI | `https://api.openai.com/v1/chat/completions` | GPT (생활기록부용) |

### 필수 환경 변수 (.env)
```bash
# 데이터베이스
DB_HOST=localhost
DB_PORT=3306
DB_USER=iyrc
DB_PASSWORD=dodan1004
DB_NAME=minilms

# FTP 서버
FTP_HOST=bitnmeta2.synology.me
FTP_PORT=2121
FTP_USER=ha
FTP_PASSWORD=dodan1004~

# AI API Keys (각 서비스에서 발급 필요)
GROQ_API_KEY=your_groq_api_key
GOOGLE_CLOUD_TTS_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 의존성 설치
```bash
# Python 의존성 (총 20개 패키지, 최적화 완료)
pip install -r requirements.txt

# RAG 시스템 필수 패키지 (이미 requirements.txt에 포함)
# - langchain-core, langchain-text-splitters
# - faiss-cpu, sentence-transformers
# - pypdf2, python-docx, tiktoken
```

---

## 📊 프로젝트 규모

- **총 코드 라인**: 29,379+ 라인
  - Backend (main.py): 8,554 라인
  - Frontend (app.js): 20,825 라인
- **API 엔드포인트**: 120+ 개
- **데이터베이스 테이블**: 15+ 개
- **문서화**: 49개 매뉴얼 (시스템 39개 + 배포 10개)

---

## 🎯 최신 업데이트 (v3.5)

### ✅ 최근 변경사항 (2026-01-07)
- **데이터베이스 로컬 전환**: 외부 DB(`www.kdt2025.com`) → 로컬 DB(`localhost`)
  - Host: `www.kdt2025.com` → `localhost`
  - Database: `bh2025` → `minilms`
  - 로컬 MariaDB 10.6.22 사용
- **데이터베이스 이름 변경**: `bh2025` → `minilms`
  - 설정 파일 업데이트 (.env, .env.example)
  - MySQL 데이터베이스 마이그레이션 완료 (19개 테이블 이동)
- **systemd 서비스 등록**: 서버 부팅 시 자동 시작
  - 서비스 파일: `/etc/systemd/system/minilms.service`
  - PM2 대신 systemd로 프로세스 관리

### ✅ 완료된 기능
- **문서 관리**: 시스템관리 → 강의 메뉴로 이동, 업로드/다운로드/삭제
- **문제은행**: RAG 기반 시험 문제 자동 생성 (AI 메뉴)
- **RAG 시스템**: 유사도 임계값 조정, DB 직접 조회 (강사수/학생수)
- **예진이 3D 채팅**: RAG 토글 추가, 문서 기반 답변
- **메뉴 권한**: instructor_codes 테이블 menu_permissions 관리
- **모바일 자동 분기**: User Agent 감지 후 자동 리다이렉트
- **캐싱 시스템**: 5분 캐시 + 백그라운드 업데이트

### 🐛 수정된 버그
- 강사 권한에서 새 메뉴(문서 관리, 문제은행) 표시 안 되는 문제
- RAG 유사도 점수 낮은 문제 (임계값 0.3으로 조정)
- 강사 수 조회 SQL 에러 (role 컬럼 없음 → 상위 10명 목록으로 변경)
- 시간표 ENUM 값 수정 (workship → practice)
- Windows 한글 경로 문제 (임시 폴더 사용)

---

## 🔗 링크

- **GitHub Repository**: https://github.com/EmmettHwang/BH2025_WOWU
- **Branch**: `hun` (개발), `main` (프로덕션)
- **Latest PR**: https://github.com/EmmettHwang/BH2025_WOWU/compare/main...hun

---

## 📞 지원

### 문제 해결
1. [메뉴 권한 문제](documents/manual/MENU_PERMISSION_FIX.md)
2. [캐시 문제](documents/manual/CACHE_FIX_GUIDE.md)
3. [업로드 용량 문제](documents/manual/UPLOAD_CAPACITY_INFO.md)

### 개발자 문의
- GitHub Issues: https://github.com/EmmettHwang/BH2025_WOWU/issues

---

**마지막 업데이트**: 2026-01-07
**버전**: 3.5.1
**총 코드 라인**: 29,379+ (backend: 8,554 / frontend: 20,825)
**API 엔드포인트**: 120+
**상태**: ✅ 프로덕션 배포 완료 + 🔍 RAG 시스템 + 📝 문제은행 + 🎓 교육관리
