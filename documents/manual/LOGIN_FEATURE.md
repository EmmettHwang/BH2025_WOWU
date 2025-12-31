# 로그인 기능 구현 문서

## 📋 개요
교육관리시스템에 강사 인증 기반 로그인 기능이 추가되었습니다.

## ✨ 주요 기능

### 1. 로그인 시스템
- **강사 이름으로 로그인**: 기존 강사 테이블의 이름을 사용
- **기본 비밀번호**: `kdt2025` (모든 강사 공통)
- **세션 관리**: sessionStorage를 사용한 세션 유지
- **자동 리다이렉트**: 미인증 시 로그인 페이지로 자동 이동

### 2. 편의 기능

#### 아이디 저장 (Remember Username)
- 체크박스 체크 시 강사 이름을 localStorage에 저장
- 다음 로그인 시 자동으로 이름 입력란에 표시
- 저장 위치: `localStorage.instructor_name`

#### 자동 로그인 (Auto Login)
- 체크박스 체크 시 비밀번호까지 localStorage에 저장
- 다음 페이지 방문 시 자동으로 로그인 진행
- 저장 위치: `localStorage.instructor_password`
- **보안 참고**: 브라우저 로컬 스토리지에 평문 저장됨

### 3. 사용자 인터페이스

#### 로그인 페이지 (`/static/login.html`)
- 그라디언트 배경의 모던한 디자인
- 비밀번호 표시/숨김 토글 (눈 아이콘)
- 실시간 알림 메시지 (성공/실패/정보)
- 반응형 디자인 (모바일 최적화)

#### 메인 페이지 헤더
- 로그인한 강사 이름 표시
- 강사 유형(교수, 주강사 등) 표시
- 로그아웃 버튼

## 🔧 기술 구현

### 백엔드 API

#### POST `/api/auth/login`
```json
// 요청
{
  "name": "황동하",
  "password": "kdt2025"
}

// 응답 (성공)
{
  "success": true,
  "message": "황동하님, 환영합니다!",
  "instructor": {
    "code": "T-001",
    "name": "황동하",
    "instructor_type": "IC-001",
    "instructor_type_name": "교수",
    // ... 기타 강사 정보
  }
}

// 응답 (실패)
{
  "detail": "등록되지 않은 강사입니다"
}
```

#### POST `/api/auth/change-password`
```json
// 요청
{
  "instructor_code": "T-001",
  "old_password": "kdt2025",
  "new_password": "newpassword123"
}

// 응답
{
  "success": true,
  "message": "비밀번호가 변경되었습니다"
}
```

### 프론트엔드 구현

#### 로그인 체크 (app.js)
```javascript
function checkLogin() {
    const loggedIn = sessionStorage.getItem('logged_in');
    const instructor = sessionStorage.getItem('instructor');
    
    if (!loggedIn || !instructor) {
        window.location.href = '/static/login.html';
        return false;
    }
    return true;
}
```

#### 로그아웃
```javascript
function logout() {
    sessionStorage.removeItem('logged_in');
    sessionStorage.removeItem('instructor');
    window.location.href = '/static/login.html';
}
```

## 📊 데이터베이스 스키마

### instructors 테이블 업데이트
```sql
-- password 컬럼 추가 (없을 경우 자동 추가됨)
ALTER TABLE instructors 
ADD COLUMN password VARCHAR(100) DEFAULT 'kdt2025';
```

- 기존 강사들은 자동으로 기본 비밀번호(`kdt2025`) 적용
- 강사별로 비밀번호 변경 가능

## 🔐 보안 고려사항

### 현재 구현 (개발/내부용)
- ✅ 세션 기반 인증
- ✅ 평문 비밀번호 저장 (단순 시스템용)
- ✅ localStorage 기반 자동 로그인

### 프로덕션 배포 시 권장사항
1. **비밀번호 해싱**: bcrypt 등으로 암호화 저장
2. **JWT 토큰**: sessionStorage 대신 JWT 사용
3. **HTTPS**: 반드시 HTTPS 환경에서 운영
4. **세션 타임아웃**: 일정 시간 후 자동 로그아웃
5. **로그인 시도 제한**: Brute-force 공격 방지

