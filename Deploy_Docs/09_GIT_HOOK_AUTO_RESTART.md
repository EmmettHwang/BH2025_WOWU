# Git Hook을 이용한 서버 자동 재시작 설정

## 📖 개요

`git pull` 실행 시 변경된 파일을 자동으로 감지하여 PM2 서버를 재시작합니다.

---

## 🔧 설정 방법 (Windows)

### 방법 1: Git Bash 사용 (권장)

1. **Git Bash 열기**
   ```bash
   # 프로젝트 폴더로 이동
   cd "G:/내 드라이브/11. DEV_23/51. Python_mp3등/BH2025_WOWU"
   ```

2. **Hook 파일 복사**
   ```bash
   # post-merge hook 생성
   cp .git/hooks/post-merge-windows.sample .git/hooks/post-merge
   
   # 실행 권한 부여
   chmod +x .git/hooks/post-merge
   ```

3. **경로 수정 (필요시)**
   ```bash
   # 파일 편집
   nano .git/hooks/post-merge
   
   # 또는 VS Code로 열기
   code .git/hooks/post-merge
   ```
   
   ```bash
   # 이 부분을 본인의 프로젝트 경로로 수정
   PROJECT_DIR="G:/내 드라이브/11. DEV_23/51. Python_mp3등/BH2025_WOWU"
   ```

4. **테스트**
   ```bash
   git pull origin hun
   # 🔄 Git Pull 완료! 서버 자동 재시작 중...
   # 📦 Backend 파일 변경 감지
   # 🎨 Frontend 파일 변경 감지
   # 🔄 PM2 서버 재시작 중...
   # ✅ 서버 재시작 완료!
   ```

---

### 방법 2: Windows 배치 파일 사용

1. **배치 파일 설정**
   ```cmd
   # 프로젝트 폴더로 이동
   cd "G:\내 드라이브\11. DEV_23\51. Python_mp3등\BH2025_WOWU"
   
   # post-merge.bat 파일을 .git/hooks/ 폴더에 복사
   copy .git\hooks\post-merge.bat .git\hooks\post-merge
   ```

2. **경로 수정**
   ```cmd
   notepad .git\hooks\post-merge
   ```
   
   ```bat
   REM 이 부분을 본인의 프로젝트 경로로 수정
   cd /d "G:\내 드라이브\11. DEV_23\51. Python_mp3등\BH2025_WOWU"
   ```

3. **테스트**
   ```cmd
   git pull origin hun
   ```

---

### 방법 3: 수동 스크립트 실행

Git Hook이 작동하지 않을 경우, 수동으로 스크립트를 실행할 수 있습니다.

#### **auto-restart.bat** 생성

프로젝트 루트에 `auto-restart.bat` 파일 생성:

```bat
@echo off
echo 🔄 Git Pull 및 서버 재시작 스크립트

REM 프로젝트 폴더로 이동
cd /d "G:\내 드라이브\11. DEV_23\51. Python_mp3등\BH2025_WOWU"

echo 📥 최신 코드 가져오기...
git pull origin hun

echo 🔄 PM2 서버 재시작...
pm2 restart all

echo ✅ 완료!
pause
```

#### **사용 방법**

```cmd
# 더블클릭 또는 명령어 실행
auto-restart.bat
```

---

## 🚀 작동 원리

### Git Hook이란?

Git Hook은 Git 작업(commit, push, merge 등) 전후로 자동 실행되는 스크립트입니다.

### post-merge Hook

`git pull` 또는 `git merge` 실행 **후** 자동으로 실행됩니다.

```
git pull origin hun
  ↓
Git이 코드 병합
  ↓
.git/hooks/post-merge 자동 실행
  ↓
변경된 파일 확인
  ↓
backend/ 변경 → backend-server 재시작
frontend/ 변경 → frontend-server 재시작
  ↓
완료!
```

---

## 📋 Hook 스크립트 내용

### 기능

1. **변경 파일 감지**: `git diff-tree`로 변경된 파일 목록 확인
2. **Backend 감지**: `backend/` 폴더 변경 시 backend-server 재시작
3. **Frontend 감지**: `frontend/` 폴더 변경 시 frontend-server 재시작
4. **로그 출력**: 재시작 과정을 콘솔에 표시

### 코드 구조

```bash
#!/bin/bash

# 변경된 파일 목록
CHANGED_FILES=$(git diff-tree -r --name-only --no-commit-id ORIG_HEAD HEAD)

# backend 변경 확인
if echo "$CHANGED_FILES" | grep -q "^backend/"; then
    pm2 restart backend-server
fi

# frontend 변경 확인
if echo "$CHANGED_FILES" | grep -q "^frontend/"; then
    pm2 restart frontend-server
fi
```

