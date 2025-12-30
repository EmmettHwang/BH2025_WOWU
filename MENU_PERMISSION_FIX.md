# 메뉴 권한 문제 해결 가이드

## 문제 설명
새로 추가된 메뉴(문서 관리, 문제은행)가 강사 권한에서 보이지 않는 문제

## 원인
- `instructor_codes` 테이블의 `menu_permissions` JSON 배열에 새 메뉴가 추가되지 않음
- 프런트엔드의 `applyMenuPermissions()` 함수가 `menu_permissions` 배열에 있는 메뉴만 활성화

## 해결 방법

### 1. DB 마이그레이션 실행 (Cafe24 서버에서)

```bash
# Cafe24 서버 접속
cd ~/public_html/wowu  # 또는 프로젝트 경로

# MySQL 접속 정보 확인
cat .env | grep DB_

# MySQL 마이그레이션 실행
mysql -h [DB_HOST] -u [DB_USER] -p[DB_PASSWORD] [DB_NAME] < migrations/0003_add_menu_permissions.sql

# 또는 MySQL 클라이언트로 직접 실행
mysql -h [DB_HOST] -u [DB_USER] -p[DB_PASSWORD] [DB_NAME]
# 접속 후:
source migrations/0003_add_menu_permissions.sql;

# 확인
SELECT code, name, menu_permissions FROM instructor_codes;
```

### 2. 수동 실행 (phpMyAdmin 등)

```sql
-- 문서 관리 메뉴 추가
UPDATE instructor_codes
SET menu_permissions = JSON_ARRAY_APPEND(
    COALESCE(menu_permissions, JSON_ARRAY()),
    '$',
    'rag-documents'
)
WHERE code != 'IC-999' AND code != '0'
  AND (menu_permissions IS NULL OR NOT JSON_CONTAINS(menu_permissions, '"rag-documents"'));

-- 문제은행 메뉴 추가
UPDATE instructor_codes
SET menu_permissions = JSON_ARRAY_APPEND(
    COALESCE(menu_permissions, JSON_ARRAY()),
    '$',
    'exam-bank'
)
WHERE code != 'IC-999' AND code != '0'
  AND (menu_permissions IS NULL OR NOT JSON_CONTAINS(menu_permissions, '"exam-bank"'));

-- 확인
SELECT code, name, menu_permissions FROM instructor_codes;
```

### 3. 결과 확인

마이그레이션 후 `menu_permissions` 예시:
```json
[
  "dashboard",
  "students",
  "courses",
  "timetables",
  "training-logs",
  "rag-documents",
  "exam-bank"
]
```

### 4. 앱 재시작

```bash
# PM2로 재시작
pm2 restart wowu-backend

# 프론트엔드 새로고침
# 브라우저에서 Ctrl+F5 (하드 리프레시)
```

## 향후 메뉴 추가 시 체크리스트

새 메뉴를 추가할 때는 반드시:

1. **index.html**: 메뉴 버튼에 `data-tab="menu-id"` 추가
2. **app.js**: `showTab()` switch case에 렌더링 함수 추가
3. **DB 마이그레이션**: instructor_codes 테이블의 menu_permissions에 새 메뉴 ID 추가
4. **문서화**: 이 파일에 새 메뉴 추가 기록

## 현재 메뉴 ID 목록

### 시스템 관리
- `instructor-codes`: 강사코드/권한
- `instructors`: 강사 관리
- `system-settings`: 시스템 설정
- `db-backup`: DB 백업
- `notices`: 공지사항

### 과정
- `courses`: 교과목 관리
- `holidays`: 공휴일 관리
- `process-management`: 과정 관리

### 학생
- `students`: 학생 관리
- `counselings`: 상담 관리

### 강의
- `timetables`: 시간표 관리
- `training-logs`: 훈련일지 관리
- `rag-documents`: **문서 관리 (RAG)** ⭐ 새로 추가

### AI
- `ai-ssirn`: SSIRN 메모장
- `ai-record`: AI 생기부
- `ai-timetable`: AI 시간표
- `ai-training`: AI 훈련일지
- `ai-counseling`: AI 상담일지
- `exam-bank`: **문제은행** ⭐ 새로 추가
- `aesong-3d-chat`: 예진이 만나기

### 팀
- `teams`: 팀 관리
- `team-activity-logs`: 팀 활동일지

## 트러블슈팅

### 문제: 마이그레이션 후에도 메뉴가 보이지 않음

1. **브라우저 캐시 확인**
   ```
   Ctrl+F5로 하드 리프레시
   또는 개발자 도구 > Application > Clear storage
   ```

2. **sessionStorage 확인**
   ```javascript
   // 개발자 도구 Console에서
   console.log(JSON.parse(sessionStorage.getItem('instructor')));
   ```

3. **API 응답 확인**
   ```javascript
   // 개발자 도구 Console에서
   fetch('/api/instructor-codes')
     .then(r => r.json())
     .then(d => console.log(d));
   ```

4. **로그아웃 후 재로그인**
   - sessionStorage에 오래된 권한 정보가 캐시되어 있을 수 있음

### 문제: JSON_ARRAY_APPEND 함수 오류

MySQL 버전이 5.7 미만인 경우:
```sql
-- 대신 이렇게 수동으로 추가
UPDATE instructor_codes
SET menu_permissions = '["dashboard","students","courses","timetables","training-logs","rag-documents","exam-bank"]'
WHERE code = 'IC-001';
```

## 참고 파일
- `/frontend/app.js`: `applyMenuPermissions()` 함수 (14155번째 줄)
- `/migrations/0003_add_menu_permissions.sql`: 마이그레이션 스크립트
- `/frontend/index.html`: 메뉴 버튼 정의
