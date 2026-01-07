# 🐛 문제 해결 가이드

배포 및 운영 중 발생할 수 있는 일반적인 문제들과 해결 방법입니다.

---

## 📋 목차

1. [서버 접속 문제](#서버-접속-문제)
2. [배포 중 오류](#배포-중-오류)
3. [애플리케이션 오류](#애플리케이션-오류)
4. [데이터베이스 문제](#데이터베이스-문제)
5. [파일 업로드 문제](#파일-업로드-문제)
6. [성능 문제](#성능-문제)
7. [로그 확인 방법](#로그-확인-방법)

---

## 🔐 서버 접속 문제

### ❌ SSH 접속 거부

**증상**: `Connection refused` 또는 `Permission denied`

**원인 및 해결:**

```bash
# 1. SSH 서비스 확인
sudo systemctl status sshd

# 2. SSH 서비스 재시작
sudo systemctl restart sshd

# 3. 방화벽 확인
sudo ufw status
sudo ufw allow 22/tcp

# 4. SSH 포트 확인
sudo netstat -tlnp | grep sshd
```

### ❌ SSH 키 인증 실패

**증상**: `Permission denied (publickey)`

```bash
# 로컬에서 공개키 재전송
ssh-copy-id -i ~/.ssh/id_ed25519.pub user@server-ip

# 서버에서 권한 확인
chmod 700 ~/.ssh
chmod 600 ~/.ssh/authorized_keys

# SSH 설정 확인
sudo nano /etc/ssh/sshd_config
# PubkeyAuthentication yes 확인
sudo systemctl restart sshd
```

---

## 💥 배포 중 오류

### ❌ Git Clone 실패

**증상**: `Permission denied` 또는 `Authentication failed`

```bash
# SSH 키 확인
cat ~/.ssh/id_ed25519.pub

# GitHub에 SSH 키 등록 확인
# https://github.com/settings/keys

# HTTPS로 클론 (대안)
git clone https://github.com/EmmettHwang/BH2025_WOWU.git

# Personal Access Token 사용
git clone https://[TOKEN]@github.com/EmmettHwang/BH2025_WOWU.git
```

### ❌ Python 패키지 설치 실패

**증상**: `pip install` 실패

```bash
# pip 업그레이드
python3 -m pip install --upgrade pip

# 가상환경 재생성
cd backend
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 개별 패키지 설치
pip install fastapi uvicorn pymysql pandas pillow

# 의존성 충돌 해결
pip install --upgrade --force-reinstall -r requirements.txt
```

### ❌ Node.js 패키지 설치 실패

**증상**: `npm install` 오류

```bash
# npm 캐시 정리
npm cache clean --force

# node_modules 삭제 후 재설치
rm -rf node_modules package-lock.json
npm install

# npm 버전 업그레이드
npm install -g npm@latest

# 권한 문제 해결
sudo chown -R $USER ~/.npm
```

---

## 🚨 애플리케이션 오류

### ❌ PM2 프로세스가 시작 안 됨

**증상**: `pm2 status`에서 `errored` 상태

```bash
# 상세 로그 확인
pm2 logs --err

# 프로세스 삭제 후 재시작
pm2 delete all
pm2 start ecosystem.config.cjs

# 수동 실행으로 에러 확인
cd backend
source venv/bin/activate
python3 -m uvicorn main:app --host 0.0.0.0 --port 8000

# 프론트엔드
node frontend/proxy-server.cjs
```

### ❌ 포트가 이미 사용 중

**증상**: `Address already in use` 또는 `EADDRINUSE`

```bash
# 포트 사용 프로세스 확인
sudo netstat -tlnp | grep :8000
sudo netstat -tlnp | grep :3000

# 프로세스 종료 (PID 확인 후)
sudo kill -9 [PID]

# 또는 포트별 종료
sudo fuser -k 8000/tcp
sudo fuser -k 3000/tcp

# PM2로 정리
pm2 delete all
pm2 status
```

### ❌ 503 Bad Gateway (Nginx)

**증상**: Nginx에서 503 에러

```bash
# 1. 백엔드 서버 확인
pm2 status
pm2 logs backend-server

# 2. 포트 리스닝 확인
netstat -tlnp | grep :8000
netstat -tlnp | grep :3000

# 3. 백엔드 재시작
pm2 restart backend-server

# 4. Nginx 설정 확인
sudo nginx -t
sudo tail -f /var/log/nginx/error.log

# 5. Nginx 재시작
sudo systemctl restart nginx
```

### ❌ 500 Internal Server Error

**증상**: API 요청 시 500 에러

```bash
# 백엔드 로그 확인
pm2 logs backend-server --lines 100

# Python 에러 확인
cd backend
source venv/bin/activate
python3 -c "import main"

# 환경변수 확인
cat backend/.env

# 데이터베이스 연결 테스트
mysql -h bitnmeta2.synology.me -P 3307 -u iyrc -p
```

---

## 🗄️ 데이터베이스 문제

### ❌ 데이터베이스 연결 실패

**증상**: `Can't connect to MySQL server`

```bash
# 1. 네트워크 연결 확인
ping bitnmeta2.synology.me
telnet bitnmeta2.synology.me 3307

# 2. MySQL 접속 테스트
mysql -h bitnmeta2.synology.me -P 3307 -u iyrc -p

# 3. 방화벽 확인
sudo ufw status

# 4. VPN 연결 확인 (필요시)
# VPN이 필요한 경우 VPN 연결 후 재시도
```

### ❌ 테이블이 없음

**증상**: `Table doesn't exist`

```bash
# MySQL 접속
mysql -h bitnmeta2.synology.me -P 3307 -u iyrc -p bh2025

# 테이블 목록 확인
SHOW TABLES;

# 테이블 구조 확인
DESCRIBE students;
DESCRIBE instructors;

# 마이그레이션 실행 (필요시)
cd migrations
# SQL 파일 실행
```

### ❌ 인코딩 문제 (한글 깨짐)

**증상**: 한글이 `?????`로 표시

```bash
# 데이터베이스 인코딩 확인
mysql -h bitnmeta2.synology.me -P 3307 -u iyrc -p
SHOW VARIABLES LIKE 'character%';

# 테이블 인코딩 변경
ALTER DATABASE bh2025 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE students CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
```

---

## 📤 파일 업로드 문제

### ❌ 413 Request Entity Too Large

**증상**: 파일 업로드 시 413 에러

```bash
# 1. Nginx 설정 확인
sudo grep -r "client_max_body_size" /etc/nginx/

# 2. Nginx 설정 수정
sudo nano /etc/nginx/nginx.conf
# http 블록에 추가:
# client_max_body_size 100M;

# 또는 사이트별 설정
sudo nano /etc/nginx/sites-available/bh2025
# server 블록에 추가:
# client_max_body_size 100M;

# 3. Nginx 재시작
sudo nginx -t
sudo systemctl reload nginx
```

### ❌ 500 이미지 다운로드 오류

**증상**: 이미지 썸네일/다운로드 시 500 에러

```bash
# 1. FTP 연결 확인
cd /home/user/webapp
python3 test_ftp.py

# 2. 백엔드 로그 확인
pm2 logs backend-server | grep -i "ftp\|image\|thumbnail"

# 3. 썸네일 디렉토리 권한 확인
ls -la backend/thumbnails/
chmod 755 backend/thumbnails/

# 4. 임시 디렉토리 권한 확인 (Windows)
# Python이 tempfile.gettempdir() 사용
```

### ❌ 한글 파일명 업로드 문제

**증상**: 한글 파일명이 깨지거나 업로드 실패

```bash
# 백엔드 코드에서 자동 처리됨
# 한글 → ASCII로 변환 (타임스탬프 + UUID 추가)

# FTP 인코딩 확인
pm2 logs backend-server | grep -i "encoding"

# 최신 코드로 업데이트
git pull origin main
pm2 restart all
```

---

## ⚡ 성능 문제

### ❌ 서버 응답 느림

**증상**: 페이지 로딩이 느림

```bash
# 1. CPU/메모리 확인
htop
free -h

# 2. 디스크 사용량 확인
df -h
du -sh /*

# 3. PM2 리소스 확인
pm2 monit

# 4. 네트워크 확인
ping 8.8.8.8
curl -w "@-" -o /dev/null -s http://localhost:8000 <<'EOF'
    time_total:  %{time_total}\n
EOF
```

### ❌ 메모리 부족

**증상**: `Out of memory` 또는 프로세스 죽음

```bash
# 1. 메모리 확인
free -h

# 2. 메모리 사용 프로세스 확인
ps aux --sort=-%mem | head -10

# 3. PM2 재시작
pm2 restart all

# 4. 스왑 메모리 추가
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 5. 로그 정리
pm2 flush
sudo journalctl --vacuum-time=3d
```

### ❌ 디스크 공간 부족

**증상**: `No space left on device`

```bash
# 1. 디스크 사용량 확인
df -h
du -sh /* | sort -rh | head -10

# 2. 큰 파일 찾기
find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null

# 3. 로그 파일 정리
sudo journalctl --vacuum-time=7d
pm2 flush
sudo rm -rf /var/log/*.gz

# 4. 패키지 캐시 정리
sudo apt autoremove -y
sudo apt autoclean

# 5. Docker 정리 (사용 시)
docker system prune -a
```

---

## 📝 로그 확인 방법

### PM2 로그

```bash
# 전체 로그
pm2 logs

# 특정 앱 로그
pm2 logs backend-server
pm2 logs frontend-server

# 에러만
pm2 logs --err

# 최근 100줄
pm2 logs --lines 100

# 특정 키워드 검색
pm2 logs | grep -i "error\|warning"
```

### Nginx 로그

```bash
# 액세스 로그
sudo tail -f /var/log/nginx/access.log

# 에러 로그
sudo tail -f /var/log/nginx/error.log

# 특정 사이트 로그
sudo tail -f /var/log/nginx/bh2025_access.log
sudo tail -f /var/log/nginx/bh2025_error.log

# 에러 검색
sudo grep -i "error" /var/log/nginx/error.log | tail -20
```

### 시스템 로그

```bash
# 시스템 전체 로그
sudo journalctl -xe

# 특정 서비스
sudo journalctl -u nginx -f
sudo journalctl -u pm2-root -f

# 최근 1시간
sudo journalctl --since "1 hour ago"

# 특정 우선순위 (0=emerg, 3=err)
sudo journalctl -p 3 -xb
```

### 애플리케이션 로그

```bash
# Python 로그
tail -f backend/logs/*.log

# Node.js 로그
tail -f frontend/logs/*.log

# PM2 로그 파일
tail -f ~/.pm2/logs/backend-error.log
tail -f ~/.pm2/logs/frontend-error.log
```

---

## 🔧 디버깅 팁

### 단계별 디버깅

```bash
# 1. 서비스 상태 확인
sudo systemctl status nginx
pm2 status

# 2. 포트 리스닝 확인
sudo netstat -tlnp | grep -E ":(80|443|3000|8000)"

# 3. 프로세스 확인
ps aux | grep -E "(nginx|python|node)"

# 4. 로그 실시간 모니터링
# 터미널 1
pm2 logs

# 터미널 2
sudo tail -f /var/log/nginx/error.log

# 5. API 테스트
curl http://localhost:8000
curl http://localhost:3000
```

### 환경변수 확인

```bash
# PM2 환경변수
pm2 show backend-server | grep env

# 시스템 환경변수
printenv | grep -E "(DB|FTP|API)"

# .env 파일 (있는 경우)
cat backend/.env
```

---

## 🚑 긴급 복구 절차

### 서비스 완전 재시작

```bash
# 1. 모든 프로세스 중지
pm2 stop all
pm2 delete all

# 2. Nginx 재시작
sudo systemctl restart nginx

# 3. 서버 재시작
pm2 start ecosystem.config.cjs
pm2 save

# 4. 상태 확인
pm2 status
sudo systemctl status nginx
```

### 이전 버전으로 롤백

```bash
# Git 로그 확인
git log --oneline -10

# 이전 커밋으로 복원
git reset --hard [commit-hash]

# 또는 특정 버전으로
git checkout [commit-hash]

# 서버 재시작
pm2 restart all --update-env
```

---

## 📞 추가 도움

### 문제 보고 시 포함할 정보

1. **에러 메시지**: 정확한 에러 메시지 전체
2. **로그**: PM2, Nginx 로그
3. **환경**: OS 버전, Node.js/Python 버전
4. **재현 단계**: 문제를 재현하는 방법
5. **시도한 해결책**: 이미 시도한 방법들

### 체크리스트

```bash
# 시스템 정보 수집
echo "=== 시스템 정보 ===" && \
uname -a && \
echo "=== Node.js ===" && \
node --version && \
npm --version && \
echo "=== Python ===" && \
python3 --version && \
echo "=== PM2 ===" && \
pm2 status && \
echo "=== Nginx ===" && \
sudo nginx -v && \
sudo systemctl status nginx && \
echo "=== 디스크 ===" && \
df -h && \
echo "=== 메모리 ===" && \
free -h
```

---

## 🔗 관련 문서

- [전체 배포 가이드](./01_DEPLOYMENT_GUIDE.md)
- [PM2 관리](./04_PM2_MANAGEMENT.md)
- [Nginx 설정](./03_NGINX_CONFIG.md)
- [모니터링 및 로그](./08_MONITORING_LOGS.md)

---

**작성자**: EmmettHwang  
**마지막 업데이트**: 2024-12-XX  
**버전**: 1.0.0
