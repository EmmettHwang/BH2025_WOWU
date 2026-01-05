# 📦 Backend Requirements 설치 가이드

## 📋 개요

백엔드는 **2개의 requirements 파일**을 제공합니다:

1. **requirements.txt**: 전체 시스템 (FastAPI + RAG + DB + 모든 기능)
2. **requirements_rag.txt**: RAG 시스템만 (문서 검색 전용)

---

## 🚀 설치 방법

### 방법 1: 전체 시스템 설치 (권장)

```bash
# 1. 가상환경 생성 (선택사항)
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate

# 2. 전체 패키지 설치
cd /home/user/webapp/backend
pip install -r requirements.txt
```

### 방법 2: RAG만 설치

RAG 문서 검색 기능만 필요한 경우:

```bash
cd /home/user/webapp/backend
pip install -r requirements_rag.txt
```

---

## 📦 주요 패키지 설명

### 1. FastAPI & Web Framework (전체 설치만)

| 패키지 | 버전 | 용도 |
|--------|------|------|
| fastapi | 0.104.1 | 웹 프레임워크 |
| uvicorn | 0.24.0 | ASGI 서버 |
| python-multipart | 0.0.6 | 파일 업로드 |

### 2. Database (전체 설치만)

| 패키지 | 버전 | 용도 |
|--------|------|------|
| pymysql | 1.1.0 | MySQL 연결 |
| cryptography | 41.0.7 | 암호화 |

### 3. Data Processing

| 패키지 | 버전 | 용도 | 포함 파일 |
|--------|------|------|-----------|
| pandas | 2.1.3 | 데이터 처리 | 전체만 |
| numpy | 1.26.2 | 수치 연산 | 둘 다 |
| openpyxl | 3.1.2 | Excel 처리 | 전체만 |

### 4. PDF & Document Processing

| 패키지 | 버전 | 용도 | 포함 파일 |
|--------|------|------|-----------|
| reportlab | 4.0.7 | PDF 생성 | 전체만 |
| PyPDF2 | 3.0.1 | PDF 읽기 | 둘 다 |
| python-docx | 1.1.0 | DOCX 읽기 | 둘 다 |
| Pillow | 10.1.0 | 이미지 처리 | 전체만 |

### 5. AI & LLM

| 패키지 | 버전 | 용도 | 포함 파일 |
|--------|------|------|-----------|
| openai | 1.3.7 | OpenAI API | 둘 다 |
| anthropic | 0.7.1 | Claude API | 전체만 |
| groq | 0.4.1 | Groq API | 둘 다 |
| google-generativeai | 0.3.1 | Gemini API | 둘 다 |

### 6. RAG & Vector Store ⭐

| 패키지 | 버전 | 용도 | 포함 파일 |
|--------|------|------|-----------|
| sentence-transformers | 2.2.2 | 임베딩 생성 | 둘 다 |
| faiss-cpu | 1.7.4 | 벡터 검색 | 둘 다 |
| transformers | 4.35.2 | Hugging Face | 둘 다 |
| torch | 2.1.1 | PyTorch | 둘 다 |

### 7. HTTP & Networking

| 패키지 | 버전 | 용도 | 포함 파일 |
|--------|------|------|-----------|
| requests | 2.31.0 | HTTP 요청 | 전체만 |
| httpx | 0.25.2 | 비동기 HTTP | 둘 다 |
| urllib3 | 2.1.0 | URL 처리 | 전체만 |

### 8. Utilities

| 패키지 | 버전 | 용도 | 포함 파일 |
|--------|------|------|-----------|
| python-dotenv | 1.0.0 | 환경변수 | 전체만 |
| aiofiles | 23.2.1 | 비동기 파일 | 둘 다 |

---

## 🔍 버전 확인

설치 후 버전 확인:

```bash
pip list | grep -E "fastapi|sentence-transformers|faiss|pymysql"
```

예상 출력:
```
faiss-cpu          1.7.4
fastapi            0.104.1
pymysql            1.1.0
sentence-transformers  2.2.2
```

---

## 🐛 문제 해결

### 문제 1: faiss-cpu 설치 실패

**증상:**
```
ERROR: Could not find a version that satisfies the requirement faiss-cpu
```

**해결:**
```bash
# CPU 버전 설치 (권장)
pip install faiss-cpu==1.7.4

# 또는 최신 버전
pip install faiss-cpu

# GPU 버전 (CUDA 필요)
pip install faiss-gpu==1.7.4
```

### 문제 2: torch 설치 시간 오래 걸림

**증상:**
```
Downloading torch... (매우 느림)
```

