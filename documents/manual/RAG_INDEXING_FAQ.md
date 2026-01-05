# RAG 인덱싱 FAQ

## ❓ RAG 인덱싱은 매번 모든 문서를 다시 처리해야 하나요?

### 답변: **아니요! 절대 아닙니다!** ✅

RAG 인덱싱은 **새로 추가된 문서만** 처리합니다. 기존 문서는 이미 벡터 DB에 저장되어 있으므로 **다시 처리하지 않습니다**.

---

## 🗄️ 벡터 DB 저장 방식

### 파일 저장 위치
- **Linux**: `./simple_vector_db/`
- **Windows**: `%TEMP%/bh2025_vector_db/`

### 저장되는 파일
1. **`biohealth_docs.index`**: FAISS 인덱스 파일
2. **`biohealth_docs.pkl`**: 문서 내용 및 메타데이터 (Python pickle)

### 저장 시점
- ✅ **문서 추가 시**: `_save_index()` 자동 호출
- ✅ **서버 시작 시**: `_load_index()` 자동 로드

---

## 🔄 서버 재시작 시 동작

### 1. 서버 시작
```python
# backend/rag/simple_vector_store.py 라인 64
self._load_index()  # 저장된 인덱스 자동 로드
```

### 2. 인덱스 로드
```python
# 라인 179-190
if os.path.exists(index_path) and os.path.exists(metadata_path):
    self.index = faiss.read_index(index_path)
    with open(metadata_path, 'rb') as f:
        data = pickle.load(f)
        self.documents = data['documents']  # 기존 문서 복원
        self.metadatas = data['metadatas']  # 기존 메타데이터 복원
```

### 3. 결과
- ✅ 기존 158개 문서 **자동 복원**
- ✅ 재인덱싱 **불필요**
- ✅ 서버 시작 **10초 이내**

---

## 📝 새 문서 추가 시 동작

### 1. 사용자가 PDF 업로드
```
파일 선택 → "RAG 인덱싱?" → "예" 선택
```

### 2. 백엔드 처리
```python
# backend/main.py 라인 8411-8447
# 1. 문서 파싱 (PDF → 텍스트)
documents = document_loader.load_document(str(file_path), metadata)

# 2. 청킹 (텍스트 → 청크)
texts = [doc.page_content for doc in documents]

# 3. 임베딩 생성 (청크 → 벡터)
embeddings = embedding_model.encode(texts)

# 4. 벡터 DB에 추가 (새 문서만!)
doc_ids = vector_store_manager.add_documents(texts, metadatas)

# 5. 자동 저장
self._save_index()  # 파일로 저장
```

### 3. 결과
- ✅ **새 문서 1개**만 처리
- ✅ **기존 158개** 문서는 그대로 유지
- ✅ 총 **159개** 문서 (158 + 1)

---

## 🎬 애니메이션이 반복되는 이유 (해결됨!)

### ❌ 문제 (이전)
```javascript
// frontend/app.js 라인 20046
currentStage = (currentStage + 1) % stages.length;
// % stages.length 때문에 무한 반복!
// 0 → 1 → 2 → 3 → 0 → 1 → 2 → 3 → ...
```

**사용자 오해**:
- "Parsing → Chunking → Embedding → Indexing이 계속 반복된다!"
- "모든 문서를 다시 처리하는 건가?"

### ✅ 해결 (현재)
```javascript
// 수정된 코드
if (currentStage >= stages.length) {
    return;  // 4단계 완료 후 중지
}
currentStage++;  // 0 → 1 → 2 → 3 → 중지
```

**개선 사항**:
- ✅ **4단계만 실행** (Parsing → Chunking → Embedding → Indexing)
- ✅ 마지막 단계(Indexing)에서 **중지**
- ✅ 백엔드 응답 대기 중 **Indexing 상태 유지**

---

## 📊 성능 비교

| 항목 | 처음 시작 | 서버 재시작 | 새 문서 추가 |
|------|----------|------------|--------------|
| 문서 개수 | 0개 | 158개 (복원) | 159개 (+1) |
| 처리 시간 | - | ~10초 | 1~5분 |
| 인덱싱 | - | 불필요 | 1개만 처리 |
| 벡터 생성 | - | 불필요 | 1개만 생성 |

---

## 🔍 확인 방법

### 1. 벡터 DB 파일 확인
```bash
# Linux
ls -lh ./simple_vector_db/
# biohealth_docs.index (FAISS 인덱스)
# biohealth_docs.pkl (문서 + 메타데이터)

# Windows
dir %TEMP%\bh2025_vector_db\
```

### 2. 문서 개수 확인
```bash
# PM2 로그 확인
pm2 logs bh2025-backend --lines 50 --nostream | grep "문서 수"

# 출력 예시:
# [OK] 벡터 스토어 초기화 완료 (문서 수: 158)
# [DOC] 저장된 문서 수: 158
```

### 3. API로 확인
```bash
curl http://localhost:8000/api/rag/status

# 응답 예시:
{
  "initialized": true,
  "document_count": 158,
  "embedding_model": "jhgan/ko-sroberta-multitask",
  "collection_name": "biohealth_docs",
  "vector_db": "FAISS",
  "status": "정상"
}
```

---

## 💡 주요 포인트

### ✅ DO (해야 할 것)
- 새 문서만 RAG 인덱싱
- 서버 재시작 시 자동 로드 확인
- 벡터 DB 파일 백업 (`.index`, `.pkl`)

### ❌ DON'T (하지 말아야 할 것)
- 모든 문서를 매번 재인덱싱
- 벡터 DB 파일 삭제 (백업 없이)
- 서버 재시작 시 수동 로드

---

## 🚨 트러블슈팅

### 문제 1: 서버 재시작 시 문서 수가 0
**원인**: 벡터 DB 파일이 삭제되었거나 경로가 변경됨

**해결**:
```bash
# 파일 확인
ls -lh ./simple_vector_db/

# 없으면 백업에서 복원
cp backup/biohealth_docs.* ./simple_vector_db/

# 백엔드 재시작
pm2 restart bh2025-backend
```

### 문제 2: 새 문서 추가 시 504 에러
**원인**: RAG 처리가 오래 걸림 (Nginx 타임아웃)

**해결**:
```nginx
# /etc/nginx/sites-enabled/kdt2025
location /api/ {
    proxy_read_timeout 300s;
    proxy_connect_timeout 300s;
    proxy_send_timeout 300s;
}
```

### 문제 3: 애니메이션이 무한 반복
**원인**: `currentStage = (currentStage + 1) % stages.length`

**해결**: 이미 수정됨! (커밋 `629b891`)

---

## 📚 관련 파일

- **백엔드**:
  - `backend/rag/simple_vector_store.py` (벡터 DB 관리)
  - `backend/rag/vector_store.py` (래퍼)
  - `backend/main.py` (API 엔드포인트)

- **프론트엔드**:
  - `frontend/app.js` (RAG 처리 로직)

- **문서**:
  - `documents/manual/RAG_504_TIMEOUT_FIX.md`
  - `documents/manual/NGINX_502_MAINTENANCE_PAGE.md`

---

## 🎉 결론

**RAG 인덱싱은 새 문서만 처리합니다!**

- ✅ 벡터 DB는 **파일로 저장**
- ✅ 서버 재시작 시 **자동 복원**
- ✅ 새 문서만 **증분 추가**
- ✅ 기존 문서는 **재처리 불필요**

**애니메이션 개선 완료!**

- ✅ 4단계만 실행 (무한 반복 제거)
- ✅ 처리 중인 파일 이름 표시
- ✅ AI 학습 소요 시간 안내