---

## 🔍 문제 해결

### 1. Hook이 실행되지 않을 때

**원인**: 실행 권한 없음

**해결**:
```bash
chmod +x .git/hooks/post-merge
```

**Windows에서 확인**:
```cmd
# Git Bash에서 실행
ls -la .git/hooks/post-merge
# -rwxr-xr-x 표시 확인 (x = 실행 가능)
```

---

### 2. PM2 명령을 찾을 수 없을 때

**원인**: PATH 설정 문제 또는 Anaconda 환경 미활성화

**해결**:
```bash
# .git/hooks/post-merge 파일 수정
# 이 부분을 추가
source ~/anaconda3/etc/profile.d/conda.sh
conda activate bh2025
```

또는 PM2 전체 경로 사용:
```bash
/c/Users/사용자명/AppData/Roaming/npm/pm2 restart all
```

---

### 3. 경로 문제

**원인**: 프로젝트 경로가 잘못됨

**해결**:
```bash
# .git/hooks/post-merge에서 경로 확인
PROJECT_DIR="G:/내 드라이브/11. DEV_23/51. Python_mp3등/BH2025_WOWU"

# 본인의 실제 경로로 수정
```

---

### 4. Git Bash에서 한글 경로 문제

**원인**: Windows 한글 경로 인식 문제

**해결 1**: Git Bash에서 경로 변환
```bash
cd "/g/내 드라이브/11. DEV_23/51. Python_mp3등/BH2025_WOWU"
```

**해결 2**: 영문 경로 사용
```bash
# 심볼릭 링크 생성
ln -s "/g/내 드라이브/11. DEV_23/51. Python_mp3등/BH2025_WOWU" ~/bh2025
cd ~/bh2025
```

---

## ✅ 테스트 방법

### 1. Hook 수동 실행 테스트

```bash
cd "G:/내 드라이브/11. DEV_23/51. Python_mp3등/BH2025_WOWU"

# Hook 직접 실행
.git/hooks/post-merge

# 출력 확인
# 🔄 Git Pull 완료! 서버 자동 재시작 중...
# ✅ 서버 재시작 완료!
```

### 2. 실제 Git Pull 테스트

```bash
# 테스트 브랜치에서 pull
git pull origin hun

# 자동 재시작 메시지 확인
# 🔄 Git Pull 완료! 서버 자동 재시작 중...
# 📦 Backend 파일 변경 감지
# 🔄 PM2 서버 재시작 중...
# ✅ 서버 재시작 완료!
```

### 3. PM2 상태 확인

```bash
pm2 status

# 출력 예시
# ┌─────┬────────────────────┬─────────┬─────────┬──────────┐
# │ id  │ name               │ status  │ restart │ uptime   │
# ├─────┼────────────────────┼─────────┼─────────┼──────────┤
# │ 0   │ backend-server     │ online  │ 2       │ 10s      │ ← restart 횟수 증가!
# │ 1   │ frontend-server    │ online  │ 1       │ 10s      │
# └─────┴────────────────────┴─────────┴─────────┴──────────┘
```

---

## 💡 추가 팁

### 1. 로그 파일 생성

Hook 실행 기록을 파일로 저장:

```bash
# .git/hooks/post-merge 수정
#!/bin/bash
LOG_FILE="$HOME/git-hook.log"

echo "[$(date)] Git Pull 및 재시작 시작" >> "$LOG_FILE"

# ... (기존 코드)

echo "[$(date)] 완료" >> "$LOG_FILE"
```

### 2. 알림 추가 (Windows)

```bat
REM .git/hooks/post-merge.bat에 추가
echo 📢 서버 재시작 완료! > nul
msg * "서버 재시작이 완료되었습니다!"
```

### 3. 브라우저 자동 새로고침

```bash
# .git/hooks/post-merge에 추가
# Chrome 새로고침 (Windows)
# powershell -Command "(New-Object -ComObject WScript.Shell).SendKeys('{F5}')"
```

---

## 📚 참고 자료

- **Git Hooks 공식 문서**: https://git-scm.com/docs/githooks
- **PM2 공식 문서**: https://pm2.keymetrics.io/docs/usage/quick-start/
- **Git Hook 예제**: https://github.com/git/git/tree/master/templates/hooks

---

## 🎯 요약

### 자동화 완료! ✅

```bash
git pull origin hun
```

이제 위 명령어 하나로:
1. ✅ 최신 코드 가져오기
2. ✅ 변경 파일 자동 감지
3. ✅ Backend/Frontend 서버 자동 재시작
4. ✅ 완료!

**수동 재시작 불필요! 🎉**
