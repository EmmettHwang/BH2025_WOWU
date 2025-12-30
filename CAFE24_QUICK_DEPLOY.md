# Cafe24 서버 긴급 배포 가이드

## 🚨 현재 상황
- 강사 권한에서 새 메뉴(문서 관리, 문제은행)가 보이지 않는 문제
- DB 마이그레이션 필요

## ⚡ Cafe24 서버에서 할 작업 (5분 소요)

### 1단계: 코드 업데이트
```bash
# SSH로 Cafe24 서버 접속 후

cd ~/public_html/wowu  # 프로젝트 경로로 이동
git pull origin hun    # 최신 코드 받기
```

### 2단계: DB 마이그레이션 실행

#### 방법 A: MySQL 명령줄 (추천)
```bash
# .env 파일에서 DB 정보 확인
cat .env | grep DB_

# 마이그레이션 실행
mysql -h [DB_HOST] -u [DB_USER] -p[DB_PASSWORD] [DB_NAME] < migrations/0003_add_menu_permissions.sql

# 결과 확인
mysql -h [DB_HOST] -u [DB_USER] -p[DB_PASSWORD] [DB_NAME] -e "SELECT code, name, menu_permissions FROM instructor_codes;"
```

#### 방법 B: phpMyAdmin
1. Cafe24 phpMyAdmin 접속
2. SQL 탭 클릭
3. `migrations/0003_add_menu_permissions.sql` 내용 복사/붙여넣기
4. 실행

### 3단계: 백엔드 재시작
```bash
# PM2로 재시작
pm2 restart wowu-backend

# 또는 전체 재시작
pm2 restart all

# 상태 확인
pm2 status
pm2 logs wowu-backend --lines 50
```

### 4단계: 테스트
1. 브라우저에서 Ctrl+F5 (하드 리프레시)
2. 로그아웃 후 재로그인
3. 강사 계정으로 확인:
   - 강의 메뉴 → "문서 관리 (RAG)" 보임
   - AI 메뉴 → "문제은행" 보임

## 📋 전체 명령어 복사용

```bash
# Cafe24 서버에서 실행할 전체 명령어

cd ~/public_html/wowu
git pull origin hun
mysql -h [DB_HOST] -u [DB_USER] -p[DB_PASSWORD] [DB_NAME] < migrations/0003_add_menu_permissions.sql
pm2 restart wowu-backend
pm2 logs wowu-backend --lines 50
```

## 🔧 트러블슈팅

### 문제: git pull 충돌
```bash
git stash          # 로컬 변경사항 임시 저장
git pull origin hun
git stash pop      # 로컬 변경사항 복원 (필요시)
```

### 문제: MySQL 접속 안됨
- Cafe24 호스팅 관리 콘솔에서 DB 접속 정보 재확인
- DB 호스트가 localhost가 아닐 수 있음

### 문제: PM2 명령어 안됨
```bash
# PM2가 없다면 설치
npm install -g pm2

# 또는 직접 실행
cd ~/public_html/wowu
python3 -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 &
```

### 문제: 마이그레이션 후에도 메뉴 안 보임
1. 브라우저에서 Ctrl+F5 (캐시 삭제)
2. 로그아웃 후 재로그인 (sessionStorage 갱신)
3. 개발자 도구 Console에서 확인:
   ```javascript
   fetch('/api/instructor-codes')
     .then(r => r.json())
     .then(d => console.log(d));
   ```

## 📚 상세 가이드
- `MENU_PERMISSION_FIX.md`: 상세한 문제 해결 가이드
- `DEPLOY_CAFE24.md`: 전체 Cafe24 배포 가이드

## 💡 향후 메뉴 추가 시
새 메뉴를 추가할 때는 **반드시** DB 마이그레이션도 함께 작성하세요!

체크리스트:
1. ✅ index.html: 메뉴 버튼에 `data-tab="menu-id"` 추가
2. ✅ app.js: showTab() switch case에 렌더링 함수 추가
3. ✅ migrations/xxxx.sql: instructor_codes.menu_permissions에 메뉴 ID 추가
4. ✅ MENU_PERMISSION_FIX.md: 메뉴 ID 목록 업데이트
