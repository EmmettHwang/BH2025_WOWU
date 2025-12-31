# 캐시 문제 해결 가이드

## 🔧 문제 증상
- 새로고침해도 대시보드가 업데이트되지 않음
- 차트가 사라지거나 이전 버전이 표시됨
- 무한 로딩 상태에 빠짐

## ✅ 해결 방법

### 1. 자동 해결 (권장)
브라우저를 새로고침하면 자동으로 캐시가 초기화됩니다.

**캐시 버전 시스템이 자동으로 작동:**
- 앱 버전: v1.1.0
- 오래된 캐시 자동 삭제
- 최신 코드 자동 로드

### 2. 수동 해결

#### 방법 A: 하드 리프레시
```
Windows/Linux: Ctrl + Shift + R
Mac: Cmd + Shift + R
```

#### 방법 B: 개발자 도구 사용
1. F12 키로 개발자 도구 열기
2. Console 탭에서 실행:
```javascript
clearCache(); 
location.reload();
```

#### 방법 C: 브라우저 캐시 전체 삭제
```
Windows/Linux: Ctrl + Shift + Delete
Mac: Cmd + Shift + Delete
```
→ "캐시된 이미지 및 파일" 선택 후 삭제

### 3. 에러 발생 시
화면에 에러 메시지가 표시되면:
- "캐시 삭제 후 새로고침" 버튼 클릭
- 또는 "새로고침" 버튼 클릭

## 📊 확인 방법

### 브라우저 콘솔에서 확인
F12 → Console 탭에서 다음 메시지를 확인:

```
✅ 정상 로딩:
🔄 캐시 버전 업데이트: null → 1.1.0
✅ 캐시 초기화 완료
🚀 대시보드 로딩 시작...
✅ 데이터 로딩 완료: { students: 24, instructors: 5, ... }
📊 차트 렌더링 시작...
✅ 대시보드 렌더링 완료

❌ 문제 발생:
❌ 대시보드 로드 실패: [에러 메시지]
```

## 🎯 예방 조치

### 개발자용
1. **버전 업데이트 시**:
   - `app.js`의 `CACHE_VERSION` 증가
   - `index.html`의 `app.js?v=X.X.X` 버전 증가

2. **캐시 무효화 확인**:
   ```javascript
   // app.js 상단
   const CACHE_VERSION = '1.1.0'; // 변경
   ```
   
   ```html
   <!-- index.html -->
   <script src="/app.js?v=1.1.0"></script>
   ```

### 사용자용
1. 문제 발생 시 **하드 리프레시** 사용
2. 주기적으로 **브라우저 캐시 삭제**
3. 에러 메시지 확인 후 **재시도 버튼** 클릭

## 🚀 현재 상태

### 적용된 개선사항
✅ 캐시 버전 관리 시스템 (v1.1.0)
✅ 브라우저 캐시 버스팅 (쿼리 스트링)
✅ 자동 캐시 초기화
✅ 상세한 에러 메시지
✅ 디버깅 로그 추가

### 테스트 URL
- **프론트엔드**: https://3000-i3oloko346uog7d7oo8v5-3844e1b6.sandbox.novita.ai
- **백엔드 API**: https://8000-i3oloko346uog7d7oo8v5-3844e1b6.sandbox.novita.ai/docs

## 📝 기술 세부사항

### 캐시 버전 시스템
```javascript
// 앱 로드 시 자동 실행
const CACHE_VERSION = '1.1.0';

(function checkCacheVersion() {
    const currentVersion = localStorage.getItem('cache_version');
    if (currentVersion !== CACHE_VERSION) {
        // 전체 캐시 삭제
        Object.keys(localStorage).forEach(k => {
            if (k.startsWith('cache_')) {
                localStorage.removeItem(k);
            }
        });
        localStorage.setItem('cache_version', CACHE_VERSION);
    }
})();
```

### 브라우저 캐시 버스팅
```html
<!-- 버전 쿼리 스트링 추가 -->
<script src="/app.js?v=1.1.0"></script>
```

파일이 변경되면 브라우저가 새 파일로 인식하여 자동 다운로드합니다.

## 🔍 트러블슈팅

### Q: 여전히 이전 버전이 보입니다
A: 
1. 브라우저를 완전히 닫고 다시 열기
2. 시크릿/프라이빗 모드에서 테스트
3. 다른 브라우저에서 테스트

### Q: 로딩이 무한 반복됩니다
A:
1. F12 → Console에서 에러 메시지 확인
2. Network 탭에서 실패한 요청 확인
3. 백엔드 서버 상태 확인

### Q: 차트가 표시되지 않습니다
A:
1. Chart.js CDN 로드 확인
2. Console에서 "📊 차트 렌더링 시작" 로그 확인
3. Canvas 요소 존재 확인

## 📞 지원

문제가 지속되면:
1. 브라우저 콘솔 스크린샷
2. Network 탭 스크린샷
3. 에러 메시지 전체 내용

위 정보와 함께 문의하세요.
