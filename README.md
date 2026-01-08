# BH2025 바이오헬스 교육관리 플랫폼

## 📌 버전 정보
- **현재 버전**: v3.8.0
- **최종 업데이트**: 2026년 01월 08일

## 🎉 최근 업데이트 (v3.8.0)

### ✨ 신규 기능
1. **신규가입 설정** (시스템 등록)
   - 모집중인 과정 다중 선택 체크박스
   - 관심분야 키워드 설정 (10개 기본값 포함)
   - 테마 색상 프리셋 (5가지)
   - register.html 신규가입 페이지 완전 복원

2. **강사코드 권한 관리 대폭 개선**
   - ✅ 카테고리별 계층 구조 그룹핑
     - 시스템 관리, 과정, 학생, 강의, 성적, AI, 팀
   - ✅ 상위 메뉴 체크 시 하위 메뉴 일괄 선택/해제
   - ✅ 부분 선택 시 indeterminate 상태 표시
   - ✅ **권한 없는 메뉴 완전히 숨김** (사이드바에서 제거)
   - ✅ 예진이 만나기 예외 처리 제거 (일반 권한 체크)

### ⚡ 성능 최적화
1. **적응형 폴링** (RAG 진행률 조회)
   - 3초 → 5초 → 10초 → 30초 자동 조정
   - API 트래픽 60-75% 감소
   - 진행 없을 때 자동으로 폴링 간격 증가

2. **로그 필터링**
   - 백엔드: RAG 진행률 조회 로그 제거
   - 프론트엔드: 대시보드 새로고침 로그 제거
   - 로그 양 90% 감소

### 🎨 UI/UX 개선
1. **매트릭스 애니메이션**
   - RAG Embedding 단계 (40-90%)에서 표시
   - Binary 레인 애니메이션 (Matrix 스타일)
   - 모달 종료 시 자동 정리

2. **메뉴 구조 최적화**
   - 문제은행: 성적 → 강의 메뉴로 이동
   - 계층 구조로 메뉴 그룹핑

### 🔧 시스템 안정성
1. **DB 마이그레이션**
   - 신규가입 설정 컬럼 추가 (open_courses, interest_keywords)
   - 기본 관심분야 키워드 자동 입력
     - AI, 로봇, 빅데이터, 프로그래밍, 헬스케어
     - 데이터엔지니어, 데이터과학자, 의과학자
     - ML엔지니어, AI보안엔지니어, AI APP개발
     - 임베디드&온디바이스AI, 전문도메인융합
     - 첨단산업AX, AI HW엔지니어

2. **배포 환경 개선**
   - ecosystem.config.cjs Linux 경로 수정
   - PYTHONPATH 환경변수 설정
   - Python 모듈 경로 문제 해결

---

## 📅 개발 이력
- **2026년 01월 08일**: v3.8.0 - 권한 관리 개선, 신규가입 설정 추가
- **2026년 01월 06일**: v3.7.0 - RAG 최적화, 성능 개선
- **2025년**: 초기 개발 및 기능 구현

---
### 개략적인 개발 환경은 다음과 같음 
<img width="425" height="406" alt="image" src="https://github.com/user-attachments/assets/2ba34988-415f-4876-9a9f-000f1fa842ac" />


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

### 긴급조치 (Cafe24 서버가 응답 없을 때)
# 1) 강제 재시작
pm2 delete bh2025-backend
pm2 start ecosystem.config.cjs
pm2 save

# 2) 메모리 부족 시
pm2 restart all

# 3) 여전히 안 되면
sudo systemctl restart pm2-root
# 1) 강제 재시작
pm2 delete bh2025-backend
pm2 start ecosystem.config.cjs
pm2 save

# 2) 메모리 부족 시
pm2 restart all

# 3) 여전히 안 되면
sudo systemctl restart pm2-root

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

## 🎯 최신 업데이트 (v3.7)

### ⚡ 성능 최적화 및 UX 개선 (2026-01-08)

#### 🚀 적응형 폴링 시스템
- **스마트 폴링**: 진행 상황에 따라 자동으로 간격 조정
  - 빠른 진행 시: 3초 간격 유지 (즉각 피드백)
  - 변화 없음 2회: 5초로 증가
  - 변화 없음 5회: 10초로 증가
  - 변화 없음 10회: 30초로 증가 (최대)
  - 진행률 변화 감지 시: 즉시 3초로 리셋!
- **트래픽 절감**: 평균 60~75% API 요청 감소
- **배터리 절약**: 모바일 환경에서 효율적

#### 🧹 로그 시스템 대폭 정리
- **불필요한 로그 제거**:
  - RAG 진행률 조회 200 OK (3초마다 폴링)
  - 대시보드 새로고침 8개 API (courses, students, instructors 등)
