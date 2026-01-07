# RAG 문서 폴더 분리 구현 요약

## 📋 변경 사항 개요

### 문제점
- **이전**: 모든 문서(일반 문서 + RAG 문서)가 `documents/` 폴더에 혼재
- **불편함**: RAG 인덱싱된 문서와 일반 문서를 구분하기 어려움

### 해결 방법
- **현재**: RAG 인덱싱 문서는 `rag_documents/` 폴더에, 일반 문서는 `documents/` 폴더에 분리 저장
- **장점**: 
  - 파일 관리가 명확해짐
  - RAG 문서와 일반 문서를 쉽게 구분 가능
  - UI에서 폴더별 뱃지 표시

> ⚠️ **중요**: `backend/rag_documents/` 폴더는 RAG 시스템의 Python 모듈이 있는 폴더이므로, RAG 문서는 `backend/rag_documents/` 폴더에 저장됩니다.

---

## 🗂️ 폴더 구조

### Backend 폴더 구조
```
backend/
├── documents/          # 일반 문서 저장
│   ├── README.md
│   └── *.pdf, *.docx, *.txt, ...
├── rag_documents/     # RAG 인덱싱된 문서 저장 (신규) ✨
│   ├── README.md
│   └── *.pdf, *.docx, *.txt, ...
├── rag_documents/               # RAG 시스템 모듈 (Python 코드) ⚠️
│   ├── __init__.py
│   ├── document_loader.py
│   ├── vector_store.py
│   └── ...
├── uploads/           # 임시 업로드 파일
└── vector_db/         # 벡터 데이터베이스
```

### 파일 저장 규칙
| 업로드 타입 | 카테고리 | 저장 폴더 | 설명 |
|------------|---------|----------|------|
| RAG 인덱싱 선택 | `rag-indexed` 또는 `rag` | `./rag_documents/` | RAG 시스템에서 학습할 문서 |
| 일반 업로드 | `general` 또는 기타 | `./documents/` | 참고 자료용 일반 문서 |

---

## 🔧 Backend API 수정 내용

### 1. POST /api/documents/upload
**변경**: 카테고리에 따라 저장 폴더 자동 결정

```python
# 카테고리에 따라 저장 폴더 결정
if category == "rag-indexed" or category == "rag_documents":
    # RAG 문서는 rag 폴더에 저장
    documents_dir = Path("./rag")
else:
    # 일반 문서는 documents 폴더에 저장
    documents_dir = Path("./documents")

documents_dir.mkdir(exist_ok=True)
```

**사용 예시**:
```javascript
// RAG 문서 업로드
formData.append('file', file);
formData.append('category', 'rag-indexed');  // rag 폴더에 저장

// 일반 문서 업로드
formData.append('file', file);
formData.append('category', 'general');  // documents 폴더에 저장
```

---

### 2. GET /api/documents/list
**변경**: 두 폴더 모두에서 파일 조회 + 폴더 정보 추가

```python
@app.get("/api/documents/list")
async def list_documents():
    documents = []
    
    # documents 폴더와 rag 폴더 모두에서 파일 조회
    for folder_name in ["documents", "rag_documents"]:
        folder_path = Path(f"./{folder_name}")
        
        if folder_path.exists():
            for file_path in folder_path.iterdir():
                # ...
                documents.append({
                    "filename": file_path.name,
                    "file_size_mb": ...,
                    "modified_at": ...,
                    "extension": ...,
                    "folder": folder_name  # ✅ 폴더 정보 추가
                })
```

**응답 예시**:
```json
{
  "success": true,
  "documents": [
    {
      "filename": "20250105_140530_guide.pdf",
      "file_size_mb": 2.45,
      "modified_at": "2025-01-05T14:05:30",
      "extension": ".pdf",
      "folder": "rag_documents"  // ✅ RAG 폴더
    },
    {
      "filename": "20250105_141020_report.docx",
      "file_size_mb": 1.23,
      "modified_at": "2025-01-05T14:10:20",
      "extension": ".docx",
      "folder": "documents"  // ✅ 일반 폴더
    }
  ],
  "count": 2
}
```

