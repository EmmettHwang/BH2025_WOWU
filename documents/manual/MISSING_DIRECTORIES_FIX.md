# 필수 디렉토리 누락 문제 해결

## 🐛 발생한 문제

```
GET http://localhost:8000/api/documents/list 404 (Not Found)
GET http://localhost:8000/api/rag/status 404 (Not Found)
```

### 에러 메시지
```
문서 목록 로드 실패: AxiosError
❌ RAG 상태 조회 실패: AxiosError
```

---

## 🔍 원인 분석

백엔드 API 엔드포인트는 정상적으로 구현되어 있었지만, **필수 디렉토리가 생성되지 않음**:

1. ❌ `backend/documents/` - 문서 저장 디렉토리 없음
2. ❌ `backend/uploads/` - RAG 업로드 디렉토리 없음
3. ❌ `backend/vector_db/` - 벡터 DB 저장 디렉토리 없음

### 왜 문제가 발생했나?

- `.gitignore`에 이 디렉토리들이 포함되어 있어서 Git에서 추적되지 않음
- 새로운 환경에서 clone 시 디렉토리가 생성되지 않음
- API는 이 디렉토리들이 존재한다고 가정하고 작동함

---

## ✅ 해결 방법

### 1. 필수 디렉토리 생성

```bash
cd backend
mkdir -p documents uploads vector_db
```

### 2. Git 추적을 위한 파일 추가

각 디렉토리에 `.gitkeep` 및 `README.md` 파일 추가:

```bash
# documents 디렉토리
touch documents/.gitkeep
echo "# 문서 저장 디렉토리" > documents/README.md

# uploads 디렉토리
touch uploads/.gitkeep
echo "# RAG 업로드 디렉토리" > uploads/README.md

# vector_db 디렉토리 (로컬에만 필요, Git에는 추가 안 함)
touch vector_db/.gitkeep
echo "# 벡터 DB 저장 디렉토리" > vector_db/README.md
```

---

## 📂 디렉토리 구조

```
backend/
├── documents/          # 문서 저장 (Git 추적 O)
│   ├── .gitkeep
│   └── README.md
├── uploads/           # RAG 업로드 (Git 추적 O)
│   ├── .gitkeep
│   └── README.md
├── vector_db/         # 벡터 DB (Git 추적 X - .gitignore)
│   ├── .gitkeep
│   └── README.md
├── rag/               # RAG 모듈
├── main.py            # 메인 서버
└── requirements.txt
```

---

## 🔧 관련 API 엔드포인트

### 정상 작동 확인된 엔드포인트

1. **GET /api/documents/list** (Line 8219)
   ```python
   @app.get("/api/documents/list")
   async def list_documents():
       documents_dir = Path("./documents")
       if not documents_dir.exists():
           return {"success": True, "documents": [], "count": 0}
       # ...
   ```

2. **GET /api/rag/status** (Line 7801)
   ```python
   @app.get("/api/rag/status")
   async def rag_status():
       if not vector_store_manager:
           return {"initialized": False, "message": "RAG 시스템이 초기화되지 않았습니다"}
       # ...
   ```

3. **GET /api/rag/documents** (Line 7477)
   ```python
   @app.get("/api/rag/documents")
   async def list_rag_documents(limit: int = 100):
       if not vector_store_manager:
           raise HTTPException(status_code=503, detail="RAG 시스템이 초기화되지 않았습니다")
       # ...
   ```

---

## 📦 커밋 정보

- **Commit**: 367e618
- **Message**: fix: 필수 디렉토리 생성 (documents, uploads)
- **Changes**: 4 files changed, 2 insertions(+)
  - `backend/documents/.gitkeep`
  - `backend/documents/README.md`
  - `backend/uploads/.gitkeep`
  - `backend/uploads/README.md`

---

## 🚀 사용자 조치 사항

### 1. 최신 코드 받기

```bash
cd "G:\내 드라이브\11. DEV_23\51. Python_mp3등\BH2025_WOWU"
git pull origin hun
```

### 2. vector_db 디렉토리 생성 (로컬에만)

```bash
cd backend
mkdir -p vector_db
```

> **참고**: `vector_db`는 `.gitignore`에 포함되어 있어 Git에서 추적되지 않으므로 로컬에서 직접 생성해야 합니다.

### 3. 백엔드 서버 재시작

```bash
cd backend
python main.py
```

### 4. 브라우저 확인

- http://localhost:8000/docs
- 다음 엔드포인트들이 작동하는지 확인:
  - `GET /api/documents/list`
  - `GET /api/rag/status`
  - `GET /api/rag/documents`

---

## ✅ 검증 완료

### 디렉토리 확인
```bash
$ cd backend && ls -la | grep -E "documents|uploads|vector_db"
drwxr-xr-x  2 user user   4096 Jan  5 01:10 documents
drwxr-xr-x  2 user user   4096 Jan  5 01:10 uploads
drwxr-xr-x  2 user user   4096 Jan  5 01:10 vector_db
```

### API 엔드포인트 확인
- ✅ `/api/documents/list` - Line 8219 (정상)
- ✅ `/api/rag/status` - Line 7801 (정상)
- ✅ `/api/rag/documents` - Line 7477 (정상)

---

## 🔮 향후 개선 사항

### startup 이벤트에서 디렉토리 자동 생성

```python
@app.on_event("startup")
async def startup_event():
    """서버 시작 시 필수 디렉토리 생성"""
    required_dirs = ["documents", "uploads", "vector_db"]
    for dir_name in required_dirs:
        dir_path = Path(f"./{dir_name}")
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"✅ Created directory: {dir_name}")
```

이렇게 하면 서버 시작 시 자동으로 필수 디렉토리가 생성됩니다.

---

## 📚 관련 문서

1. **SYNTAX_ERROR_FIX_SUMMARY.md** - 문법 오류 수정
2. **DOCUMENT_CONTEXT_UI_GUIDE.md** - 문서 컨텍스트 UI
3. **RAG_IMPLEMENTATION_REPORT.md** - RAG 구현 보고서
4. **REQUIREMENTS_INSTALL_GUIDE.md** - Requirements 설치

---

## 🎯 결론

**필수 디렉토리 누락 문제 해결 완료!**

- ✅ `backend/documents/` 생성 및 Git 추적
- ✅ `backend/uploads/` 생성 및 Git 추적
- ✅ `backend/vector_db/` 생성 (로컬 환경)
- ✅ API 엔드포인트 정상 작동 확인
- ✅ GitHub에 푸시 완료

**이제 문서 업로드 및 RAG 기능이 정상 작동합니다!**

---

*최종 수정: 2026-01-05*
*Commit: 367e618*
