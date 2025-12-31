# BH2025 바이오헬스 교육관리 플랫폼

> **보건복지부(한국보건산업진흥원) K-디지털 트레이닝**  
> 우송대학교산학협력단 바이오헬스아카데미 올인원테크 이노베이터

통합 교육 관리 시스템 + RAG 기반 지식 검색 + AI 문제 생성

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
git pull origin hun

# DB 마이그레이션 (필요시)
mysql -h [DB_HOST] -u [DB_USER] -p[DB_PASSWORD] [DB_NAME] < migrations/0003_add_menu_permissions.sql

# PM2 재시작
pm2 restart wowu-backend
```

---

## 📂 프로젝트 구조

```
BH2025_WOWU/
├── backend/
│   ├── main.py                 # FastAPI 통합 API (7600+ lines)
│   ├── rag/                    # RAG 시스템
│   │   ├── rag_chain.py       # RAG 체인 (LangChain)
│   │   ├── simple_vector_store.py  # FAISS 벡터 DB
│   │   └── document_loader.py      # 문서 로더
│   └── .env                    # 환경 변수
├── frontend/
│   ├── index.html              # 메인 웹 (강사용)
│   ├── app.js                  # 메인 로직 (18000+ lines)
│   ├── aesong-3d-chat.html     # 예진이 3D 채팅
│   └── config.js               # 설정
├── documents/                  # RAG 문서 폴더
│   └── manual/                 # 시스템 매뉴얼
├── migrations/                 # DB 마이그레이션
│   ├── 0001_initial_schema.sql
│   ├── 0002_exam_bank.sql
│   └── 0003_add_menu_permissions.sql
├── ecosystem.config.js         # PM2 설정
├── requirements.txt            # Python 의존성
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
- **벡터 DB**: FAISS (CPU)
- **임베딩 모델**: `jhgan/ko-sroberta-multitask` (한국어 특화)
- **LLM API**: GROQ Llama 3.3 70B, Google Gemini 2.0
- **문서 포맷**: PDF, DOCX, TXT
- **자동 문서 로드**: startup 시 `documents/` 폴더 스캔
- **유사도 임계값**: 0.8% (현재 임베딩 상태 기준)
- **검색 문서 수**: Top-K = 10

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

## 📖 문서 가이드

### 🚀 시작하기
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

### 필수 환경 변수 (.env)
```bash
# 데이터베이스
DB_HOST=your_db_host
DB_PORT=3307
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=bh2025

# FTP 서버
FTP_HOST=your_ftp_host
FTP_PORT=2121
FTP_USER=your_ftp_user
FTP_PASSWORD=your_ftp_password

# AI API Keys
GROQ_API_KEY=your_groq_api_key
GOOGLE_CLOUD_TTS_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 의존성 설치
```bash
# Python 의존성
pip install -r requirements.txt

# RAG 시스템 필수 패키지
pip install langchain langchain-core langchain-text-splitters
pip install faiss-cpu sentence-transformers
pip install pypdf2 python-docx tiktoken
```

---

## 🎯 최신 업데이트 (v3.5)

### ✅ 완료된 기능
- **문서 관리**: 시스템관리 → 강의 메뉴로 이동, 업로드/다운로드/삭제
- **문제은행**: RAG 기반 시험 문제 자동 생성 (AI 메뉴)
- **RAG 시스템**: 유사도 임계값 조정, DB 직접 조회 (강사수/학생수)
- **예진이 3D 채팅**: RAG 토글 추가, 문서 기반 답변
- **메뉴 권한**: instructor_codes 테이블 menu_permissions 관리

### 🐛 수정된 버그
- 강사 권한에서 새 메뉴(문서 관리, 문제은행) 표시 안 되는 문제
- RAG 유사도 점수 낮은 문제 (임계값 0.008로 조정)
- 강사 수 조회 SQL 에러 (role 컬럼 없음 → 상위 10명 목록으로 변경)

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

**마지막 업데이트**: 2024-12-31  
**버전**: 3.5  
**상태**: ✅ 프로덕션 배포 완료 + 🔍 RAG 시스템 + 📝 문제은행 + 🎓 교육관리
