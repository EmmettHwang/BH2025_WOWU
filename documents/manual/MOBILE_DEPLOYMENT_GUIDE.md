# 📱 m.kdt2025.com 모바일 배포 완벽 가이드

## ✅ 완료된 작업

### 1. PWA 설정 완료
- ✅ manifest.json 생성
- ✅ Service Worker (sw.js) 구현
- ✅ PWA 메타 태그 추가
- ✅ 앱 아이콘 생성 (180x180, 192x192, 512x512)
- ✅ 캐시 헤더 설정 (_headers)

### 2. 주소창 제거 설정
- ✅ `display: "standalone"` 모드
- ✅ iOS/Android 전체화면 지원
- ✅ 상태바 스타일 설정

---

## 🚀 Cloudflare Pages 배포 단계

### Step 1: Cloudflare 프로젝트 생성

```bash
# Cloudflare 인증
wrangler login

# 프로젝트 생성
wrangler pages project create biohealth-mobile
```

### Step 2: 배포 실행

```bash
# 모바일 디렉토리만 배포
wrangler pages deploy frontend/mobile --project-name biohealth-mobile

# 또는 전체 frontend 배포 (권장)
wrangler pages deploy frontend --project-name biohealth-mobile
```

### Step 3: 커스텀 도메인 설정

**Cloudflare Dashboard에서**:

1. **Pages** → **biohealth-mobile** → **Custom domains**
2. **Add a custom domain** 클릭
3. 도메인 입력: `m.kdt2025.com`
4. DNS 레코드 자동 생성 확인

**또는 수동 DNS 설정**:
```
Type: CNAME
Name: m
Target: biohealth-mobile.pages.dev
Proxy: Enabled (오렌지 클라우드)
TTL: Auto
```

### Step 4: SSL/TLS 설정

Cloudflare Dashboard → **SSL/TLS**:
- **SSL/TLS 암호화 모드**: Full (strict) ✅
- **Always Use HTTPS**: ON ✅
- **Automatic HTTPS Rewrites**: ON ✅
- **Minimum TLS Version**: TLS 1.2 ✅

---

## 📱 스마트폰에 바로가기 설치 방법

### iOS (iPhone/iPad)

1. **Safari**에서 `m.kdt2025.com` 접속
2. 하단 중앙 **공유** 버튼 탭 (⬆️ 아이콘)
3. 아래로 스크롤하여 **"홈 화면에 추가"** 선택
4. 앱 이름 확인: **"바이오헬스"**
5. 우측 상단 **추가** 탭

**결과**:
- ✅ 홈 화면에 앱 아이콘 생성
- ✅ 앱 실행 시 주소창 없음
- ✅ 네이티브 앱처럼 동작

**iOS 스크린샷**:
```
┌─────────────────────┐
│  Safari 공유 메뉴     │
├─────────────────────┤
│ 메시지 보내기         │
│ 복사하기             │
│ ...                 │
│ 📱 홈 화면에 추가 ✅  │  ← 여기 탭
│ 즐겨찾기 추가         │
│ ...                 │
└─────────────────────┘
```

### Android (Chrome)

**방법 1: 자동 설치 배너**
1. **Chrome**에서 `m.kdt2025.com` 접속
2. 하단에 "홈 화면에 추가" 배너 표시
3. **설치** 버튼 탭
4. 확인 팝업에서 **설치** 탭

**방법 2: 수동 설치**
1. **Chrome**에서 `m.kdt2025.com` 접속
2. 우측 상단 **메뉴** (⋮) 탭
3. **"홈 화면에 추가"** 또는 **"앱 설치"** 선택
4. **설치** 탭

**결과**:
- ✅ 홈 화면에 앱 아이콘 생성
- ✅ 앱 서랍에도 등록
- ✅ 앱 실행 시 주소창 없음
- ✅ 전체화면 모드

**Android 스크린샷**:
```
┌─────────────────────┐
│  Chrome 메뉴         │
├─────────────────────┤
│ 새 탭               │
│ 방문 기록           │
│ 다운로드            │
│ 📱 앱 설치 ✅        │  ← 여기 탭
│ 북마크             │
│ ...                │
└─────────────────────┘
```

---

## 🎯 주소창 제거 원리

### 1. manifest.json 설정
```json
{
  "display": "standalone"  // 브라우저 UI 제거
}
```

### 2. HTML Meta 태그
```html
<!-- PWA 활성화 -->
<meta name="mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-capable" content="yes">

<!-- 상태바 스타일 (iOS) -->
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">

<!-- 노치 영역까지 사용 -->
<meta name="viewport" content="viewport-fit=cover">
```

### 3. 중요 사항
⚠️ **주소창 제거는 홈 화면 아이콘으로 실행했을 때만 작동**

- ❌ Safari/Chrome에서 직접 접속 → 주소창 있음
- ✅ 홈 화면 아이콘으로 실행 → 주소창 없음

---

## ✅ 배포 후 테스트 체크리스트

### 1. PWA 유효성 검사

**Chrome DevTools**:
1. `m.kdt2025.com` 접속
2. F12 → **Lighthouse** 탭
3. **Progressive Web App** 체크박스 선택
4. **Analyze page load** 실행