---

### 3. DELETE /api/documents/{filename}
**변경**: 두 폴더 모두에서 파일 검색 후 삭제

```python
@app.delete("/api/documents/{filename}")
async def delete_document(filename: str):
    # documents와 rag 폴더 모두에서 파일 찾기
    file_path = None
    for folder in ["documents", "rag_documents"]:
        test_path = Path(f"./{folder}") / filename
        if test_path.exists():
            file_path = test_path
            break
    
    if not file_path:
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
    
    file_path.unlink()  # 파일 삭제
```

---

### 4. GET /api/documents/download/{filename}
**변경**: 두 폴더 모두에서 파일 검색 후 다운로드

```python
@app.get("/api/documents/download/{filename}")
async def download_document(filename: str):
    # documents와 rag 폴더 모두에서 파일 찾기
    file_path = None
    for folder in ["documents", "rag_documents"]:
        test_path = Path(f"./{folder}") / filename
        if test_path.exists():
            file_path = test_path
            break
    
    if not file_path:
        raise HTTPException(status_code=404, detail="파일을 찾을 수 없습니다")
    
    return FileResponse(path=str(file_path), filename=filename)
```

---

### 5. POST /api/rag_documents/index-document
**변경**: rag 폴더 우선 검색

```python
@app.post("/api/rag_documents/index-document")
async def index_document_to_rag(request: Request):
    # rag 폴더와 documents 폴더에서 파일 찾기 (rag 우선)
    file_path = None
    for folder in ["rag_documents", "documents"]:
        test_path = Path(f"./{folder}") / filename
        if test_path.exists():
            file_path = test_path
            break
    
    if not file_path:
        raise HTTPException(status_code=404, detail=f"파일을 찾을 수 없습니다: {filename}")
    
    # RAG 인덱싱 진행...
```

---

## 🎨 Frontend UI 개선

### 문서 목록에 폴더 뱃지 표시

**수정 전**:
```
📄 document.pdf
   [인덱싱됨] 2.5 MB · 2025-01-05
```

**수정 후**:
```
📄 document.pdf [RAG] [인덱싱됨]
   2.5 MB · 2025-01-05
```

### 구현 코드
```javascript
listDiv.innerHTML = documents.map(doc => {
    const isIndexed = ragDocNames.includes(doc.filename);
    
    // ✅ RAG 폴더 문서는 보라색 뱃지 표시
    const folderBadge = doc.folder === 'rag' 
        ? '<span class="bg-purple-100 text-purple-700 text-xs px-2 py-1 rounded-full font-semibold ml-2">
             <i class="fas fa-brain mr-1"></i>RAG
           </span>' 
        : '';
    
    // ✅ RAG 폴더 문서는 아이콘 색상도 보라색으로
    const iconColor = doc.folder === 'rag_documents' ? 'text-purple-500' : 'text-blue-500';
    
    return `
        <div class="bg-white rounded-lg p-4 border">
            <i class="fas fa-file-${getFileIcon(doc.extension)} text-3xl ${iconColor}"></i>
            <h4>${doc.filename}</h4>
            ${folderBadge}
            ${isIndexed ? '✅ 인덱싱됨' : '⭕ 미인덱싱'}
        </div>
    `;
}).join('');
```

### UI 표시 예시

#### RAG 문서
```
🟣 20250105_140530_guide.pdf [RAG] [✅ 인덱싱됨]
   2.45 MB · 2025-01-05 14:05:30
   [질문하기] [다운로드] [삭제]
```

#### 일반 문서
```
🔵 20250105_141020_report.docx [⭕ 미인덱싱]
   1.23 MB · 2025-01-05 14:10:20
   [질문하기] [다운로드] [삭제]
```

