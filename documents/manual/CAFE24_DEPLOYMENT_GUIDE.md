# Cafe24 서버호스팅 배포 가이드

## 📋 개요
Cafe24 서버호스팅(VPS)를 이용한 교육관리시스템 배포 가이드입니다.

## 🎯 Cafe24 호스팅 옵션

### ⚠️ 중요: 호스팅 종류 확인

1. **일반 웹호스팅** ❌
   - PHP/MySQL 전용
   - Python/FastAPI 실행 불가
   - **본 프로젝트에 사용 불가능**

2. **서버호스팅 (VPS)** ✅ **권장**
   - Linux 서버 전체 제어
   - Python, Node.js 등 자유롭게 설치
   - Root 권한 제공
   - **본 프로젝트 배포 가능**

3. **클라우드 서버** ✅
   - VPS와 동일하나 더 유연한 스케일링
   - **본 프로젝트 배포 가능**

### 💰 가격 (2024년 기준)
- **서버호스팅 Basic**: 월 33,000원~
- **클라우드 서버**: 월 11,000원~ (시간당 과금 가능)

---

## 🚀 배포 방법

### 방법 1: 수동 배포 (FTP + SSH) - 가장 간단

#### 사전 준비
1. **Cafe24 서버호스팅 또는 클라우드 서버 신청**
   - https://www.cafe24.com/?controller=hosting_linux
   - CentOS 또는 Ubuntu 선택 권장

2. **서버 정보 확인**
   - SSH 접속 정보 (IP, 포트, 계정, 비밀번호)
   - FTP 접속 정보
   - 할당된 도메인 또는 IP

#### 단계 1: SSH 접속

```bash
# Windows: PuTTY 또는 PowerShell 사용
# macOS/Linux: 터미널 사용

ssh username@your-server-ip
# 또는 포트가 다른 경우
ssh -p 2222 username@your-server-ip

# 비밀번호 입력
```

#### 단계 2: 서버 환경 구성

```bash
# 시스템 업데이트
sudo yum update -y  # CentOS
# 또는
sudo apt update && sudo apt upgrade -y  # Ubuntu

# Python 3.11 설치
sudo yum install python3.11 python3.11-pip -y  # CentOS
# 또는
sudo apt install python3.11 python3.11-pip -y  # Ubuntu

# Git 설치
sudo yum install git -y  # CentOS
# 또는
sudo apt install git -y  # Ubuntu

# 가상환경 도구 설치
pip3.11 install virtualenv
```

#### 단계 3: 프로젝트 배포

```bash
# 홈 디렉토리로 이동
cd ~

# GitHub에서 프로젝트 클론
git clone https://github.com/Emmett6401/BH2025_WOWU.git
cd BH2025_WOWU

# 가상환경 생성 및 활성화
python3.11 -m venv venv
source venv/bin/activate

# 의존성 설치
pip install -r backend/requirements.txt

# .env 파일 생성
cat > .env << 'EOF'
OPENAI_API_KEY=your-openai-key-here
EOF

# 권한 설정
chmod 755 -R .
```

#### 단계 4: 방화벽 및 포트 설정

```bash
# 방화벽에서 포트 8000 열기 (CentOS)
sudo firewall-cmd --permanent --add-port=8000/tcp
sudo firewall-cmd --reload

# 또는 Ubuntu
sudo ufw allow 8000/tcp
sudo ufw reload

# Cafe24 관리 콘솔에서도 포트 8000 개방 필요!
```

#### 단계 5: 서비스 실행 (PM2 사용)

```bash
# Node.js 및 PM2 설치
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
source ~/.bashrc
nvm install 18
npm install -g pm2

# PM2로 백엔드 실행
cd ~/BH2025_WOWU/backend
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name bhhs-backend

# PM2 자동 시작 설정
pm2 startup
pm2 save

# 상태 확인
pm2 list
pm2 logs bhhs-backend
```

#### 단계 6: Nginx 리버스 프록시 설정 (선택사항)

```bash
# Nginx 설치
sudo yum install nginx -y  # CentOS
# 또는
sudo apt install nginx -y  # Ubuntu

# Nginx 설정 파일 생성
sudo nano /etc/nginx/conf.d/bhhs.conf
```

**Nginx 설정 내용:**
```nginx
server {
    listen 80;
    server_name your-domain.com;  # 또는 서버 IP

    # 클라이언트 최대 업로드 크기 (사진 업로드용)
    client_max_body_size 20M;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 타임아웃 설정 (AI 생성 등 긴 요청 대응)
        proxy_connect_timeout 300;
        proxy_send_timeout 300;
        proxy_read_timeout 300;
    }
}
```

