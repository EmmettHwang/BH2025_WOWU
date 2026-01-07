# 🔧 PM2 프로세스 관리 가이드

PM2를 사용한 Node.js 및 Python 애플리케이션 프로세스 관리입니다.

---

## 📋 목차

1. [PM2 소개](#pm2-소개)
2. [설치](#설치)
3. [기본 사용법](#기본-사용법)
4. [ecosystem.config.cjs](#ecosystemconfigcjs)
5. [프로세스 관리](#프로세스-관리)
6. [로그 관리](#로그-관리)
7. [모니터링](#모니터링)
8. [자동 시작 설정](#자동-시작-설정)

---

## 🎯 PM2 소개

PM2는 Node.js 애플리케이션을 위한 프로세스 관리자입니다.

**주요 기능:**
- 프로세스 자동 재시작
- 로그 관리
- 클러스터 모드
- 모니터링
- 배포 관리

---

## 📥 설치

```bash
# 전역 설치
npm install -g pm2

# 버전 확인
pm2 --version

# PM2 업데이트
npm update -g pm2
```

---

## 🚀 기본 사용법

### 프로세스 시작

```bash
# 단일 파일 실행
pm2 start app.js

# 이름 지정
pm2 start app.js --name "my-app"

# Python 애플리케이션
pm2 start "python3 main.py" --name backend --interpreter python3

# 클러스터 모드 (CPU 코어 수만큼)
pm2 start app.js -i max
```

### Cafe24 vs 로컬 차이

| 상황 | Cafe24 서버 | 로컬 개발 |
|-----|------------|---------|
| **처음 시작** | `pm2 start ecosystem.config.cjs` | `pm2 start ecosystem.config.cjs` |
| **이미 실행 중** | `pm2 restart all` ✅ | `pm2 restart all` ✅ |
| **코드 업데이트 후** | `pm2 restart all` | `pm2 restart all` |
| **서버 재부팅 후** | 자동 시작 | `pm2 resurrect` 또는 재시작 |

---

## ⚙️ ecosystem.config.cjs

BH2025 WOWU 프로젝트 설정:

```javascript
module.exports = {
  apps: [
    {
      name: 'frontend-server',
      script: './frontend/proxy-server.cjs',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      env: {
        NODE_ENV: 'production',
        PORT: 3000
      },
      error_file: './logs/frontend-error.log',
      out_file: './logs/frontend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true
    },
    {
      name: 'backend-server',
      script: 'python3',
      args: '-m uvicorn main:app --host 0.0.0.0 --port 8000',
      cwd: './backend',
      instances: 1,
      exec_mode: 'fork',
      watch: false,
      interpreter: 'none',
      env: {
        PYTHONUNBUFFERED: '1',
        VIRTUAL_ENV: './venv'
      },
      error_file: './logs/backend-error.log',
      out_file: './logs/backend-out.log',
      log_date_format: 'YYYY-MM-DD HH:mm:ss Z',
      merge_logs: true
    }
  ]
};
```

### 설정 사용

```bash
# ecosystem 파일로 시작
pm2 start ecosystem.config.cjs

# 특정 앱만 시작
pm2 start ecosystem.config.cjs --only frontend-server

# 업데이트 후 재시작
pm2 reload ecosystem.config.cjs

# 환경변수 업데이트와 함께 재시작
pm2 restart ecosystem.config.cjs --update-env
```

---

## 🎛️ 프로세스 관리

### 상태 확인

```bash
# 전체 상태
pm2 status

# 상세 정보
pm2 show frontend-server

# 실시간 모니터링
pm2 monit
```

### 시작/중지/재시작

```bash
# 전체 재시작
pm2 restart all

# 특정 앱 재시작
pm2 restart frontend-server

# 무중단 재시작 (클러스터 모드)
pm2 reload all

# 중지
pm2 stop all
pm2 stop frontend-server

# 삭제 (PM2에서 제거)
pm2 delete all
pm2 delete frontend-server
```

### 프로세스 목록 관리

```bash
# 현재 상태 저장
pm2 save

# 저장된 상태로 복원
pm2 resurrect

# 모든 프로세스 제거
pm2 kill
```

---

## 📝 로그 관리

### 로그 확인

```bash
# 전체 로그 (실시간)
pm2 logs

# 특정 앱 로그
pm2 logs frontend-server

# 스크롤 없이 보기
pm2 logs --nostream

# 최근 N줄만 보기
pm2 logs --lines 100

# 에러 로그만
pm2 logs --err

# 출력 로그만
pm2 logs --out
```

### 로그 파일 관리

```bash
# 로그 파일 비우기
pm2 flush

# 로그 파일 위치
~/.pm2/logs/

# 프로젝트별 로그
./logs/frontend-error.log
./logs/frontend-out.log
./logs/backend-error.log
./logs/backend-out.log
```

---

## 📊 모니터링

### 실시간 모니터링

```bash
# 대시보드
pm2 monit

# 간단한 상태
pm2 status

# 메모리/CPU 사용량
pm2 list
```

### PM2 Plus (웹 모니터링 - 선택사항)

```bash
# PM2 Plus 연결
pm2 link [secret_key] [public_key]

# 웹에서 모니터링
# https://app.pm2.io
```

---

## 🔄 자동 시작 설정

### 서버 재부팅 시 자동 시작

```bash
# 자동 시작 스크립트 생성
pm2 startup

# 출력된 명령어 복사 후 실행
# 예: sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u root --hp /root

# 현재 PM2 프로세스 상태 저장
pm2 save

# 자동 시작 확인
sudo systemctl status pm2-root
```

### 자동 시작 제거

```bash
# 자동 시작 비활성화
pm2 unstartup

# PM2 프로세스 삭제
pm2 delete all
pm2 save --force
```

---

## 🔧 고급 설정

### 환경변수 설정

```bash
# 환경변수와 함께 시작
pm2 start app.js --env production

# ecosystem.config.cjs에서 설정
env: {
  NODE_ENV: 'production',
  PORT: 3000,
  DB_HOST: 'localhost'
}
```

### Watch 모드 (개발용)

```bash
# 파일 변경 감지 및 자동 재시작
pm2 start app.js --watch

# 특정 폴더 제외
pm2 start app.js --watch --ignore-watch="node_modules"
```

### 메모리 기반 재시작

```bash
# 메모리 사용량이 500MB 초과 시 재시작
pm2 start app.js --max-memory-restart 500M
```

---

## 💡 실전 팁

### Cafe24 배포 워크플로우

```bash
# 1. 서버 접속
ssh root@cafe24-server

# 2. 프로젝트 폴더로 이동
cd /root/BH2025_WOWU

# 3. 최신 코드 받기
git pull origin main

# 4. 의존성 업데이트 (필요시)
npm install
cd backend && source venv/bin/activate && pip install -r requirements.txt && deactivate && cd ..

# 5. PM2 재시작
pm2 restart all --update-env

# 6. 로그 확인
pm2 logs --lines 50
```

### 로컬 개발 워크플로우

```bash
# 1. 프로젝트 폴더로 이동
cd "G:\내 드라이브\11. DEV_23\51. Python_mp3등\BH2025_WOWU"

# 2. 최신 코드 받기
git pull origin main

# 3. PM2 상태 확인
pm2 status

# 4a. 서버가 없으면 시작
pm2 start ecosystem.config.cjs

# 4b. 서버가 있으면 재시작
pm2 restart all

# 5. 브라우저에서 확인
# http://localhost:3000
```

---

## 🐛 문제 해결

### 프로세스가 시작되지 않음

```bash
# 상세 로그 확인
pm2 logs --err

# 프로세스 상세 정보
pm2 show backend-server

# 수동으로 실행해보기
cd backend
source venv/bin/activate
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 메모리 부족

```bash
# 메모리 사용량 확인
pm2 status
free -h

# 프로세스 재시작
pm2 restart all

# 로그 정리
pm2 flush
```

### PM2가 응답하지 않음

```bash
# PM2 데몬 재시작
pm2 kill
pm2 resurrect

# 또는 처음부터
pm2 start ecosystem.config.cjs
```

---

## ✅ 체크리스트

### 초기 설정
- [ ] PM2 전역 설치
- [ ] ecosystem.config.cjs 설정
- [ ] 로그 디렉토리 생성
- [ ] 자동 시작 설정

### 일상 관리
- [ ] pm2 status로 상태 확인
- [ ] pm2 logs로 로그 모니터링
- [ ] 주기적으로 pm2 flush
- [ ] 업데이트 후 pm2 restart all

---

## 🔗 관련 문서

- [전체 배포 가이드](./01_DEPLOYMENT_GUIDE.md)
- [Nginx 설정](./03_NGINX_CONFIG.md)
- [코드 업데이트](./06_UPDATE_WORKFLOW.md)

---

## 📚 참고 자료

- PM2 공식 문서: https://pm2.keymetrics.io/docs/
- PM2 GitHub: https://github.com/Unitech/pm2

---

**작성자**: EmmettHwang  
**마지막 업데이트**: 2024-12-XX  
**버전**: 1.0.0