---

## 📝 사용 흐름

### 1. RAG 문서 업로드 (rag 폴더에 저장)
```
1. 사용자가 파일 선택
2. "RAG 시스템에 인덱싱하시겠습니까?" 모달 표시
3. "예" 클릭
   → category: 'rag-indexed'로 업로드
   → backend/rag_documents/ 폴더에 저장
4. 4단계 RAG 애니메이션 표시
5. 문서 목록에 [RAG] 뱃지와 함께 표시
```

### 2. 일반 문서 업로드 (documents 폴더에 저장)
```
1. 사용자가 파일 선택
2. "RAG 시스템에 인덱싱하시겠습니까?" 모달 표시
3. "아니오" 클릭
   → category: 'general'로 업로드
   → backend/documents/ 폴더에 저장
4. 즉시 업로드 완료
5. 문서 목록에 일반 문서로 표시
```

### 3. 문서 조회 및 관리
```
- GET /api/documents/list
  → documents/ 와 rag_documents/ 폴더 모두에서 조회
  → folder 필드로 구분

- DELETE /api/documents/{filename}
  → 두 폴더 모두에서 검색 후 삭제

- GET /api/documents/download/{filename}
  → 두 폴더 모두에서 검색 후 다운로드
```

---

## ✅ 변경 파일 목록

### Backend
1. ✅ `backend/main.py` - API 로직 수정
   - POST /api/documents/upload: 폴더 분리 로직 추가
   - GET /api/documents/list: 두 폴더 모두 조회
   - DELETE /api/documents/{filename}: 두 폴더에서 검색
   - GET /api/documents/download/{filename}: 두 폴더에서 검색
   - POST /api/rag_documents/index-document: rag 폴더 우선 검색

2. ✅ `backend/rag_documents/README.md` - 신규 폴더 설명

### Frontend
1. ✅ `frontend/app.js` - UI 표시 로직 수정
   - loadDocuments(): folder 필드 활용
   - RAG 문서에 보라색 뱃지 표시
   - RAG 문서 아이콘 색상 보라색 변경

2. ✅ `frontend/index.html` - 캐시 버전 업데이트
   - v=2.0.250 → v=2.0.270

---

## 🚀 배포 방법

### 로컬 테스트
```bash
# 1. 최신 코드 받기
cd "G:\내 드라이브\11. DEV_23\51. Python_mp3등\BH2025_WOWU"
git pull origin hun

# 2. Backend rag 폴더 생성 (자동으로 생성되지만 확인)
cd backend
mkdir -p rag

# 3. 서버 재시작
python main.py

# 4. 브라우저 강제 새로고침
# Windows/Linux: Ctrl+Shift+R
# Mac: Cmd+Shift+R

# 5. 테스트
http://localhost:8000 접속
→ 문서 관리 페이지
→ 파일 업로드 (RAG 선택 / 일반 선택)
→ 문서 목록에서 [RAG] 뱃지 확인
```

### Cafe24 서버 배포
```bash
# SSH 접속
ssh -p [포트] [사용자]@[호스트]

# 프로젝트 디렉토리로 이동
cd ~/BH2025_WOWU

# 최신 코드 받기
git pull origin hun

# rag 폴더 확인 및 생성
cd backend
mkdir -p rag
cd ..

# PM2 재시작
pm2 restart all

# 로그 확인
pm2 logs bh2025-backend --lines 50
```

---

## 🧪 테스트 시나리오

### 시나리오 1: RAG 문서 업로드
```
1. 파일 선택 (예: guide.pdf)
2. "RAG 인덱싱?" → "예" 클릭
3. 4단계 애니메이션 확인
4. 문서 목록 확인
   ✅ [RAG] 뱃지가 보임
   ✅ 아이콘이 보라색
   ✅ [인덱싱됨] 상태
5. 서버 파일 확인: backend/rag_documents/20250105_xxxxxx_guide.pdf
```

