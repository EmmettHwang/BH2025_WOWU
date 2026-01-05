# Cafe24 PM2 배포 가이드

## 📋 필수 요구사항

### Python 버전
- **최소 버전**: Python 3.9
- **권장 버전**: Python 3.9 ~ 3.11
- **테스트 완료**: Python 3.9.25

### Python 버전 확인
```bash
python3 --version
# 또는
python --version
```

**버전이 맞지 않으면 Cafe24 호스팅 관리자에게 문의**

---

## 📦 패키지 요구사항 검증

### requirements.txt 전체 목록

```txt
# FastAPI & Web (필수)
fastapi==0.104.1
uvicorn[standard]==0.24.0
python-multipart==0.0.6
starlette==0.27.0
pydantic==2.4.2
pydantic-core==2.10.1

# Database (필수)
pymysql==1.1.0
cryptography==41.0.7

# Data Processing (필수)
pandas==2.1.3
numpy==1.26.2
openpyxl==3.1.2

# PDF & Document (필수)
reportlab==4.0.7
PyPDF2==3.0.1
python-docx==1.1.0
Pillow==10.1.0

# AI & LLM (필수)
openai==1.3.7
anthropic==0.7.1
groq==0.4.1
google-generativeai==0.3.1

# RAG & Vector Store (필수 - 중요!)
langchain==0.1.0
langchain-community==0.0.10
sentence-transformers==2.3.1
huggingface-hub==0.20.3
faiss-cpu==1.7.4
transformers==4.35.2
torch==2.1.1

# HTTP & Networking (필수)
requests==2.31.0
httpx==0.25.2
urllib3==2.1.0

# Utilities (필수)
python-dotenv==1.0.0
aiofiles==23.2.1
```

### 패키지 크기 및 설치 시간 예상

| 카테고리 | 크기 | 설치 시간 |
|---------|------|----------|
| FastAPI & Web | ~50MB | 1-2분 |
| Database | ~20MB | 30초 |
| Data Processing | ~100MB | 2-3분 |
| PDF & Document | ~80MB | 2분 |
| AI & LLM | ~100MB | 2-3분 |
| **RAG & Vector Store** | **~3GB** | **10-15분** |
| HTTP & Networking | ~30MB | 1분 |
| Utilities | ~10MB | 30초 |
| **총합** | **~3.4GB** | **20-30분** |

⚠️ **주의**: RAG 시스템 패키지가 매우 큽니다!

---

## 🚀 PM2로 배포하기

### 1. PM2 설치 확인

```bash
pm2 --version
```

**설치되지 않았다면**:
```bash
npm install -g pm2
```

---

### 2. 프로젝트 배포

#### 2-1. Git Clone
```bash
cd ~
git clone https://github.com/EmmettHwang/BH2025_WOWU.git
cd BH2025_WOWU
git checkout hun
```

#### 2-2. Python 가상환경 생성
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 2-3. 패키지 설치
```bash
cd backend
pip install --upgrade pip
pip install -r requirements.txt
```

**설치 중 오류가 발생하면**:
```bash
# torch 먼저 설치 (CPU 버전)
pip install torch==2.1.1 --index-url https://download.pytorch.org/whl/cpu

# 나머지 설치
pip install -r requirements.txt
```

#### 2-4. 필수 디렉토리 생성
```bash
mkdir -p documents uploads vector_db logs
cd ..
mkdir -p logs
```

#### 2-5. 환경 변수 설정
```bash
cp backend/.env.example backend/.env
nano backend/.env
```

**필수 설정**:
```bash
# 데이터베이스
DB_HOST=your_mysql_host
DB_PORT=3306
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=BH2025

# API 키 (RAG 필수)
GROQ_API_KEY=your_groq_api_key
```

---

### 3. PM2로 서버 시작

#### 3-1. PM2 설정 확인
```bash
cat ecosystem.config.js
```

**현재 설정**:
```javascript
{
  name: 'bh2025-backend',
  script: 'uvicorn',
  args: 'main:app --host 0.0.0.0 --port 8000 --workers 4',
  interpreter: 'python3',
  cwd: './backend',
  ...
}
```

