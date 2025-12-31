# 🚀 Cafe24 서버 배포 가이드

## 📋 사전 준비사항

### 1. 서버 환경
```bash
# Python 3.11+ 설치 확인
python3 --version

# PM2 설치 확인
pm2 --version

# Git 설치 확인
git --version
```

### 2. 필요한 패키지 설치 (없는 경우)
```bash
# Python3 가상환경
sudo apt install python3-venv python3-pip

# PM2 (Node.js 필요)
curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.0/install.sh | bash
nvm install 18
npm install -g pm2
```

---

## 🎯 빠른 배포 (자동 스크립트)

### 처음 배포하는 경우:
```bash
# 1. 저장소 클론 (처음 한 번만)
git clone https://github.com/EmmettHwang/BH2025_WOWU.git
cd BH2025_WOWU

# 2. 배포 스크립트 실행
./deploy.sh
```

### 이미 배포되어 있는 경우:
```bash
# 프로젝트 디렉토리로 이동
cd BH2025_WOWU

# 배포 스크립트 실행 (자동으로 pull + 재시작)
./deploy.sh
```

---

## 🔧 수동 배포 (단계별)

### 1. 코드 업데이트
```bash
git fetch origin hun
git pull origin hun
```

### 2. 가상환경 활성화
```bash
# 처음이면 생성
python3 -m venv venv

# 활성화
source venv/bin/activate
```

### 3. 패키지 설치
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### 4. PM2 재시작
```bash
# 기존 프로세스 재시작
pm2 restart bh2025-backend

# 또는 처음 시작
pm2 start ecosystem.config.js
pm2 save
```

---

## 📊 서비스 관리

### PM2 기본 명령어
```bash
# 상태 확인
pm2 status

# 실시간 로그 확인
pm2 logs bh2025-backend

# 최근 로그 확인 (100줄)
pm2 logs bh2025-backend --lines 100 --nostream

# 서비스 재시작
pm2 restart bh2025-backend

# 서비스 중지
pm2 stop bh2025-backend

# 서비스 시작
pm2 start bh2025-backend

# 서비스 삭제
pm2 delete bh2025-backend

# 메모리 사용량 모니터링
pm2 monit
```

### 로그 파일 위치
```bash
# 에러 로그
./logs/backend-error.log

# 출력 로그
./logs/backend-out.log

# 로그 직접 확인
tail -f ./logs/backend-out.log
tail -f ./logs/backend-error.log
```

---

## 🗄️ 데이터베이스 마이그레이션

### 새 테이블 생성 (문제은행)
```bash
# 로컬에서 접속
mysql -h bitnmeta2.synology.me -P 23306 -u BH2025 -pDBwjdqh!2025 BH2025

# SQL 파일 실행
mysql -h bitnmeta2.synology.me -P 23306 -u BH2025 -pDBwjdqh!2025 BH2025 < migrations/0002_exam_bank.sql
```

---

## 🔍 트러블슈팅

### 1. PM2 프로세스가 시작되지 않을 때
```bash
# 에러 로그 확인
pm2 logs bh2025-backend --err --lines 50

# 수동 실행으로 에러 확인
source venv/bin/activate
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### 2. 포트가 이미 사용 중일 때
```bash
# 포트 사용 확인
sudo lsof -i :8000

# 프로세스 종료
sudo kill -9 <PID>
```

### 3. Python 패키지 에러
```bash
# 가상환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. RAG 시스템 초기화 에러
```bash
# 벡터 DB 초기화
rm -rf /tmp/bh2025_vector_db
# 서비스 재시작
pm2 restart bh2025-backend
```

### 5. 메모리 부족
```bash
# ecosystem.config.js에서 max_memory_restart 조정
# 현재: 1G
# 필요시: 2G 또는 4G로 증가
```

---

## 🌐 Nginx 설정 (선택사항)

### Nginx 리버스 프록시 설정
```nginx
# /etc/nginx/sites-available/bh2025

server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_cache_bypass $http_upgrade;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 정적 파일 직접 서빙 (선택사항)
    location /static {
        alias /path/to/BH2025_WOWU/frontend;
    }
}
```

### Nginx 적용
```bash
# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/bh2025 /etc/nginx/sites-enabled/

# 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
```

---

## 🔐 보안 설정

### 1. 방화벽 설정
```bash
# UFW 사용 시
sudo ufw allow 8000/tcp
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

### 2. SSL 인증서 (Let's Encrypt)
```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 📈 성능 최적화

### 1. Uvicorn Workers 조정
```javascript
// ecosystem.config.js
args: 'backend.main:app --host 0.0.0.0 --port 8000 --workers 4'
// workers 수는 CPU 코어 수에 맞게 조정
```

### 2. PM2 Cluster 모드 (선택사항)
```javascript
// ecosystem.config.js
instances: 4,  // 또는 'max'
exec_mode: 'cluster'
```

---

## 📞 문제 발생 시

### 로그 확인 순서:
1. `pm2 logs bh2025-backend` - PM2 로그
2. `./logs/backend-error.log` - 에러 로그
3. `./logs/backend-out.log` - 출력 로그
4. 수동 실행으로 직접 확인

### 재배포 체크리스트:
- [ ] Git pull 완료
- [ ] requirements.txt 패키지 설치
- [ ] DB 마이그레이션 (필요시)
- [ ] PM2 재시작
- [ ] 서비스 상태 확인
- [ ] 로그 확인

---

## 🎉 배포 완료 확인

```bash
# 1. 서비스 상태
pm2 status

# 2. API 헬스체크
curl http://localhost:8000/

# 3. 로그 확인
pm2 logs bh2025-backend --lines 20 --nostream
```

---

**문제가 발생하면 로그를 확인하고, 필요시 수동 실행으로 디버깅하세요!** 🚀