```bash
# Nginx 설정 테스트
sudo nginx -t

# Nginx 시작 및 자동 시작 설정
sudo systemctl start nginx
sudo systemctl enable nginx

# 방화벽에서 HTTP(80) 포트 열기
sudo firewall-cmd --permanent --add-service=http
sudo firewall-cmd --reload
```

#### 단계 7: 도메인 연결 (선택사항)

1. **Cafe24 관리 콘솔**에서 도메인 설정
2. **DNS A 레코드** 추가:
   - 호스트: @ (또는 www)
   - 값: 서버 IP 주소
   - TTL: 3600

3. 전파 대기 (1~24시간)

---

### 방법 2: Docker 배포 (고급)

#### 단계 1: Docker 설치

```bash
# Docker 설치 스크립트 실행
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Docker Compose 설치
sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose

# Docker 서비스 시작
sudo systemctl start docker
sudo systemctl enable docker

# 현재 사용자를 docker 그룹에 추가
sudo usermod -aG docker $USER
# 재로그인 필요
```

#### 단계 2: Docker로 배포

```bash
cd ~/BH2025_WOWU

# Docker 이미지 빌드
docker build -t bhhs-edu-system .

# 컨테이너 실행
docker run -d \
  --name bhhs-backend \
  --restart always \
  -p 8000:8080 \
  --env-file .env \
  bhhs-edu-system

# 상태 확인
docker ps
docker logs bhhs-backend
```

---

## 🔧 Cafe24 관리 콘솔 설정

### 1. 방화벽 규칙 추가
```
Cafe24 관리 콘솔 로그인
→ 서버 관리
→ 방화벽 설정
→ 포트 8000 (또는 80) 인바운드 허용
```

### 2. SSL 인증서 설정 (HTTPS)
```
Cafe24 관리 콘솔
→ SSL 인증서 관리
→ Let's Encrypt 무료 인증서 신청
→ 도메인 선택 및 자동 갱신 설정
```

### 3. 백업 설정
```
Cafe24 관리 콘솔
→ 백업 관리
→ 자동 백업 활성화 (일일 권장)
```

---

## 📊 모니터링 및 관리

### PM2 명령어

```bash
# 서비스 상태 확인
pm2 list

# 로그 확인 (실시간)
pm2 logs bhhs-backend

# 로그 확인 (최근 100줄)
pm2 logs bhhs-backend --lines 100

# 서비스 재시작
pm2 restart bhhs-backend

# 서비스 중지
pm2 stop bhhs-backend

# 서비스 삭제
pm2 delete bhhs-backend

# 모든 서비스 재시작
pm2 restart all
```

### 시스템 리소스 모니터링

```bash
# CPU/메모리 사용률
top
# 또는
htop  # 설치 필요: sudo yum install htop

# 디스크 사용량
df -h

# 메모리 사용량
free -h

# 네트워크 연결 확인
netstat -tulpn | grep :8000
```

---

## 🔄 업데이트 배포

### 코드 업데이트 시

```bash
# SSH 접속
ssh username@your-server-ip

# 프로젝트 디렉토리로 이동
cd ~/BH2025_WOWU

# 최신 코드 가져오기
git pull origin main

# 가상환경 활성화
source venv/bin/activate

# 의존성 업데이트 (필요시)
pip install -r backend/requirements.txt

# PM2로 재시작
pm2 restart bhhs-backend

# 로그 확인
pm2 logs bhhs-backend --lines 50
```

---

## 🚨 트러블슈팅

### 1. 포트가 이미 사용 중
```bash
# 포트 8000을 사용하는 프로세스 찾기
sudo lsof -i :8000

# 프로세스 종료
sudo kill -9 PID번호
```

### 2. Python 버전 문제
```bash
# Python 버전 확인
python3.11 --version

# 가상환경에서 Python 버전 확인
source venv/bin/activate
python --version
```

### 3. 메모리 부족
```bash
# 스왑 메모리 추가
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 영구 설정
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

### 4. 데이터베이스 연결 실패
```bash
# MySQL 서버 접근 테스트
telnet bitnmeta2.synology.me 3307