#### 3-2. 시작
```bash
pm2 start ecosystem.config.js
```

#### 3-3. 상태 확인
```bash
pm2 status
pm2 logs bh2025-backend
```

#### 3-4. 자동 시작 설정
```bash
pm2 startup
pm2 save
```

---

## 🔧 PM2 관리 명령어

### 기본 명령어
```bash
# 상태 확인
pm2 status

# 로그 보기 (실시간)
pm2 logs bh2025-backend

# 로그 보기 (정적)
pm2 logs bh2025-backend --nostream

# 재시작
pm2 restart bh2025-backend

# 중지
pm2 stop bh2025-backend

# 삭제
pm2 delete bh2025-backend

# 모든 프로세스 재시작
pm2 restart all

# 모든 프로세스 중지
pm2 stop all

# 모든 프로세스 삭제
pm2 delete all
```

### 모니터링
```bash
# 실시간 모니터링
pm2 monit

# 메모리 사용량 확인
pm2 list

# 상세 정보
pm2 show bh2025-backend

# 로그 파일 위치
pm2 logs bh2025-backend --lines 0
```

---

## 🐛 문제 해결

### 1. Python 버전 문제

**증상**: `Python 3.9 이상 필요`

**해결**:
```bash
# Python 버전 확인
python3 --version

# Cafe24에서 Python 버전 확인
ls /usr/bin/python*

# 특정 버전 사용
pm2 delete bh2025-backend
# ecosystem.config.js의 interpreter를 변경
# interpreter: '/usr/bin/python3.9'
pm2 start ecosystem.config.js
```

### 2. 가상환경 경로 문제

**증상**: `ModuleNotFoundError`

**해결**:
```bash
# ecosystem.config.js 수정
interpreter: '/home/your_username/BH2025_WOWU/venv/bin/python3'
```

### 3. 패키지 설치 실패

**증상**: `ERROR: Could not install packages`

**해결**:
```bash
# 가상환경 활성화 확인
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip setuptools wheel

# 개별 설치
pip install torch==2.1.1 --index-url https://download.pytorch.org/whl/cpu
pip install faiss-cpu==1.7.4
pip install sentence-transformers==2.3.1
pip install langchain==0.1.0

# 나머지 설치
pip install -r requirements.txt
```

### 4. 메모리 부족

**증상**: 서버가 자주 재시작됨

**해결**:
```javascript
// ecosystem.config.js 수정
max_memory_restart: '2G',  // 메모리 제한 증가
args: 'main:app --host 0.0.0.0 --port 8000 --workers 2',  // 워커 감소
```

### 5. Import 경로 오류

**증상**: `ModuleNotFoundError: No module named 'backend'`

**해결**: ✅ 이미 수정됨
```javascript
// ecosystem.config.js
args: 'main:app ...',  // backend.main:app ❌
cwd: './backend',      // ./ ❌
```

### 6. RAG 시스템 초기화 실패

**증상**: `RAG 시스템 초기화 실패`

**해결**:
```bash
# 필수 디렉토리 확인
cd ~/BH2025_WOWU/backend
ls -la | grep -E "documents|uploads|vector_db"

# 없으면 생성
mkdir -p documents uploads vector_db

# 권한 확인
chmod 755 documents uploads vector_db

# PM2 재시작
pm2 restart bh2025-backend
```

---

## 📊 서버 시작 확인

### 1. 시작 로그 확인

```bash
pm2 logs bh2025-backend --lines 100
```

**정상 시작 로그**:
```
============================================================
🚀 BH2025 WOWU 백엔드 서버 시작
============================================================

📋 등록된 API 엔드포인트:

📁 Documents API:
  {'DELETE'} /api/documents/{filename}
  {'GET'} /api/documents/download/{filename}
  {'GET'} /api/documents/list
  {'POST'} /api/documents/upload

🤖 RAG API:
  {'DELETE'} /api/rag/clear
  {'GET'} /api/rag/documents
  {'GET'} /api/rag/status
  ...

============================================================

[INFO] RAG 시스템 초기화 중...
✅ RAG 시스템 초기화 완료
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 2. HTTP 접속 테스트

```bash
# 로컬 테스트
curl http://localhost:8000/