- **로그 파일 크기**: 90% 감소
- **유지되는 중요 로그**:
  - ✅ POST/PUT/DELETE (데이터 변경)
  - ✅ 로그인 실패 (401, 보안)
  - ✅ 에러 (4xx, 5xx)
  - ✅ 파일 업로드/다운로드

#### 📚 메뉴 구조 개선
- **문제은행 위치 변경**: 성적 메뉴 → 강의 메뉴
- **논리적 그룹화**:
  - 강의: 시간표, 훈련일지, 문서관리(RAG), 문제은행
  - 성적: 온라인시험, 온라인퀴즈, 과제제출

#### 📊 성능 개선 효과
| 항목 | Before | After | 개선율 |
|------|--------|-------|--------|
| API 트래픽 (느린 인덱싱) | 600회/30분 | 150회/30분 | **75%↓** |
| 로그 발생량 (하루) | ~5000줄 | ~500줄 | **90%↓** |
| 대시보드 새로고침 로그 | 8줄 | 0줄 | **100%↓** |

#### 🔧 기술 구현
```javascript
// 적응형 폴링
if (currentProgress !== lastProgress) {
    resetPollingInterval(3000);  // 변화 감지 → 3초
} else {
    noChangeCount++;
    if (noChangeCount === 2) resetPollingInterval(5000);
    if (noChangeCount === 5) resetPollingInterval(10000);
    if (noChangeCount === 10) resetPollingInterval(30000);
}
```

```python
# 로그 필터
class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if '200 OK' in message:
            # RAG 진행률 & 대시보드 API 제외
            if '/api/rag/indexing-progress/' in message:
                return False
            for api in dashboard_apis:
                if f'GET {api} ' in message:
                    return False
        return True
```

#### 📦 커밋 히스토리 (v3.7)
- `b6d4a8c`: 버전 v3.6.0 업데이트 및 README 갱신
- `c0314ef`: 문제은행 메뉴 위치 변경 (성적 → 강의)
- `a4db72c`: RAG 진행률 조회 API 로그 제거
- `607e90b`: 적응형 폴링으로 API 트래픽 대폭 감소
- `a37edb6`: 대시보드 새로고침 API 로그 제거

---

## 📜 이전 버전 (v3.6)

### 🎬 RAG 인덱싱 UX 대폭 개선 (2026-01-08)

#### ✨ 새로운 기능
- **매트릭스 애니메이션**: The Matrix 스타일 세로로 떨어지는 초록색 바이너리 코드 (40~90% 구간)
- **진행률 디스크 저장**: 서버 재시작 시에도 진행률 유지 (`indexing_progress.json`)
- **실시간 진행률**: 배치별 세밀한 진행률 업데이트 (50%→90%)
- **백그라운드 처리**: 인덱싱 중에도 다른 작업 가능, "빠져나가기" 버튼
- **단계별 애니메이션**:
  - 0~20%: Parsing Stage (PDF + 광선 빔)
  - 20~40%: Chunking Stage (회전하는 큐브)
  - 40~90%: **Embedding Stage (매트릭스 레인)** 🎬
  - 90~100%: Indexing Stage (벡터 공간 정착)

#### 🔥 수정된 주요 버그
- **502 Bad Gateway 해결**: 동기 → FastAPI BackgroundTasks 비동기 처리
- **진행률 손실 문제**: 재시작 시 진행률 복원 (1시간 이내 항목)
- **화면 멈춤 현상**: 백엔드 14% 진행인데 프론트 5% 멈춤 → 실시간 업데이트
- **progress_callback 에러**: VectorStoreManager에 콜백 파라미터 추가
- **서버 블로킹**: 인덱싱으로 인한 전체 서버 블로킹 → 백그라운드 처리

#### 📊 커밋 히스토리 (v3.6)
- `38ad2d1`: 진행률 디스크 영구 저장
- `46c27e8`: UX 개선 (애니메이션, 빠져나가기)
- `7fb4ba4`: 502 에러 해결 (백그라운드 태스크)
- `37530c1`: progress_callback 파라미터 추가
- `60be2d2`: 떠다니는 애니메이션 제거
- `6c9301d`: 가로 스트림 활성화
- `90ef5f8`: 진행률별 애니메이션 자동 전환
- `a653ce8`: 폴링 최적화 및 로그 정리
- `8e0d4b1`: 매트릭스 스타일 애니메이션 추가

---

## 📜 이전 버전 (v3.5)

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

**마지막 업데이트**: 2026-01-08  
**버전**: 3.7.0  
**상태**: ✅ 프로덕션 배포 완료 + ⚡ 적응형 폴링 + 🧹 로그 최적화 + 🎬 매트릭스 애니메이션 + 🔍 RAG 시스템 + 📝 문제은행 + 🎓 교육관리
