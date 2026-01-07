# 교육관리 플랫폼

**통합 교육 관리 시스템 + RAG 기반 지식 검색 + AI 문제 생성**

## 🎓 프로젝트 개요
FastAPI 백엔드 + Vanilla JavaScript 프론트엔드 + RAG 시스템으로 구성된 통합 솔루션입니다.

- **완성일**: 2026년 01월 08일
- **버전**: v1.1.202601080107
- **상태**: ✅ 프로덕션 배포 완료

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
??????????_WOWU/
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
- **[개발 환경 종합 가이드](./documents/manual/DEVELOPMENT_ENVIRONMENT.md)** ⭐ 신규 개발자 필독!
- [로컬 개발 환경 설정](./documents/manual/LOCAL_DEVELOPMENT.md)
- [Cafe24 배포 가이드](./documents/manual/DEPLOY_CAFE24.md)
- [긴급 배포 (5분)](./documents/manual/CAFE24_QUICK_DEPLOY.md)

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
| Password | `xxxxxxxx` |
| Database | `xxxxxxx` |

#### 2. FTP 서버 (Synology NAS)
| 항목 | 값 |
|------|-----|
| Host | `bitnmeta2.synology.me` |
| Port | `2121` |
| User | `xxxxxxx` |
| Password | `xxxxxxx` |

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
DB_PASSWORD=xxxxxx
DB_NAME=xxxxx

# FTP 서버
FTP_HOST=bitnmeta2.synology.me
FTP_PORT=2121
FTP_USER=xxxxxx
FTP_PASSWORD=xxxxxx

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

## 🎯 최신 업데이트 (v1.1.202601080107)

### ✅ 최근 변경사항 (2026-01-08)

#### 🗃️ DB 관리 시스템 (신규)
- **DB 백업/복구**: 완전한 데이터베이스 백업 및 복구 기능
- **테이블별 선택 복구**: 특정 테이블만 선택하여 복구 가능
- **테이블별 선택 삭제**: 특정 테이블만 선택하여 초기화 가능
- **자동 백업**: 복구/초기화 전 자동 안전 백업 생성
- **진행 애니메이션**: 백업/복구/초기화 시 단계별 진행 표시
- **완료 화면**: 작업 완료 후 결과 요약 팝업 (2.5초)

#### 🔐 긴급 관리자 계정
- **아이디**: `root`
- **비밀번호**: `xhRl1004!@#`
- DB에 강사가 없어도 항상 접속 가능한 하드코딩 계정

#### 📊 성적 메뉴 (신규)
- **문제은행**: RAG 기반 시험 문제 자동 생성
- **온라인시험**: 시험 관리 (예정)
- **선착순 퀴즈**: 퀴즈 관리 (예정)
- **과제관리**: 과제 관리 (예정)

#### 🎨 UI/UX 개선
- **모달 알림**: 모든 `alert()` → 스타일된 `showAlert()` 모달로 변경
- **확인 대화상자**: 모든 `confirm()` → 스타일된 `showConfirm()` 모달로 변경
- **학생 등록 페이지**: 별도 회원가입 페이지 추가

### ✅ 이전 주요 기능
- **데이터베이스 로컬 전환**: 외부 DB → 로컬 DB (localhost)
- **systemd 서비스 등록**: 서버 부팅 시 자동 시작
- **문서 관리**: 업로드/다운로드/삭제
- **예진이 3D 채팅**: RAG 토글 추가, 문서 기반 답변
- **메뉴 권한**: instructor_codes 테이블 menu_permissions 관리
- **모바일 자동 분기**: User Agent 감지 후 자동 리다이렉트

### 🐛 수정된 버그
- DB 관리 모달 포커스 오류 수정
- 백업/복구 후 페이지 데이터 새로고침 안 되는 문제 수정
- `closeDbManagementModal()`에서 액션 초기화로 인한 작업 실패 수정

---

## 📞 지원

### 문제 해결
1. [메뉴 권한 문제](documents/manual/MENU_PERMISSION_FIX.md)
2. [캐시 문제](documents/manual/CACHE_FIX_GUIDE.md)
3. [업로드 용량 문제](documents/manual/UPLOAD_CAPACITY_INFO.md)

### 개발자 문의
- GitHub Issues: https://github.com/EmmettHwang/BH2025_WOWU/issues

---

**마지막 업데이트**: 2026-01-08 01:07
**버전**: v1.1.202601080107
**버전 형식**: v{메이저}.{마이너}.{년월일시분}
**총 코드 라인**: 30,000+ (backend: 8,100+ / frontend: 21,000+)
**API 엔드포인트**: 125+
**상태**: ✅ 프로덕션 배포 완료 + 🔍 RAG 시스템 + 📝 문제은행 + 🎓 교육관리 + 🗃️ DB 관리