### 시나리오 2: 일반 문서 업로드
```
1. 파일 선택 (예: report.docx)
2. "RAG 인덱싱?" → "아니오" 클릭
3. 즉시 업로드 완료
4. 문서 목록 확인
   ✅ [RAG] 뱃지 없음
   ✅ 아이콘이 파란색
   ✅ [미인덱싱] 상태
5. 서버 파일 확인: backend/documents/20250105_xxxxxx_report.docx
```

### 시나리오 3: 문서 삭제
```
1. RAG 문서 삭제 → backend/rag_documents/ 에서 삭제 확인
2. 일반 문서 삭제 → backend/documents/ 에서 삭제 확인
```

### 시나리오 4: 문서 다운로드
```
1. RAG 문서 다운로드 → backend/rag_documents/ 에서 다운로드
2. 일반 문서 다운로드 → backend/documents/ 에서 다운로드
```

---

## 📊 예상 효과

### 파일 관리 개선
| 항목 | 수정 전 | 수정 후 | 개선 |
|------|---------|---------|------|
| **폴더 구분** | ❌ 모두 documents/ | ✅ documents/, rag_documents/ 분리 | 🎯 명확함 |
| **RAG 문서 식별** | ⚠️ 인덱싱 상태만 표시 | ✅ [RAG] 뱃지 + 보라색 | 🎯 직관적 |
| **파일 찾기** | ⚠️ 모든 파일 혼재 | ✅ 폴더별 분리 | 🎯 편리함 |
| **백업/관리** | ⚠️ 구분 어려움 | ✅ 폴더별 백업 가능 | 🎯 효율적 |

### 사용자 경험 개선
- ✅ RAG 문서와 일반 문서를 한눈에 구분 가능
- ✅ 보라색 뱃지와 아이콘으로 시각적 차별화
- ✅ 파일 관리가 더 직관적이고 명확해짐

---

## 🔗 관련 정보

### 커밋 정보
- **커밋 해시**: ff9c10c
- **브랜치**: hun
- **커밋 메시지**: "feat: RAG 문서를 별도 폴더(rag_documents/)에 저장 및 UI 표시 개선"
- **변경 통계**: 4 files changed, 60 insertions(+), 37 deletions(-)

### GitHub
- **커밋 URL**: https://github.com/EmmettHwang/BH2025_WOWU/commit/ff9c10c
- **PR**: https://github.com/EmmettHwang/BH2025_WOWU/compare/main...hun

### 관련 문서
- [RAG 애니메이션 수정](./RAG_ANIMATION_FIX_SUMMARY.md)
- [RAG 구현 리포트](./RAG_IMPLEMENTATION_REPORT.md)
- [문서 컨텍스트 UI 가이드](./DOCUMENT_CONTEXT_UI_GUIDE.md)

---

## 🎯 주요 변경 요약

### Backend
1. ✅ RAG 문서는 `backend/rag_documents/` 폴더에 저장
2. ✅ 일반 문서는 `backend/documents/` 폴더에 저장
3. ✅ API가 두 폴더 모두 지원 (조회/삭제/다운로드)
4. ✅ 업로드 시 category 파라미터로 자동 폴더 결정

### Frontend
1. ✅ RAG 문서에 보라색 [RAG] 뱃지 표시
2. ✅ RAG 문서 아이콘 색상 보라색으로 변경
3. ✅ 문서 목록에서 폴더 정보 시각적 표시
4. ✅ 캐시 버전 업데이트 (v=2.0.270)

---

**작성일**: 2026-01-05  
**작성자**: Claude (Genspark AI Developer)  
**버전**: 1.0  
**상태**: ✅ 완료 및 배포 준비
 ✅ 완료 및 배포 준비
*: Claude (Genspark AI Developer)  
**버전**: 1.0  
**상태**: ✅ 완료 및 배포 준비
