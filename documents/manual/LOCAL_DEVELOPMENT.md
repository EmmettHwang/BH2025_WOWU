# 로컬 개발 환경 설정 가이드

## 🚀 빠른 시작

### 1️⃣ 사전 요구사항

- **Node.js** 16+ 설치
- **Python** 3.8+ 설치
- **Git** 설치

### 2️⃣ 초기 설정

```bash
# 1. 저장소 클론
git clone https://github.com/EmmettHwang/BH2025_WOWU.git
cd BH2025_WOWU

# 2. Node.js 패키지 설치
npm install

# 3. PM2 설치 (전역)
npm install -g pm2

# 4. Python 가상환경 설정
cd backend
python -m venv venv

# Windows:
venv\Scripts\activate
# Mac/Linux:
source venv/bin/activate

# 5. Python 패키지 설치
pip install -r requirements.txt
```

### 3️⃣ 서버 실행

#### 방법 A: PM2 사용 (추천) ⭐

**Windows (배치 파일):**
```bash
# 프로젝트 루트에서
start-servers.bat
```

**Windows (PowerShell):**
```powershell
# 프로젝트 루트에서
.\start-servers.ps1
```

**Mac/Linux:**
```bash
# 프로젝트 루트에서
pm2 start ecosystem.config.cjs
pm2 status
```

#### 방법 B: 수동 실행 (2개 터미널 필요)

**터미널 1 - 백엔드:**
```bash
cd backend
venv\Scripts\activate  # Windows
# 또는
source venv/bin/activate  # Mac/Linux

python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**터미널 2 - 프론트엔드:**
```bash
node frontend/proxy-server.cjs
```

### 4️⃣ 접속

- **프론트엔드**: http://localhost:3000
- **백엔드 API**: http://localhost:8000
- **API 문서**: http://localhost:8000/docs

---

## 📊 PM2 명령어

### 서버 관리
```bash
pm2 start ecosystem.config.cjs    # 서버 시작
pm2 restart all                    # 모든 서버 재시작
pm2 stop all                       # 모든 서버 중지
pm2 delete all                     # 모든 서버 제거
```

### 상태 확인
```bash
pm2 status                         # 서버 상태 확인
pm2 list                           # 서버 목록
pm2 monit                          # 실시간 모니터링
```

### 로그 확인
```bash
pm2 logs                           # 모든 로그
pm2 logs frontend-server           # 프론트엔드만
pm2 logs backend-server            # 백엔드만
pm2 logs --nostream                # 스크롤 없이 보기
pm2 logs --lines 100               # 최근 100줄
```

### 개별 서버 제어
```bash
pm2 restart frontend-server        # 프론트엔드만 재시작
pm2 restart backend-server         # 백엔드만 재시작
pm2 stop frontend-server           # 프론트엔드만 중지
pm2 stop backend-server            # 백엔드만 중지
```

---

## 🛠️ 문제 해결

### 포트가 이미 사용 중

**Windows:**
```bash
# 포트 8000 확인
netstat -ano | findstr :8000
# PID로 종료
taskkill /PID [PID번호] /F

# 포트 3000 확인
netstat -ano | findstr :3000
taskkill /PID [PID번호] /F
```

**Mac/Linux:**
```bash
# 포트 8000 확인 및 종료
lsof -ti:8000 | xargs kill -9

# 포트 3000 확인 및 종료
lsof -ti:3000 | xargs kill -9
```

### PM2가 서버를 시작하지 못함

```bash
# PM2 완전 초기화
pm2 kill
pm2 resurrect

# 다시 시작
pm2 start ecosystem.config.cjs
```

### Python 가상환경 문제

```bash
# 가상환경 재생성
cd backend
rm -rf venv  # 또는 Windows: rmdir /s venv
python -m venv venv
venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

---

## 💡 개발 팁

### 코드 변경 시

- **프론트엔드**: 파일 변경 시 브라우저 새로고침 (`F5`)
- **백엔드**: `--reload` 옵션으로 자동 재시작됨

### 데이터베이스 연결

`.env` 파일 없이도 작동 (기본값 사용)  
커스터마이징하려면 `backend/.env` 파일 생성

### Git 작업

```bash
# 변경사항 확인
git status

# 커밋
git add .
git commit -m "feat: 새로운 기능"

# 푸시
git push origin main
```

---

## 🔧 고급 설정

### PM2 시작 프로그램 등록 (Windows)

1. `Win + R` → `shell:startup` 입력
2. `start-servers.bat` 바로가기 추가

### PM2 자동 시작 (Mac/Linux)

```bash
pm2 startup
pm2 save
```

---

## 📞 지원

문제가 발생하면:
1. PM2 로그 확인: `pm2 logs`
2. GitHub Issues: https://github.com/EmmettHwang/BH2025_WOWU/issues
