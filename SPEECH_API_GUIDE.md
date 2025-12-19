# 🎤 Web Speech API 사용 가이드

## 📋 개요

**speech 브랜치**에 브라우저 내장 Web Speech API를 사용한 음성 인식 기능이 추가되었습니다.

### ✨ 주요 특징

- ✅ **완전 무료**: 브라우저 내장 API (API 키 불필요)
- ✅ **서버 부하 없음**: 클라이언트에서 처리
- ✅ **간단한 사용법**: 함수 호출만으로 음성 인식
- ✅ **한국어 지원**: ko-KR 언어 설정
- ✅ **에러 처리**: 친절한 에러 메시지 제공

### ⚠️ 제약사항

- HTTPS 환경에서만 작동 (localhost 예외)
- Chrome, Edge, Safari 브라우저 권장 (Firefox 제한적)
- 인터넷 연결 필요 (Google 서버 사용)
- 한 번에 약 60초까지 인식 가능

---

## 🚀 빠른 시작

### 1. 브랜치 확인

```bash
cd /home/user/webapp
git checkout speech
```

### 2. 테스트 페이지 접속

```
https://your-domain.com/test-speech.html
```

### 3. 기본 사용법

```javascript
// 검색창에 음성 입력
voiceSearch('#search-input');

// 특정 입력 필드에 음성 입력
voiceInput('#student-name');

// 텍스트 영역에 음성 입력
voiceInput('#memo-textarea');
```

---

## 📚 API 레퍼런스

### startSpeechRecognition()

음성 인식을 시작합니다.

**구문:**
```javascript
startSpeechRecognition(onResult, onError, onStart, onEnd)
```

**파라미터:**
- `onResult(transcript, confidence)`: 인식 성공 시 호출
  - `transcript` (string): 인식된 텍스트
  - `confidence` (number): 신뢰도 (0.0 ~ 1.0)
- `onError(errorMessage)`: 에러 발생 시 호출
  - `errorMessage` (string): 에러 메시지
- `onStart()`: 인식 시작 시 호출
- `onEnd()`: 인식 종료 시 호출

**예시:**
```javascript
startSpeechRecognition(
    (transcript, confidence) => {
        console.log('인식 결과:', transcript);
        console.log('신뢰도:', confidence);
    },
    (error) => {
        console.error('오류:', error);
    },
    () => {
        console.log('시작됨');
    },
    () => {
        console.log('종료됨');
    }
);
```

---

### stopSpeechRecognition()

음성 인식을 중지합니다.

**구문:**
```javascript
stopSpeechRecognition()
```

**예시:**
```javascript
stopSpeechRecognition();
```

---

### voiceSearch()

검색창에 음성으로 입력합니다.

**구문:**
```javascript
voiceSearch(inputSelector)
```

**파라미터:**
- `inputSelector` (string): 검색 입력 필드의 CSS 셀렉터 (기본: `'#search-input'`)

**예시:**
```javascript
// 기본 검색창
voiceSearch();

// 특정 검색창
voiceSearch('#custom-search');
```

---

### voiceInput()

특정 입력 필드에 음성으로 입력합니다.

**구문:**
```javascript
voiceInput(fieldSelector)
```

**파라미터:**
- `fieldSelector` (string): 입력 필드의 CSS 셀렉터

**예시:**
```javascript
// 학생 이름 입력
voiceInput('#student-name');

// 메모 입력
voiceInput('#memo-textarea');

// 과정명 입력
voiceInput('#course-name');
```

---

## 💡 실전 예제

### 예제 1: 검색 기능에 음성 추가

```html
<div class="search-box">
    <input type="text" id="search-input" placeholder="검색...">
    <button onclick="voiceSearch('#search-input')">
        <i class="fas fa-microphone"></i>
    </button>
</div>
```

### 예제 2: 폼 입력에 음성 추가

```html
<form>
    <div class="form-group">
        <label>학생 이름</label>
        <div class="input-with-voice">
            <input type="text" id="student-name">
            <button type="button" onclick="voiceInput('#student-name')">
                🎤
            </button>
        </div>
    </div>
    
    <div class="form-group">
        <label>메모</label>
        <div class="input-with-voice">
            <textarea id="memo"></textarea>
            <button type="button" onclick="voiceInput('#memo')">
                🎤
            </button>
        </div>
    </div>
</form>
```

### 예제 3: 커스텀 음성 인식

```javascript
function customVoiceRecognition() {
    const inputField = document.querySelector('#custom-input');
    
    startSpeechRecognition(
        // 성공 시
        (transcript) => {
            inputField.value = transcript;
            alert(`인식 완료: ${transcript}`);
        },
        // 실패 시
        (error) => {
            alert(`오류 발생: ${error}`);
        },
        // 시작 시
        () => {
            inputField.classList.add('recording');
            inputField.placeholder = '🎤 듣고 있습니다...';
        },
        // 종료 시
        () => {
            inputField.classList.remove('recording');
            inputField.placeholder = '입력...';
        }
    );
}
```