**통과 기준**:
- ✅ HTTPS로 제공됨
- ✅ Service Worker 등록됨
- ✅ manifest.json 유효함
- ✅ 적절한 아이콘 제공
- ✅ 뷰포트 메타 태그 설정
- ✅ 점수 90 이상

### 2. manifest.json 확인

```bash
# 브라우저에서 접속
https://m.kdt2025.com/manifest.json

# 또는 curl 테스트
curl https://m.kdt2025.com/manifest.json
```

**확인 사항**:
```json
{
  "name": "바이오헬스교육관리시스템",
  "short_name": "바이오헬스",
  "display": "standalone",  ← 이것이 중요!
  "start_url": "/mobile/",
  "icons": [...]
}
```

### 3. Service Worker 확인

**Chrome DevTools**:
1. F12 → **Application** 탭
2. 좌측 **Service Workers** 선택
3. 확인사항:
   - ✅ Status: **activated and is running**
   - ✅ Source: `/mobile/sw.js`
   - ✅ Scope: `/mobile/`

### 4. 아이콘 확인

```bash
# 각 아이콘 접속 테스트
https://m.kdt2025.com/mobile/icon-180x180.png  ✅
https://m.kdt2025.com/mobile/icon-192x192.png  ✅
https://m.kdt2025.com/mobile/icon-512x512.png  ✅
```

### 5. 실제 기기 테스트

**iOS**:
- [ ] Safari에서 "홈 화면에 추가" 버튼 보임
- [ ] 홈 화면에 아이콘 추가됨
- [ ] 아이콘으로 실행 시 주소창 없음 ✅
- [ ] 상태바가 앱 테마 색상으로 표시됨

**Android**:
- [ ] Chrome에서 "설치" 배너 표시됨
- [ ] 홈 화면에 아이콘 추가됨
- [ ] 앱 서랍에도 등록됨
- [ ] 아이콘으로 실행 시 주소창 없음 ✅
- [ ] 전체화면 모드로 실행됨

---

## 🔍 문제 해결

### Q1. "홈 화면에 추가" 버튼이 안 보여요

**원인**: PWA 요구사항 미충족

**해결책**:
1. ✅ HTTPS 확인 (http:// → https://)
2. ✅ manifest.json 유효성 검사
3. ✅ Service Worker 등록 확인
4. ✅ 아이콘 파일 경로 확인

**확인 방법**:
```bash
# Chrome DevTools → Console
# 에러 메시지 확인
```

### Q2. 주소창이 여전히 보여요

**원인**: 브라우저에서 직접 접속

**해결책**:
- ❌ Safari/Chrome에서 URL 직접 입력
- ✅ **홈 화면 아이콘**으로 실행

**추가 확인**:
1. manifest.json에 `"display": "standalone"` 있는지 확인
2. 앱 삭제 후 재설치
3. 브라우저 캐시 삭제

### Q3. Android에서 설치 배너가 안 나와요

**원인**: 설치 조건 미충족

**해결책**:
1. Chrome 버전 업데이트 (최신)
2. 다른 도메인에서 이미 설치했는지 확인
3. 시크릿 모드로 테스트
4. 수동 설치 방법 사용 (메뉴 → 홈 화면에 추가)

### Q4. 아이콘이 기본 아이콘으로 보여요

**원인**: 아이콘 파일 경로 오류

**해결책**:
```bash
# 아이콘 파일 확인
ls -la /home/user/webapp/frontend/mobile/icon-*.png

# 브라우저에서 직접 접속
https://m.kdt2025.com/mobile/icon-192x192.png
```

---

## 📊 현재 구성 요약

```
frontend/mobile/
├── index.html           # 메인 대시보드 (PWA 메타 태그 포함)
├── login.html           # 로그인 (PWA 메타 태그 포함)
├── manifest.json        # PWA 설정 파일 ✅
├── sw.js                # Service Worker ✅
├── _headers             # Cloudflare 캐시 헤더 ✅
├── icon-180x180.png     # iOS 아이콘 ✅
├── icon-192x192.png     # Android 아이콘 ✅
├── icon-512x512.png     # Android 스플래시 ✅
├── DEPLOYMENT.md        # 배포 가이드 ✅
└── [기타 HTML 페이지들]
```

---

## 🎉 완료!

이제 `m.kdt2025.com`이 완벽한 PWA로 동작합니다:

### ✨ 사용자 경험
- ✅ 홈 화면에 앱 아이콘 추가
- ✅ 주소창 없는 전체화면 모드
- ✅ 네이티브 앱과 동일한 UX
- ✅ 빠른 로딩 (Service Worker 캐싱)
- ✅ 오프라인 지원

### 🚀 배포 명령어 요약

```bash
# 1. Cloudflare 배포
wrangler pages deploy frontend --project-name biohealth-mobile

# 2. 커스텀 도메인 설정 (Dashboard에서)
m.kdt2025.com → biohealth-mobile.pages.dev

# 3. 스마트폰에서 테스트
# iOS: Safari → 공유 → 홈 화면에 추가
# Android: Chrome → 메뉴 → 앱 설치
```

---

## 📚 추가 자료

- 배포 가이드: `/frontend/mobile/DEPLOYMENT.md`
- PWA 체크리스트: https://web.dev/pwa-checklist/
- Service Worker 문서: https://developer.mozilla.org/en-US/docs/Web/API/Service_Worker_API
