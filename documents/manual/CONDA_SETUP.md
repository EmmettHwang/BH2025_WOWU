# 🐍 Conda 환경으로 로컬 실행하기

## 🎯 빠른 시작

### 1️⃣ Conda 환경이 이미 있는 경우 (bh2025)

```bash
# 1. 프로젝트 폴더로 이동
cd "G:\내 드라이브\11. DEV_23\51. Python_mp3등\BH2025_WOWU"

# 2. Conda 환경 활성화
conda activate bh2025

# 3. Python 패키지 설치
cd backend
pip install -r requirements.txt
cd ..

# 4. 서버 실행
start-servers-conda.bat
```

### 2️⃣ Conda 환경이 없는 경우

```bash
# 1. 새 Conda 환경 생성
conda create -n bh2025 python=3.8

# 2. 환경 활성화
conda activate bh2025

# 3. 프로젝트 폴더로 이동
cd "G:\내 드라이브\11. DEV_23\51. Python_mp3등\BH2025_WOWU"

# 4. Python 패키지 설치
cd backend
pip install -r requirements.txt
cd ..

# 5. Node.js 패키지 설치
npm install
npm install -g pm2

# 6. 서버 실행
start-servers-conda.bat
```

---

## 📋 Conda 명령어

### 환경 관리
```bash
# 환경 목록 확인
conda env list

# 환경 활성화
conda activate bh2025

# 환경 비활성화
conda deactivate

# 환경 삭제
conda remove -n bh2025 --all
```

### 패키지 관리
```bash
# 설치된 패키지 확인
conda list
# 또는
pip list

# 패키지 설치
pip install 패키지명
# 또는
conda install 패키지명

# requirements.txt로 일괄 설치
pip install -r requirements.txt
```

---

## 🚀 서버 실행 방법

### 방법 A: Conda 전용 배치 파일 사용 (권장)

```bash
# 서버 시작
start-servers-conda.bat

# 서버 중지
stop-servers-conda.bat
```

### 방법 B: 수동 실행 (2개 터미널)

**터미널 1 - 백엔드:**
```bash
conda activate bh2025
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**터미널 2 - 프론트엔드:**
```bash
cd "G:\내 드라이브\11. DEV_23\51. Python_mp3등\BH2025_WOWU"
node frontend/proxy-server.cjs
```

---

## 🔧 PM2 명령어

### 서버 관리
```bash
pm2 status              # 상태 확인
pm2 logs                # 로그 보기
pm2 restart all         # 재시작
pm2 stop all            # 중지
pm2 delete all          # 제거
```

### 개별 서버 제어
```bash
pm2 restart frontend-server
pm2 restart backend-server
pm2 logs frontend-server
pm2 logs backend-server
```

---

## 🛠️ 문제 해결

### ❌ "conda를 찾을 수 없습니다"

**Anaconda Prompt 사용:**
1. 시작 메뉴에서 "Anaconda Prompt" 검색
2. Anaconda Prompt 실행
3. 프로젝트 폴더로 이동
4. 명령어 실행

### ❌ Conda 환경 활성화 실패

```bash
# Conda 초기화 (PowerShell)
conda init powershell

# Conda 초기화 (CMD)
conda init cmd.exe

# 터미널 재시작 필요
```

### ❌ 패키지 설치 오류

```bash
# pip 업그레이드
python -m pip install --upgrade pip

# 패키지 재설치
pip install -r requirements.txt --upgrade --force-reinstall
```

### ❌ PM2 명령어를 찾을 수 없음

```bash
# Node.js가 설치되어 있는지 확인
node --version
npm --version

# PM2 재설치
npm install -g pm2
```

---

## 📊 환경 설정 체크리스트

- [ ] Anaconda/Miniconda 설치 확인
- [ ] Conda 환경 생성 (`bh2025`)
- [ ] Conda 환경 활성화
- [ ] Python 패키지 설치 (`pip install -r requirements.txt`)
- [ ] Node.js 설치 확인
- [ ] npm 패키지 설치 (`npm install`)
- [ ] PM2 전역 설치 (`npm install -g pm2`)
- [ ] `start-servers-conda.bat` 실행
- [ ] 브라우저에서 `http://localhost:3000` 접속

---

## 🎉 성공 화면

**PM2 상태:**
```
┌─────┬───────────────────┬─────────┬─────────┐
│ id  │ name              │ status  │ cpu     │
├─────┼───────────────────┼─────────┼─────────┤
│ 0   │ frontend-server   │ online  │ 0%      │
│ 1   │ backend-server    │ online  │ 0%      │
└─────┴───────────────────┴─────────┴─────────┘
```

**브라우저:**
- Frontend: http://localhost:3000
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## 💡 추가 팁

### VS Code에서 Conda 환경 사용

1. `Ctrl + Shift + P` → "Python: Select Interpreter"
2. Conda 환경 `bh2025` 선택
3. 터미널에서 자동으로 활성화됨

### Jupyter Notebook에서 사용

```bash
conda activate bh2025
conda install ipykernel
python -m ipykernel install --user --name=bh2025
```

### 환경 복제 (백업)

```bash
# 환경 내보내기
conda env export > environment.yml

# 환경 불러오기
conda env create -f environment.yml
```

---

## 🔗 참고 문서

- Conda 공식 문서: https://docs.conda.io/
- PM2 문서: https://pm2.keymetrics.io/
- 프로젝트 README: `README.md`
- 일반 로컬 개발: `LOCAL_DEVELOPMENT.md`

---

## 📞 도움말

문제가 발생하면:
1. Conda 환경 확인: `conda info --envs`
2. 패키지 확인: `pip list`
3. PM2 상태 확인: `pm2 status`
4. PM2 로그 확인: `pm2 logs`
5. GitHub Issues: https://github.com/EmmettHwang/BH2025_WOWU/issues