# Python에서 연결 테스트
python3.11 << 'EOF'
import pymysql
try:
    conn = pymysql.connect(
        host='bitnmeta2.synology.me',
        user='iyrc',
        passwd='Dodan1004!',
        db='bh2025',
        port=3307
    )
    print("✅ 데이터베이스 연결 성공!")
    conn.close()
except Exception as e:
    print(f"❌ 연결 실패: {e}")
EOF
```

### 5. Nginx 502 Bad Gateway
```bash
# FastAPI 서비스 상태 확인
pm2 list
pm2 logs bhhs-backend

# 로컬에서 API 테스트
curl http://localhost:8000/health

# Nginx 로그 확인
sudo tail -f /var/log/nginx/error.log
```

---

## 🔐 보안 설정

### 1. SSH 보안 강화
```bash
# SSH 포트 변경 (기본 22 → 다른 포트)
sudo nano /etc/ssh/sshd_config
# Port 22 → Port 2222 로 변경

# 루트 로그인 비활성화
# PermitRootLogin yes → PermitRootLogin no

# SSH 재시작
sudo systemctl restart sshd
```

### 2. 방화벽 설정
```bash
# 필요한 포트만 열기
sudo firewall-cmd --permanent --remove-service=ssh  # 기본 22 제거
sudo firewall-cmd --permanent --add-port=2222/tcp  # 새 SSH 포트
sudo firewall-cmd --permanent --add-port=80/tcp    # HTTP
sudo firewall-cmd --permanent --add-port=443/tcp   # HTTPS
sudo firewall-cmd --reload
```

### 3. 자동 업데이트 설정
```bash
# CentOS
sudo yum install yum-cron -y
sudo systemctl start yum-cron
sudo systemctl enable yum-cron

# Ubuntu
sudo apt install unattended-upgrades -y
sudo dpkg-reconfigure -plow unattended-upgrades
```

---

## 📱 FTP를 통한 파일 업로드 (초보자용)

Cafe24 FTP를 사용하여 코드를 업로드하는 방법:

### 1. FileZilla 사용

1. **FileZilla 다운로드**: https://filezilla-project.org/
2. **접속 정보 입력**:
   - 호스트: Cafe24에서 제공한 FTP 주소
   - 사용자명: FTP 계정
   - 비밀번호: FTP 비밀번호
   - 포트: 21
3. **프로젝트 파일 업로드**:
   - 로컬: `BH2025_WOWU` 폴더
   - 서버: `/home/사용자명/BH2025_WOWU`
4. **SSH로 접속하여 서비스 시작**

---

## 💰 비용 비교

| 항목 | Cafe24 서버호스팅 | Google Cloud Run |
|------|------------------|------------------|
| 월 기본료 | 33,000원~ | 무료 (일정량까지) |
| 트래픽 | 제한 있음 | 1GB 무료 |
| 자동 스케일링 | 불가 | 가능 |
| 서버 관리 | 직접 관리 필요 | 완전 자동 |
| 도메인 | Cafe24 도메인 사용 가능 | 별도 구매 필요 |
| 설정 난이도 | 중간 | 쉬움 |

---

## 🎯 추천 구성

### 소규모 운영 (학생 100명 이하)
- **Cafe24 서버호스팅 Basic** (월 33,000원)
- CPU: 2 Core
- RAM: 4GB
- 디스크: 50GB SSD

### 중규모 운영 (학생 300명 이하)
- **Cafe24 클라우드 서버** (월 55,000원)
- CPU: 4 Core
- RAM: 8GB
- 디스크: 100GB SSD

---

## 📚 참고 자료

- [Cafe24 호스팅 가이드](https://www.cafe24.com/)
- [FastAPI 배포 문서](https://fastapi.tiangolo.com/deployment/)
- [PM2 공식 문서](https://pm2.keymetrics.io/)
- [Nginx 설정 가이드](https://nginx.org/en/docs/)

---

## 🆘 지원

### Cafe24 고객센터
- 전화: 1544-6704
- 이메일: help@cafe24.com
- 평일 09:00 ~ 18:00

### 기술 지원이 필요한 경우
1. **서버 초기 설정**: Cafe24 관리자 도움 요청
2. **배포 관련**: 본 가이드의 명령어 순서대로 진행
3. **에러 발생 시**: 로그 파일 (`pm2 logs`) 확인 후 문의

---

**작성일**: 2025-11-14  
**버전**: 1.0  
**프로젝트**: 교육관리시스템 v3.3  
**대상**: Cafe24 서버호스팅/클라우드 서버