## 🚀 사용 방법

### 1. 로그인
```
URL: http://localhost:3000/static/login.html
또는: http://your-domain.com/static/login.html

강사 이름: 황동하
비밀번호: kdt2025
```

### 2. 자동 로그인 설정
1. 로그인 페이지에서 "자동 로그인" 체크박스 선택
2. 로그인 성공
3. 다음 번 방문 시 자동으로 로그인됨

### 3. 비밀번호 변경 (API 호출)
```bash
curl -X POST http://localhost:8000/api/auth/change-password \
  -H "Content-Type: application/json" \
  -d '{
    "instructor_code": "T-001",
    "old_password": "kdt2025",
    "new_password": "mynewpassword"
  }'
```

## 📝 테스트 시나리오

### 시나리오 1: 첫 로그인
1. 메인 페이지 접속 → 로그인 페이지로 리다이렉트
2. 강사 이름 입력: `황동하`
3. 비밀번호 입력: `kdt2025`
4. 로그인 버튼 클릭
5. 메인 페이지로 이동 → 우측 상단에 강사 이름 표시

### 시나리오 2: 아이디 저장
1. 로그인 페이지에서 "아이디 저장" 체크
2. 로그인 성공
3. 로그아웃
4. 로그인 페이지 재방문 → 강사 이름 자동 입력됨

### 시나리오 3: 자동 로그인
1. 로그인 페이지에서 "자동 로그인" 체크
2. 로그인 성공
3. 브라우저 닫기
4. 메인 페이지 재방문 → 자동으로 로그인 진행

### 시나리오 4: 로그아웃
1. 메인 페이지 우측 상단 "로그아웃" 버튼 클릭
2. 확인 대화상자에서 "확인" 클릭
3. 로그인 페이지로 이동

## 🐛 트러블슈팅

### 문제 1: "등록되지 않은 강사입니다" 오류
**원인**: 입력한 이름이 instructors 테이블에 없음  
**해결**: 정확한 강사 이름 입력 또는 강사 추가

### 문제 2: "비밀번호가 일치하지 않습니다" 오류
**원인**: 잘못된 비밀번호 입력  
**해결**: 기본 비밀번호 `kdt2025` 입력 또는 변경된 비밀번호 확인

### 문제 3: 자동 로그인이 작동하지 않음
**원인**: localStorage가 비활성화되었거나 데이터가 삭제됨  
**해결**: 브라우저 설정에서 localStorage 활성화 확인

### 문제 4: 메인 페이지가 계속 로그인 페이지로 리다이렉트됨
**원인**: sessionStorage가 초기화됨 (탭 닫기 등)  
**해결**: 다시 로그인하거나 자동 로그인 체크박스 사용

## 📈 향후 개선 계획

1. **권한 관리**: 강사 유형별 접근 권한 설정
2. **비밀번호 재설정**: 이메일을 통한 비밀번호 복구
3. **다중 인증**: 2FA (Two-Factor Authentication)
4. **로그인 기록**: 접속 시간, IP 주소 기록
5. **세션 타임아웃**: 30분 미활동 시 자동 로그아웃
6. **비밀번호 정책**: 길이, 복잡도 요구사항

## 🔗 관련 파일

### 백엔드
- `backend/main.py` - 로그인/인증 API 구현

### 프론트엔드
- `frontend/login.html` - 로그인 페이지
- `frontend/index.html` - 메인 페이지 (헤더 수정)
- `frontend/app.js` - 로그인 체크 및 로그아웃 로직

## 📞 지원

문제가 발생하면:
1. 백엔드 로그 확인: `pm2 logs bhhs-backend`
2. 브라우저 콘솔 확인 (F12)
3. API 테스트: `curl http://localhost:8000/api/auth/login`

---

**작성일**: 2025-11-15  
**버전**: 1.0  
**브랜치**: login  
**작성자**: Claude Code Assistant
