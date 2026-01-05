# Cafe24 리눅스 서버 배포 가이드

## 📋 목차

1. [사전 준비](#사전-준비)
2. [서버 접속](#서버-접속)
3. [프로젝트 배포](#프로젝트-배포)
4. [환경 설정](#환경-설정)
5. [서버 시작](#서버-시작)
6. [문제 해결](#문제-해결)
7. [유지보수](#유지보수)

---

## 사전 준비

### 1. Cafe24 호스팅 요구사항

- **상품**: 리눅스 웹호스팅 (Python 지원)
- **Python 버전**: 3.9 이상
- **디스크 용량**: 최소 5GB 이상 권장
- **메모리**: 최소 2GB 이상 권장

### 2. 필요한 정보 준비

- [ ] Cafe24 SSH 접속 정보 (호스트, 포트, 사용자명, 비밀번호)
- [ ] MySQL 데이터베이스 정보 (호스트, 포트, DB명, 사용자명, 비밀번호)
- [ ] FTP 정보 (호스트, 포트, 사용자명, 비밀번호)
- [ ] GROQ API 키 (필수 - RAG 시스템용)
- [ ] 기타 AI API 키 (선택 - OpenAI, Gemini, Anthropic)

---

## 서버 접속

### SSH 접속

```bash
ssh -p [포트번호] [사용자명]@[호스트]
```

**예시**:
```bash
ssh -p 22022 cafe24user@yourserver.cafe24.com
```

---

## 프로젝트 배포

### 방법 1: Git Clone (권장)

```bash
# 1. 홈 디렉토리로 이동
cd ~

# 2. Git 저장소 클론
git clone https://github.com/EmmettHwang/BH2025_WOWU.git

# 3. 프로젝트 디렉토리로 이동
cd BH2025_WOWU

# 4. hun 브랜치로 전환
git checkout hun
```

### 방법 2: FTP 업로드

1. FileZilla 등 FTP 클라이언트 사용
2. 전체 프로젝트 폴더를 서버에 업로드
3. SSH로 접속하여 압축 해제 (필요 시)

---

## 환경 설정

### 1. 셋업 스크립트 실행

```bash
cd ~/BH2025_WOWU
bash setup.sh
```

이 스크립트는 자동으로:
- Python 가상환경 생성
- 필수 패키지 설치
- 필요한 디렉토리 생성

### 2. 환경 변수 설정

```bash
# .env 파일 생성
cp backend/.env.example backend/.env

# 편집기로 열기
nano backend/.env
```

**반드시 설정해야 할 항목**:

```bash
# 데이터베이스
DB_HOST=your_mysql_host
DB_PORT=3306
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=BH2025

# API 키 (RAG 시스템 필수)
GROQ_API_KEY=your_groq_api_key_here
```

**저장 및 종료**:
- `Ctrl + O` (저장)
- `Enter`
- `Ctrl + X` (종료)

---

## 서버 시작

### 기본 시작

```bash
bash start.sh
```

### 커스텀 설정으로 시작

```bash
# 포트 변경
bash start.sh --port 8080

# 워커 수 변경
bash start.sh --workers 2

# 개발 모드 (코드 변경 시 자동 재시작)
bash start.sh --reload
```

### 백그라운드 실행

```bash
nohup bash start.sh > server.log 2>&1 &
```

**로그 확인**:
```bash
tail -f server.log
```

---

## 문제 해결

### 1. Python 버전 문제

**증상**: `Python 3.9 이상 필요`

**해결**:
```bash
# Python 버전 확인
python3 --version

# Cafe24에서 Python 버전 변경 (호스팅 관리자에 문의)
```

### 2. 패키지 설치 오류

**증상**: `ModuleNotFoundError`, `ImportError`

**해결**:
```bash
cd ~/BH2025_WOWU
source venv/bin/activate
cd backend
pip install -r requirements.txt --upgrade
```

### 3. 포트 충돌

**증상**: `Address already in use`

**해결**:
```bash
# 실행 중인 프로세스 확인
ps aux | grep uvicorn

# 프로세스 종료
bash stop.sh

# 또는 다른 포트 사용
bash start.sh --port 8001
```

### 4. 메모리 부족

**증상**: 서버가 자주 멈추거나 느림

**해결**:
```bash
# 워커 수 줄이기
bash start.sh --workers 2

# 또는
bash start.sh --workers 1
```

### 5. 데이터베이스 연결 오류

**증상**: `Can't connect to MySQL server`

**해결**:
1. `.env` 파일의 DB 정보 확인
2. MySQL 서버 실행 상태 확인
3. 방화벽 설정 확인
4. Cafe24 관리자 페이지에서 DB 접근 권한 확인

### 6. RAG 시스템 초기화 실패

**증상**: `RAG 시스템 초기화 실패`

**해결**:
```bash
# 필수 패키지 재설치
source venv/bin/activate
pip install sentence-transformers==2.3.1 huggingface-hub==0.20.3 faiss-cpu==1.7.4

# 디렉토리 권한 확인
chmod 755 backend/vector_db
```

---

## 유지보수

### 서버 상태 확인

```bash
# 프로세스 확인
ps aux | grep uvicorn

# 리소스 사용량 확인
top

# 디스크 사용량 확인
df -h

# 로그 확인
tail -f backend/logs/server.log
```

### 서버 재시작

```bash
bash stop.sh
bash start.sh
```

### 코드 업데이트

```bash
cd ~/BH2025_WOWU
git pull origin hun
bash stop.sh
source venv/bin/activate
cd backend
pip install -r requirements.txt --upgrade
cd ..
bash start.sh
```

### 백업

#### 데이터베이스 백업

```bash
mysqldump -h DB_HOST -u DB_USER -p DB_NAME > backup_$(date +%Y%m%d).sql
```

#### 문서/파일 백업

```bash
cd ~/BH2025_WOWU/backend
tar -czf documents_backup_$(date +%Y%m%d).tar.gz documents/
tar -czf vector_db_backup_$(date +%Y%m%d).tar.gz vector_db/
```

### 로그 관리

```bash
# 로그 파일 크기 확인
du -sh backend/logs/*

# 오래된 로그 삭제 (30일 이상)
find backend/logs/ -name "*.log" -mtime +30 -delete
```

---

## 자동 시작 설정 (systemd)

### 1. 서비스 파일 생성

```bash
sudo nano /etc/systemd/system/bh2025.service
```

**내용**:
```ini
[Unit]
Description=BH2025 WOWU Backend Server
After=network.target mysql.service

[Service]
Type=simple
User=your_username
WorkingDirectory=/home/your_username/BH2025_WOWU
ExecStart=/home/your_username/BH2025_WOWU/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

### 2. 서비스 활성화

```bash
# 서비스 리로드
sudo systemctl daemon-reload

# 서비스 시작
sudo systemctl start bh2025

# 자동 시작 활성화
sudo systemctl enable bh2025

# 상태 확인
sudo systemctl status bh2025
```

---

## Nginx 리버스 프록시 설정 (선택)

### 1. Nginx 설치

```bash
sudo apt update
sudo apt install nginx
```

### 2. 설정 파일 생성

```bash
sudo nano /etc/nginx/sites-available/bh2025
```

**내용**:
```nginx
server {
    listen 80;
    server_name yourdomain.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /home/your_username/BH2025_WOWU/frontend;
    }
}
```

### 3. 활성화

```bash
sudo ln -s /etc/nginx/sites-available/bh2025 /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## 보안 권장사항

### 1. 방화벽 설정

```bash
# UFW 활성화
sudo ufw enable

# SSH 포트 허용
sudo ufw allow 22/tcp

# HTTP/HTTPS 허용
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 애플리케이션 포트 (필요 시)
sudo ufw allow 8000/tcp
```

### 2. 파일 권한 설정

```bash
cd ~/BH2025_WOWU

# 스크립트 실행 권한
chmod +x setup.sh start.sh stop.sh

# .env 파일 보호
chmod 600 backend/.env

# 디렉토리 권한
chmod 755 backend/documents backend/uploads backend/vector_db
```

### 3. 정기 업데이트

```bash
# 매주 월요일 새벽 3시에 업데이트 (crontab)
0 3 * * 1 cd ~/BH2025_WOWU && git pull && bash stop.sh && bash start.sh
```

---

## 성능 최적화

### 1. 워커 수 설정

CPU 코어 수의 2배 + 1 권장:
```bash
# CPU 코어 수 확인
nproc

# 4코어면 워커 9개 권장
bash start.sh --workers 9
```

### 2. 메모리 최적화

```bash
# 메모리 사용량 모니터링
watch -n 5 free -m

# 필요 시 swap 증설 (Cafe24 관리자 문의)
```

---

## 체크리스트

### 배포 전

- [ ] SSH 접속 정보 확인
- [ ] 데이터베이스 준비
- [ ] API 키 준비
- [ ] 도메인/서버 확인

### 배포 중

- [ ] 프로젝트 업로드/클론
- [ ] setup.sh 실행
- [ ] .env 파일 설정
- [ ] 서버 시작 테스트

### 배포 후

- [ ] 브라우저에서 접속 테스트
- [ ] API 문서 확인 (/docs)
- [ ] 로그인 테스트
- [ ] RAG 시스템 테스트
- [ ] 백업 설정

---

## 지원 및 문의

- **GitHub**: https://github.com/EmmettHwang/BH2025_WOWU
- **이슈 트래커**: https://github.com/EmmettHwang/BH2025_WOWU/issues

---

*최종 수정: 2026-01-05*
