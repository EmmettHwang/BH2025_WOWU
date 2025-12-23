# 🚀 전체 배포 가이드

완전히 새로운 서버에 BH2025 WOWU 프로젝트를 배포하는 전체 과정입니다.

---

## 📋 목차

1. [배포 전 준비사항](#배포-전-준비사항)
2. [배포 순서 개요](#배포-순서-개요)
3. [단계별 상세 가이드](#단계별-상세-가이드)
4. [전체 명령어 스크립트](#전체-명령어-스크립트)
5. [배포 후 확인사항](#배포-후-확인사항)
6. [자주 묻는 질문](#자주-묻는-질문)

---

## 📌 배포 전 준비사항

### 필요한 정보
- [ ] 서버 접속 정보 (IP, SSH 포트, 사용자명, 비밀번호)
- [ ] 도메인 (선택사항)
- [ ] GitHub 계정 및 저장소 접근 권한
- [ ] 데이터베이스 접속 정보
- [ ] FTP 서버 접속 정보
- [ ] OpenAI API 키 (선택사항)

### 권장 서버 사양
- **OS**: Ubuntu 20.04 LTS 이상
- **CPU**: 2 Core 이상
- **RAM**: 2GB 이상
- **Storage**: 20GB 이상
- **네트워크**: 공인 IP 또는 도메인

---

## 🎯 배포 순서 개요

```
1. 서버 임대 및 기본 설정
   ├─ 서버 접속 (SSH)
   ├─ 시스템 업데이트
   └─ 보안 설정

2. 개발 환경 구축
   ├─ Git 설치
   ├─ Python 설치
   ├─ Node.js 설치
   └─ 데이터베이스 설치 (선택)

3. 프로젝트 설정
   ├─ 프로젝트 클론
   ├─ SSH 키 설정
   ├─ Python 패키지 설치
   └─ Node.js 패키지 설치

4. 웹 서버 설정
   ├─ Nginx 설치
   ├─ 프록시 설정
   └─ SSL 인증서 (선택)

5. 애플리케이션 실행
   ├─ PM2 설치
   ├─ 서버 시작
   └─ 자동 시작 설정

6. 배포 완료 및 확인
   ├─ 상태 확인
   ├─ 로그 확인
   └─ 기능 테스트
```

---

## 📚 단계별 상세 가이드

### 1단계: 서버 기본 설정

```bash
# SSH로 서버 접속
ssh root@your-server-ip
# 또는
ssh -p 22 user@your-server-ip

# 시스템 업데이트
sudo apt update && sudo apt upgrade -y

# 필수 유틸리티 설치
sudo apt install -y curl wget git build-essential software-properties-common

# 방화벽 설정
sudo ufw allow OpenSSH
sudo ufw allow 80/tcp      # HTTP
sudo ufw allow 443/tcp     # HTTPS
sudo ufw allow 3000/tcp    # Frontend (개발용)
sudo ufw allow 8000/tcp    # Backend (개발용)
sudo ufw enable

# 시간대 설정
sudo timedatectl set-timezone Asia/Seoul
```

---

### 2단계: Python 설치

```bash
# Python 3.8+ 설치
sudo apt install -y python3 python3-pip python3-venv python3-dev

# 버전 확인
python3 --version
pip3 --version

# pip 업그레이드
python3 -m pip install --upgrade pip
```

---

### 3단계: Node.js 설치

```bash
# Node.js 18.x LTS 설치
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 버전 확인
node --version
npm --version
```

---

### 4단계: MySQL 설치 (선택사항)

**현재 프로젝트는 외부 DB를 사용하므로 선택사항입니다.**

```bash
# MySQL 설치
sudo apt install -y mysql-server

# MySQL 보안 설정
sudo mysql_secure_installation

# MySQL 접속
sudo mysql

# 데이터베이스 생성
CREATE DATABASE bh2025 CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'bh2025user'@'localhost' IDENTIFIED BY 'your_secure_password';
GRANT ALL PRIVILEGES ON bh2025.* TO 'bh2025user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

### 5단계: 프로젝트 클론

```bash
# 작업 디렉토리 이동
cd /root
# 또는
cd /home/username

# Git 사용자 설정
git config --global user.name "EmmettHwang"
git config --global user.email "your-email@example.com"

# SSH 키 생성 (GitHub 인증용)
ssh-keygen -t ed25519 -C "your-email@example.com"

# 공개 키 출력 (GitHub에 등록)
cat ~/.ssh/id_ed25519.pub

# GitHub에 SSH 키 등록 후 클론
git clone git@github.com:EmmettHwang/BH2025_WOWU.git

# 또는 HTTPS로 클론
git clone https://github.com/EmmettHwang/BH2025_WOWU.git

# 프로젝트 폴더로 이동
cd BH2025_WOWU
```

---

### 6단계: Python 환경 설정

```bash
# backend 폴더로 이동
cd backend

# Python 가상환경 생성
python3 -m venv venv

# 가상환경 활성화
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip

# 패키지 설치
pip install -r requirements.txt

# 가상환경 비활성화
deactivate

# 프로젝트 루트로 이동
cd ..
```

---

### 7단계: Node.js 환경 설정

```bash
# 프로젝트 루트에서
npm install

# PM2 전역 설치
sudo npm install -g pm2

# 버전 확인
pm2 --version
```

---

### 8단계: 환경변수 설정 (선택사항)

**현재 프로젝트는 `backend/main.py`에 기본값이 설정되어 있어 선택사항입니다.**

```bash
# .env 파일 생성
nano backend/.env
```

**.env 파일 내용:**
```env
# 데이터베이스 설정
DB_HOST=bitnmeta2.synology.me
DB_PORT=3307
DB_USER=iyrc
DB_PASSWORD=Dodan1004!
DB_NAME=bh2025

# FTP 설정
FTP_HOST=bitnmeta2.synology.me
FTP_PORT=2121
FTP_USER=ha
FTP_PASSWORD=dodan1004~

# OpenAI API
OPENAI_API_KEY=your_api_key_here
```

**저장**: `Ctrl + O` → `Enter` → `Ctrl + X`

---

### 9단계: Nginx 설치 및 설정

```bash
# Nginx 설치
sudo apt install -y nginx

# Nginx 설정 파일 생성
sudo nano /etc/nginx/sites-available/bh2025
```

**Nginx 설정 내용:**
```nginx
server {
    listen 80;
    server_name yourdomain.com;  # 또는 서버 IP 주소
    
    # 파일 업로드 크기 제한 (100MB)
    client_max_body_size 100M;

    # 프론트엔드 (포트 3000)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 백엔드 API (포트 8000)
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # API 타임아웃 설정
        proxy_connect_timeout 600;
        proxy_send_timeout 600;
        proxy_read_timeout 600;
        send_timeout 600;
    }
}
```

```bash
# 설정 활성화
sudo ln -s /etc/nginx/sites-available/bh2025 /etc/nginx/sites-enabled/

# 기본 설정 비활성화
sudo rm /etc/nginx/sites-enabled/default

# 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx

# Nginx 자동 시작 설정
sudo systemctl enable nginx

# Nginx 상태 확인
sudo systemctl status nginx
```

---

### 10단계: PM2로 서버 시작

```bash
# 프로젝트 루트로 이동
cd /root/BH2025_WOWU
# 또는
cd /home/username/BH2025_WOWU

# PM2로 서버 시작
pm2 start ecosystem.config.cjs

# 상태 확인
pm2 status

# 로그 확인
pm2 logs --lines 50

# 현재 PM2 상태 저장
pm2 save

# 서버 재부팅 시 자동 시작 설정
pm2 startup

# 출력된 명령어를 복사해서 실행
# 예: sudo env PATH=$PATH:/usr/bin /usr/lib/node_modules/pm2/bin/pm2 startup systemd -u root --hp /root

# 다시 저장
pm2 save
```

---

### 11단계: SSL 인증서 설치 (HTTPS)

```bash
# Certbot 설치
sudo apt install -y certbot python3-certbot-nginx

# SSL 인증서 발급 (도메인 필요)
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 이메일 입력 및 약관 동의
# 도메인 소유 확인 자동 진행

# 자동 갱신 테스트
sudo certbot renew --dry-run

# Nginx 재시작
sudo systemctl restart nginx
```

---

## 🖥️ 전체 명령어 스크립트

### 한 번에 실행 (복사 가능)

```bash
#!/bin/bash

echo "========================================="
echo "  BH2025 WOWU 서버 배포 스크립트"
echo "========================================="

# 1. 시스템 업데이트
echo "[1/11] 시스템 업데이트..."
sudo apt update && sudo apt upgrade -y

# 2. 필수 도구 설치
echo "[2/11] 필수 도구 설치..."
sudo apt install -y curl wget git build-essential software-properties-common

# 3. Python 설치
echo "[3/11] Python 설치..."
sudo apt install -y python3 python3-pip python3-venv python3-dev
python3 -m pip install --upgrade pip

# 4. Node.js 설치
echo "[4/11] Node.js 설치..."
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 5. 방화벽 설정
echo "[5/11] 방화벽 설정..."
sudo ufw allow OpenSSH
sudo ufw allow 80,443,3000,8000/tcp
sudo ufw --force enable

# 6. 프로젝트 클론
echo "[6/11] 프로젝트 클론..."
cd /root
git clone https://github.com/EmmettHwang/BH2025_WOWU.git
cd BH2025_WOWU

# 7. Python 환경 설정
echo "[7/11] Python 패키지 설치..."
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# 8. Node.js 환경 설정
echo "[8/11] Node.js 패키지 설치..."
npm install
sudo npm install -g pm2

# 9. Nginx 설치
echo "[9/11] Nginx 설치..."
sudo apt install -y nginx

# 10. PM2 시작
echo "[10/11] 서버 시작..."
pm2 start ecosystem.config.cjs
pm2 save
pm2 startup

# 11. 완료
echo "[11/11] 배포 완료!"
echo "========================================="
echo "서버 상태:"
pm2 status
echo ""
echo "접속 URL:"
echo "  - Frontend: http://$(curl -s ifconfig.me):3000"
echo "  - Backend: http://$(curl -s ifconfig.me):8000"
echo "========================================="
```

**스크립트 저장 및 실행:**
```bash
# 스크립트 저장
nano deploy.sh

# 위 내용 붙여넣기 후 저장

# 실행 권한 부여
chmod +x deploy.sh

# 실행
./deploy.sh
```

---

## ✅ 배포 후 확인사항

### 1. PM2 상태 확인

```bash
pm2 status
```

**예상 출력:**
```
┌─────┬───────────────────┬─────────┬─────────┬─────────┬──────────┐
│ id  │ name              │ mode    │ ↺      │ status  │ cpu      │
├─────┼───────────────────┼─────────┼─────────┼─────────┼──────────┤
│ 0   │ frontend-server   │ fork    │ 0       │ online  │ 0%       │
│ 1   │ backend-server    │ fork    │ 0       │ online  │ 0%       │
└─────┴───────────────────┴─────────┴─────────┴─────────┴──────────┘
```

### 2. 로그 확인

```bash
# PM2 로그
pm2 logs --lines 100

# Nginx 로그
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log
```

### 3. 포트 확인

```bash
# 포트 8000 (백엔드) 확인
curl http://localhost:8000
# 또는
netstat -tlnp | grep 8000

# 포트 3000 (프론트엔드) 확인
curl http://localhost:3000
# 또는
netstat -tlnp | grep 3000
```

### 4. 브라우저 테스트

```bash
# 서버 IP 확인
curl ifconfig.me

# 브라우저에서 접속
# http://서버IP
# 또는
# http://yourdomain.com
```

### 5. 기능 테스트 체크리스트

- [ ] 로그인 페이지 접속
- [ ] 관리자 로그인
- [ ] 학생 관리 메뉴 접근
- [ ] 파일 업로드 테스트
- [ ] 이미지 썸네일 표시
- [ ] PDF 미리보기
- [ ] AI 챗봇 (예진이 만나기) 메뉴 확인
- [ ] 데이터베이스 연동 확인

---

## 🎯 배포 체크리스트

### 배포 전
- [ ] 서버 접속 정보 확인
- [ ] GitHub 저장소 접근 권한
- [ ] DB 접속 정보 확인
- [ ] 도메인 DNS 설정 (선택)

### 배포 중
- [ ] 시스템 업데이트
- [ ] Python 설치 (3.8+)
- [ ] Node.js 설치 (18.x)
- [ ] 프로젝트 클론
- [ ] Python 패키지 설치
- [ ] Node.js 패키지 설치
- [ ] PM2 설치
- [ ] Nginx 설치 및 설정
- [ ] 방화벽 설정

### 배포 후
- [ ] PM2 상태 online 확인
- [ ] 로그 에러 없음 확인
- [ ] 브라우저 접속 테스트
- [ ] 로그인 기능 테스트
- [ ] 파일 업로드 테스트
- [ ] SSL 인증서 (선택)
- [ ] 자동 시작 설정
- [ ] 백업 계획 수립

---

## ❓ 자주 묻는 질문

### Q1: 포트 3000, 8000을 외부에 노출하지 않으려면?

**A:** Nginx를 통해서만 접근하도록 방화벽 설정을 조정하세요.

```bash
# 외부 접근 차단
sudo ufw delete allow 3000/tcp
sudo ufw delete allow 8000/tcp

# Nginx(80, 443)만 허용
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### Q2: 다른 포트를 사용하고 싶어요

**A:** `ecosystem.config.cjs` 파일을 수정하세요.

```javascript
// ecosystem.config.cjs
module.exports = {
  apps: [
    {
      name: 'frontend-server',
      script: './frontend/proxy-server.cjs',
      env: {
        PORT: 5000  // 포트 변경
      }
    },
    // ...
  ]
}
```

Nginx 설정도 함께 수정:
```nginx
location / {
    proxy_pass http://localhost:5000;  # 변경된 포트
    # ...
}
```

### Q3: 데이터베이스를 서버에 설치해야 하나요?

**A:** 현재 프로젝트는 외부 DB(`bitnmeta2.synology.me:3307`)를 사용하므로 선택사항입니다. 독립적인 운영을 원하면 서버에 MySQL을 설치하고 `.env` 파일을 수정하세요.

### Q4: SSL 인증서가 필요한가요?

**A:** HTTPS 사용을 위해 권장하지만 필수는 아닙니다. Let's Encrypt를 사용하면 무료로 설치할 수 있습니다.

### Q5: 서버 재부팅 후 자동으로 시작되나요?

**A:** `pm2 startup`과 `pm2 save`를 실행했다면 자동 시작됩니다.

---

## 🔗 관련 문서

- [서버 초기 설정](./02_SERVER_SETUP.md)
- [Nginx 설정](./03_NGINX_CONFIG.md)
- [PM2 관리](./04_PM2_MANAGEMENT.md)
- [문제 해결](./05_TROUBLESHOOTING.md)
- [코드 업데이트](./06_UPDATE_WORKFLOW.md)

---

## 📞 지원

배포 중 문제가 발생하면:
1. [문제 해결 가이드](./05_TROUBLESHOOTING.md) 확인
2. 로그 확인: `pm2 logs`
3. GitHub Issues: https://github.com/EmmettHwang/BH2025_WOWU/issues

---

**작성자**: EmmettHwang  
**마지막 업데이트**: 2024-12-XX  
**버전**: 1.0.0
