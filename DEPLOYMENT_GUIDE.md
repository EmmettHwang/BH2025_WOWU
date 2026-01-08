# 🚀 배포 및 테스트 가이드

## 📊 최근 커밋 정보
- **커밋**: `e38c6bc`
- **메시지**: fix: 로그인 예쁜 모달 표시 완전 수정 🎨
- **GitHub**: https://github.com/EmmettHwang/BH2025_WOWU/commit/e38c6bc

---

## 🔧 Cafe24 적용

```bash
cd ~/BH2025_WOWU
git pull origin main
pm2 restart backend-server
pm2 restart frontend-proxy

# 브라우저 캐시 클리어
# Ctrl + Shift + R
```

---

## ✅ 수정 완료된 부분

### 1) 로그인 시 예쁜 모달 표시
- ✅ 401/403 에러도 예쁜 모달로 표시
- ✅ 등록되지 않은 사용자 전용 스타일
- ✅ 대기/거절/승인/등록안됨 모두 상태별 모달

### 2) 프로필 사진 표시 개선
- ✅ /api/thumbnail 프록시 사용
- ✅ 신규수강생 처리 목록에서 표시
- ✅ 상세보기 모달에서 표시

---

## 🧪 테스트 방법

### 1) 로그인 모달 테스트

#### A. 등록되지 않은 사용자
1. https://kdt2025.com/login.html 접속
2. 존재하지 않는 이름 + 아무 비밀번호 입력
3. ✅ **회색 테마 모달 표시**
   - "등록되지 않은 사용자"
   - "입력하신 정보로 등록된 학생을 찾을 수 없습니다"
   - "신규 가입을 원하시면 회원가입 페이지를 이용해 주세요"

#### B. 대기 중 신청자
1. register.html에서 신청 완료
2. login.html에서 로그인 시도
3. ✅ **노란색 테마 모달 표시**
   - "신청 대기 중"
   - "담당자가 정해지면 연락 드리겠습니다"

#### C. 거절된 신청자
1. 관리자가 신청 거절
2. login.html에서 로그인 시도
3. ✅ **빨간색 테마 모달 표시**
   - "신청 거절됨"
   - "관리자에게 문의해 주세요"

### 2) 프로필 사진 테스트

#### A. 신규 신청 시 사진 업로드
1. https://kdt2025.com/register.html 접속
2. 사진 촬영/업로드
3. 브라우저 콘솔 확인:
   - ✅ "✅ FTP 업로드 성공: ftp://..."
   - ❌ "⚠️ FTP 업로드 실패, base64로 저장"
4. 신청 완료

#### B. 관리자 화면 확인
1. 학생 관리 → 신규수강생 처리
2. 목록에서 프로필 사진 확인
   - ✅ 썸네일 표시됨
   - ❌ 사진 안 보임 → FTP 업로드 실패
3. 상세보기 클릭 → 큰 프로필 사진 확인

---

## 🔍 프로필 사진 문제 진단

### 현재 상태
- ❌ FTP에 `student_profiles` 디렉토리 없음
- ❌ 사진 업로드 안 되고 있음

### 원인 가능성
1. **백엔드 서버 미실행** → FTP 업로드 안 됨
2. **API 엔드포인트 에러** → 업로드 실패
3. **FTP 연결 문제** → 업로드 실패

### 확인 방법
```bash
# Cafe24 서버에서 확인
pm2 logs backend-server --lines 100

# 신청 시도 후 로그 확인
# 예상 로그:
[OK] 파일 업로드 성공: ftp://bitnmeta2.synology.me/student_profiles/...
# 또는
[ERROR] 파일 업로드 실패: ...
```

---

## 📝 다음 단계

### 1) Cafe24에서 테스트
```bash
cd ~/BH2025_WOWU
git pull origin main
pm2 restart backend-server
pm2 restart frontend-proxy
pm2 logs backend-server
```

### 2) 신규 신청 테스트
- register.html에서 사진 포함 신청
- 브라우저 콘솔 확인 (F12)
- 서버 로그 확인 (pm2 logs)

### 3) 결과 확인
- FTP에 파일 업로드 확인
- 관리자 화면에서 프로필 사진 표시 확인

---

## 🎯 예상 결과

### 정상 동작 시
```
신청 → 사진 촬영 → /api/upload 호출 
→ FTP 업로드 성공 → URL 반환 
→ DB에 URL 저장 → 관리자 화면에서 표시 ✅
```

### 업로드 실패 시
```
신청 → 사진 촬영 → /api/upload 호출 
→ FTP 업로드 실패 → base64 폴백 
→ DB에 [BASE64_PENDING] 저장 → 승인 시 사진 없음 ⚠️
```

---

## 💡 문제 해결

### 프로필 사진이 안 보일 때
1. 브라우저 콘솔 확인 (F12)
2. 서버 로그 확인 (`pm2 logs backend-server`)
3. FTP 확인 (student_profiles 디렉토리 존재 여부)
4. /api/upload 엔드포인트 정상 작동 여부

### 로그인 모달이 안 뜰 때
1. 브라우저 캐시 클리어 (Ctrl + Shift + R)
2. 콘솔 에러 확인
3. 서버 재시작 (`pm2 restart backend-server`)