# API 문서
curl http://localhost:8000/docs
```

브라우저: `http://your-domain.com:8000` 또는 `http://your-ip:8000`

---

## 🔄 코드 업데이트

### 업데이트 프로세스

```bash
cd ~/BH2025_WOWU

# 1. 최신 코드 받기
git pull origin hun

# 2. 가상환경 활성화
source venv/bin/activate

# 3. 패키지 업데이트
cd backend
pip install -r requirements.txt --upgrade

# 4. PM2 재시작
cd ..
pm2 restart bh2025-backend

# 5. 로그 확인
pm2 logs bh2025-backend --lines 50
```

---

## 📦 PM2 ecosystem.config.js 상세 설명

```javascript
module.exports = {
  apps: [
    {
      // 앱 이름 (pm2 list에 표시됨)
      name: 'bh2025-backend',
      
      // 실행할 스크립트 (uvicorn 명령어)
      script: 'uvicorn',
      
      // uvicorn 인자
      // ✅ main:app (backend.main:app ❌)
      args: 'main:app --host 0.0.0.0 --port 8000 --workers 4',
      
      // Python 인터프리터
      // 가상환경 사용 시: '/home/username/BH2025_WOWU/venv/bin/python3'
      interpreter: 'python3',
      
      // 작업 디렉토리
      // ✅ ./backend (아닌 ./ ❌)
      cwd: './backend',
      
      // 인스턴스 수 (보통 1)
      instances: 1,
      
      // 자동 재시작
      autorestart: true,
      
      // 파일 변경 감지 (운영: false)
      watch: false,
      
      // 메모리 제한 (초과 시 재시작)
      max_memory_restart: '1G',
      
      // 환경 변수
      env: {
        NODE_ENV: 'production',
        PORT: 8000,
        PYTHONPATH: './backend',
        // DB 정보는 .env 파일 권장
      },
      
      // 로그 파일
      error_file: './logs/backend-error.log',
      out_file: './logs/backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true,
      time: true
    }
  ]
};
```

---

## ✅ 배포 체크리스트

### 사전 준비
- [ ] Python 3.9+ 확인
- [ ] PM2 설치 확인
- [ ] SSH 접속 정보
- [ ] MySQL 데이터베이스 정보
- [ ] GROQ API 키

### 배포 과정
- [ ] Git clone
- [ ] 가상환경 생성
- [ ] 패키지 설치 (20-30분 소요)
- [ ] 필수 디렉토리 생성
- [ ] .env 파일 설정
- [ ] PM2로 시작
- [ ] 로그 확인
- [ ] 브라우저 접속 테스트

### 배포 후
- [ ] API 문서 접근 확인 (/docs)
- [ ] RAG 시스템 초기화 확인
- [ ] PM2 자동 시작 설정
- [ ] 백업 설정

---

## 🔍 성능 튜닝

### 워커 수 조정

```javascript
// ecosystem.config.js
args: 'main:app --host 0.0.0.0 --port 8000 --workers N',
```

**권장 워커 수**:
- 1GB 메모리: `--workers 1`
- 2GB 메모리: `--workers 2`
- 4GB 메모리: `--workers 4`
- 8GB 메모리: `--workers 6`

**공식**: `워커 수 = (CPU 코어 수 × 2) + 1` (최대 메모리 범위 내)

---

## 🔐 보안

### .env 파일 보호
```bash
chmod 600 backend/.env
```

### 로그 파일 권한
```bash
chmod 640 logs/*.log
```

### 민감 정보 제거
```bash
# ecosystem.config.js에서 DB 비밀번호 제거
# .env 파일로 이동
```

---

## 📚 관련 문서

- **일반 배포 가이드**: `CAFE24_DEPLOYMENT_GUIDE.md`
- **Requirements**: `backend/requirements.txt`
- **환경 변수**: `backend/.env.example`

---

*최종 수정: 2026-01-05*