---

## 🎨 UI/UX 권장사항

### 1. 시각적 피드백

```javascript
// 녹음 중 스타일
.recording {
    border: 2px solid red;
    animation: pulse 1s infinite;
}

@keyframes pulse {
    0%, 100% { opacity: 1; }
    50% { opacity: 0.5; }
}
```

### 2. 마이크 버튼 아이콘

```html
<!-- Font Awesome -->
<i class="fas fa-microphone"></i>

<!-- Emoji -->
🎤

<!-- Unicode -->
&#127908;
```

### 3. 사용자 안내 메시지

```javascript
// 권한 요청 전
"🎤 버튼을 클릭하고 마이크 권한을 허용해주세요."

// 녹음 중
"🎤 듣고 있습니다... 말씀해주세요."

// 성공 시
"✅ 인식 완료: [텍스트]"

// 실패 시
"❌ 음성이 감지되지 않았습니다. 다시 시도해주세요."
```

---

## 🔧 트러블슈팅

### 문제 1: "브라우저가 음성 인식을 지원하지 않습니다"

**원인:**
- Firefox 브라우저 사용
- 구형 브라우저 사용

**해결:**
- Chrome, Edge, Safari 사용
- 브라우저 최신 버전으로 업데이트

---

### 문제 2: "마이크 권한이 거부되었습니다"

**원인:**
- 사용자가 마이크 권한 거부
- 브라우저 설정에서 마이크 차단

**해결:**
1. 브라우저 주소창의 🔒 아이콘 클릭
2. "마이크" 권한을 "허용"으로 변경
3. 페이지 새로고침

---

### 문제 3: "음성이 감지되지 않았습니다"

**원인:**
- 마이크가 연결되지 않음
- 마이크 볼륨이 낮음
- 주변 소음이 많음

**해결:**
- 마이크 연결 확인
- 시스템 설정에서 마이크 볼륨 조정
- 조용한 환경에서 시도

---

### 문제 4: HTTP 환경에서 작동하지 않음

**원인:**
- HTTP 프로토콜 사용 (보안 제약)

**해결:**
- HTTPS로 배포
- 또는 localhost에서 테스트

---

## 📊 브라우저 호환성

| 브라우저 | 지원 여부 | 비고 |
|---------|----------|------|
| Chrome | ✅ 완벽 지원 | 권장 |
| Edge | ✅ 완벽 지원 | 권장 |
| Safari | ✅ 지원 | iOS/macOS |
| Firefox | ⚠️ 제한적 | 일부 기능 제한 |
| Opera | ✅ 지원 | Chrome 엔진 |
| IE | ❌ 미지원 | 사용 불가 |

---

## 🌐 배포 가이드

### Cafe24 서버 배포

```bash
# 1. SSH 접속
ssh root@kdt2025.com

# 2. 저장소 업데이트
cd /root/BH2025_WOWU
git fetch origin
git checkout speech
git pull origin speech

# 3. 프론트엔드 재시작
pm2 restart bhhs-frontend

# 4. 테스트
# https://kdt2025.com/test-speech.html 접속
```

### 샌드박스 테스트

```bash
# 1. 브랜치 변경
cd /home/user/webapp
git checkout speech

# 2. 프론트엔드 재시작
pm2 restart frontend-server

# 3. 테스트 URL
# https://3000-xxx.novita.ai/test-speech.html
```

---

## 📖 추가 리소스

### 공식 문서
- [MDN Web Speech API](https://developer.mozilla.org/en-US/docs/Web/API/Web_Speech_API)
- [W3C Speech API Specification](https://w3c.github.io/speech-api/)

### 관련 코드
- `frontend/app.js` (라인 16485~): Web Speech API 구현
- `frontend/test-speech.html`: 테스트 페이지

### 관련 커밋
- `feat: Web Speech API 음성 인식 기능 추가 (v2.0.69)`

---

## 🤝 기여 가이드

### 버그 리포트

이슈 발견 시:
1. 브라우저 및 버전 명시
2. 재현 단계 상세히 기술
3. 콘솔 에러 메시지 첨부

### 기능 제안

새로운 기능 제안 시:
1. 사용 사례 설명
2. 예상 동작 설명
3. UI/UX 목업 제공 (선택)

---

## 📝 변경 이력

### v2.0.69 (2025-12-02)
- ✨ Web Speech API 음성 인식 기능 추가
- ✨ `startSpeechRecognition()` 함수 구현
- ✨ `voiceSearch()` 함수 구현
- ✨ `voiceInput()` 함수 구현
- ✨ 테스트 페이지 `test-speech.html` 추가
- 📚 사용 가이드 문서 작성

---

## 📧 문의

기술 지원: BH2025 개발팀
브랜치: `speech`
버전: v2.0.69

**Happy Coding! 🎤✨**
