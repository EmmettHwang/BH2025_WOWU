# 🔄 코드 업데이트 워크플로우

이미 배포된 서버에 새로운 코드를 안전하게 업데이트하는 방법입니다.

---

## 📋 목차

1. [기본 업데이트 절차](#기본-업데이트-절차)
2. [Cafe24 서버 업데이트](#cafe24-서버-업데이트)
3. [로컬 환경 업데이트](#로컬-환경-업데이트)
4. [의존성 업데이트](#의존성-업데이트)
5. [데이터베이스 마이그레이션](#데이터베이스-마이그레이션)
6. [롤백 방법](#롤백-방법)
7. [배포 전 체크리스트](#배포-전-체크리스트)

---

## 🚀 기본 업데이트 절차

### 표준 워크플로우

```
1. 로컬에서 개발 및 테스트
   ↓
2. Git에 커밋 및 푸시
   ↓
3. 서버에서 git pull
   ↓
4. 의존성 업데이트 (필요시)
   ↓
5. 서버 재시작
   ↓
6. 동작 확인
```

---

## 🏢 Cafe24 서버 업데이트

### 전체 명령어 (복사 가능)

```bash
# 1. SSH 접속
ssh root@your-cafe24-server

# 2. 프로젝트 폴더로 이동
cd /root/BH2025_WOWU

# 3. 현재 상태 확인
git status
git log --oneline -5

# 4. 최신 코드 받기
git pull origin main

# 5. 의존성 업데이트 (필요시)
# Node.js 패키지
npm install

# Python 패키지
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# 6. PM2 재시작
pm2 restart all --update-env

# 7. 로그 확인
pm2 logs --lines 50

# 8. 상태 확인
pm2 status
curl http://localhost:8000
curl http://localhost:3000
```

### 단계별 상세 설명

#### Step 1: 백업 생성 (권장)

```bash
# 현재 커밋 해시 저장
git log -1 > /tmp/last_deploy.txt

# 데이터베이스 백업 (필요시)
mysqldump -h bitnmeta2.synology.me -P 3307 -u iyrc -p bh2025 > backup_$(date +%Y%m%d).sql
```

#### Step 2: 코드 업데이트

```bash
# 로컬 변경사항 확인
git status

# 변경사항이 있으면 stash
git stash

# 최신 코드 받기
git pull origin main

# stash 복원 (필요시)
git stash pop
```

#### Step 3: 의존성 체크

```bash
# package.json 변경 확인
git diff HEAD@{1} package.json

# requirements.txt 변경 확인
git diff HEAD@{1} backend/requirements.txt

# 변경사항이 있으면 설치
npm install
cd backend && source venv/bin/activate && pip install -r requirements.txt && deactivate && cd ..
```

#### Step 4: 서버 재시작

```bash
# 무중단 재시작 (권장)
pm2 reload all

# 일반 재시작
pm2 restart all

# 환경변수 업데이트와 함께
pm2 restart all --update-env
```

#### Step 5: 검증

```bash
# PM2 상태
pm2 status

# 로그 확인 (에러 없는지)
pm2 logs --nostream --lines 50

# API 테스트
curl http://localhost:8000/api/system-settings
curl http://localhost:3000

# 브라우저 테스트
# http://yourdomain.com
```

---

## 💻 로컬 환경 업데이트

### Windows (Conda)

```bash
# 1. 프로젝트 폴더로 이동
cd "G:\내 드라이브\11. DEV_23\51. Python_mp3등\BH2025_WOWU"

# 2. Conda 환경 활성화
conda activate bh2025

# 3. 최신 코드 받기
git pull origin main

# 4. 의존성 업데이트 (변경사항 있으면)
npm install
cd backend
pip install -r requirements.txt
cd ..

# 5. PM2 상태 확인
pm2 status

# 6a. 서버가 없으면 시작
pm2 start ecosystem.config.cjs

# 6b. 서버가 있으면 재시작
pm2 restart all

# 7. 브라우저에서 확인
# http://localhost:3000
```

### Mac/Linux

```bash
# 1. 프로젝트 폴더로 이동
cd ~/projects/BH2025_WOWU

# 2. 최신 코드 받기
git pull origin main

# 3. 의존성 업데이트
npm install
cd backend
source venv/bin/activate
pip install -r requirements.txt
deactivate
cd ..

# 4. 서버 재시작
pm2 restart all

# 5. 확인
pm2 status
pm2 logs --lines 20
```

---

## 📦 의존성 업데이트

### Node.js 패키지

```bash
# 일반 업데이트
npm install

# 특정 패키지 업데이트
npm update axios

# 취약점 수정
npm audit fix

# 메이저 버전 업데이트 (주의!)
npm update --latest

# package-lock.json 재생성
rm package-lock.json
npm install
```

### Python 패키지

```bash
cd backend
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate  # Windows

# 일반 업데이트
pip install -r requirements.txt

# 전체 패키지 업그레이드
pip install --upgrade -r requirements.txt

# 특정 패키지 업데이트
pip install --upgrade fastapi

# 의존성 확인
pip list --outdated

deactivate
cd ..
```

---

## 🗄️ 데이터베이스 마이그레이션

### 마이그레이션 파일 적용

```bash
# SQL 파일 실행
mysql -h bitnmeta2.synology.me -P 3307 -u iyrc -p bh2025 < migrations/add_column.sql

# 또는 MySQL 접속 후
mysql -h bitnmeta2.synology.me -P 3307 -u iyrc -p bh2025
SOURCE migrations/add_column.sql;
EXIT;
```

### 컬럼 추가 예시

```sql
-- migrations/add_new_column.sql
USE bh2025;

-- 컬럼 존재 여부 확인 후 추가
SET @col_exists = 0;
SELECT COUNT(*) INTO @col_exists 
FROM information_schema.columns 
WHERE table_schema = 'bh2025' 
  AND table_name = 'students' 
  AND column_name = 'new_column';

SET @query = IF(@col_exists = 0,
    'ALTER TABLE students ADD COLUMN new_column VARCHAR(255) DEFAULT NULL',
    'SELECT "Column already exists" AS message');

PREPARE stmt FROM @query;
EXECUTE stmt;
DEALLOCATE PREPARE stmt;
```

---

## ⏮️ 롤백 방법

### Git으로 이전 버전 복원

```bash
# 1. 커밋 히스토리 확인
git log --oneline -10

# 2. 특정 커밋으로 복원
git reset --hard [commit-hash]

# 또는 이전 커밋으로
git reset --hard HEAD~1

# 3. 강제 푸시 (주의!)
git push origin main --force

# 4. 서버 재시작
pm2 restart all
```

### 안전한 롤백 (추천)

```bash
# 1. 새 브랜치로 백업
git branch backup-$(date +%Y%m%d)

# 2. 이전 커밋 체크아웃
git checkout [commit-hash]

# 3. 테스트 후 문제없으면
git checkout main
git reset --hard [commit-hash]

# 4. 서버 재시작
pm2 restart all
```

### PM2 롤백

```bash
# 이전 저장 상태로 복원
pm2 resurrect

# 특정 시점 저장 (배포 전)
pm2 save

# 복원
pm2 resurrect
```

---

## ✅ 배포 전 체크리스트

### 로컬 테스트

- [ ] 로컬에서 정상 동작 확인
- [ ] 모든 기능 테스트
- [ ] 에러 로그 없음 확인
- [ ] 브라우저 콘솔 에러 없음
- [ ] 파일 업로드/다운로드 테스트
- [ ] 데이터베이스 연동 확인

### Git 관리

- [ ] 의미있는 커밋 메시지
- [ ] 커밋 단위 적절히 분리
- [ ] main 브랜치에 푸시
- [ ] GitHub에서 코드 리뷰

### 서버 배포 전

- [ ] 백업 생성 (코드, DB)
- [ ] 현재 커밋 해시 기록
- [ ] 의존성 변경사항 확인
- [ ] 마이그레이션 파일 준비
- [ ] 배포 시간 공지 (다운타임 발생 시)

### 서버 배포 중

- [ ] git pull 성공
- [ ] 의존성 설치 완료
- [ ] 마이그레이션 실행 (필요시)
- [ ] pm2 restart 성공
- [ ] pm2 status online 확인
- [ ] 로그에 에러 없음

### 배포 후 확인

- [ ] 웹사이트 접속 확인
- [ ] 로그인 기능 테스트
- [ ] 주요 기능 동작 확인
- [ ] 파일 업로드 테스트
- [ ] API 응답 정상
- [ ] 성능 이슈 없음
- [ ] 모니터링 확인 (CPU, 메모리)

---

## 🔥 긴급 핫픽스 절차

### 긴급 수정이 필요한 경우

```bash
# 1. 로컬에서 빠르게 수정
git add .
git commit -m "hotfix: Fix critical bug"
git push origin main

# 2. 서버에 즉시 적용
ssh root@server
cd /root/BH2025_WOWU
git pull origin main
pm2 restart all --update-env

# 3. 즉시 확인
pm2 logs --lines 20
curl http://localhost:8000
```

### 서비스 중단 최소화

```bash
# 무중단 재시작 (클러스터 모드)
pm2 reload all

# 또는 개별 재시작
pm2 reload backend-server
pm2 reload frontend-server
```

---

## 📊 배포 이력 관리

### 배포 기록

```bash
# 배포 로그 파일 생성
cat >> /root/deployment_log.txt << EOF
Date: $(date)
Commit: $(git log -1 --oneline)
User: $(whoami)
Status: Success
---