**해결:**
```bash
# CPU 버전 (더 가벼움)
pip install torch==2.1.1 --index-url https://download.pytorch.org/whl/cpu

# 또는 미리 컴파일된 버전
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### 문제 3: sentence-transformers 모델 다운로드

**증상:**
처음 실행 시 모델 다운로드로 시간 소요

**해결:**
```python
# 미리 모델 다운로드
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')
```

### 문제 4: PyMySQL 연결 오류

**증상:**
```
pymysql.err.OperationalError: (2003, "Can't connect to MySQL server")
```

**해결:**
```bash
# 1. MySQL 서버 실행 확인
# 2. .env 파일 설정 확인
# 3. cryptography 설치
pip install cryptography==41.0.7
```

### 문제 5: Pillow/PIL 오류

**증상:**
```
ImportError: cannot import name 'Image' from 'PIL'
```

**해결:**
```bash
pip uninstall Pillow PIL
pip install Pillow==10.1.0
```

---

## 📊 패키지 크기 비교

| 항목 | requirements.txt | requirements_rag.txt |
|------|------------------|----------------------|
| 패키지 수 | ~30개 | ~12개 |
| 다운로드 크기 | ~2.5 GB | ~1.8 GB |
| 설치 시간 | ~15분 | ~10분 |
| 디스크 공간 | ~5 GB | ~3.5 GB |

---

## 🔄 업데이트

### 전체 업데이트

```bash
pip install -r requirements.txt --upgrade
```

### 특정 패키지만 업데이트

```bash
# FastAPI 업데이트
pip install fastapi --upgrade

# RAG 패키지 업데이트
pip install sentence-transformers faiss-cpu --upgrade
```

### 현재 패키지 목록 저장

```bash
# 현재 설치된 패키지 목록
pip freeze > requirements_installed.txt
```

---

## 🎯 사용 케이스별 설치 가이드

### 케이스 1: 로컬 개발 (Full Stack)

```bash
pip install -r requirements.txt
```

**포함:**
- FastAPI 웹 서버
- MySQL 데이터베이스 연결
- RAG 문서 검색
- PDF/Excel 처리
- 모든 AI 모델 API

### 케이스 2: RAG 서버만 (Micro Service)

```bash
pip install -r requirements_rag.txt
```

**포함:**
- RAG 문서 검색 기능만
- FAISS 벡터 DB
- 문서 파싱 (PDF, DOCX)
- AI 모델 API (OpenAI, Groq, Gemini)

### 케이스 3: 프로덕션 배포

```bash
# 1. 기본 설치
pip install -r requirements.txt

# 2. 프로덕션 전용 패키지 추가
pip install gunicorn supervisor

# 3. 로그 관리
pip install python-json-logger
```

---

## 🔐 보안 권장사항

### 1. 패키지 취약점 검사

```bash
pip install safety
safety check -r requirements.txt
```

### 2. 최신 보안 패치 적용

```bash
pip list --outdated
pip install <package> --upgrade
```

### 3. 신뢰할 수 있는 소스에서만 설치

```bash
pip install --trusted-host pypi.org --trusted-host files.pythonhosted.org -r requirements.txt
```

---

## 📝 개발 환경 권장사항

### Python 버전

- **권장**: Python 3.10 또는 3.11
- **최소**: Python 3.8
- **지원 안 함**: Python 3.7 이하

### 가상환경

```bash
# venv (기본)
python -m venv venv

# conda
conda create -n biohealth python=3.10
conda activate biohealth

# poetry
poetry install
```

### IDE 설정

**.vscode/settings.json:**
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": false,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black"
}
```

---

## 🎓 참고 자료

- [FastAPI 공식 문서](https://fastapi.tiangolo.com/)
- [Sentence Transformers](https://www.sbert.net/)
- [FAISS](https://github.com/facebookresearch/faiss)
- [PyMySQL](https://pymysql.readthedocs.io/)
- [ReportLab](https://www.reportlab.com/documentation/)

---

## ✅ 설치 완료 체크리스트

- [ ] Python 3.8+ 설치 확인
- [ ] 가상환경 생성 및 활성화
- [ ] requirements.txt 설치 완료
- [ ] MySQL 서버 실행 (전체 설치 시)
- [ ] .env 파일 설정 (API 키, DB 정보)
- [ ] 테스트 실행: `python main.py`
- [ ] RAG 시스템 초기화 확인
- [ ] 브라우저에서 접속 테스트

---

**작성일**: 2025-01-05  
**버전**: v2.0.220  
**작성자**: AI 개발팀
