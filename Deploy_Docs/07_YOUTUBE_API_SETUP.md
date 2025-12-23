# YouTube API 키 설정 가이드

## 📺 개요

KDT교육관리시스템에서 대시보드 배경음악(BGM) 재생을 위해 YouTube Data API v3를 사용합니다.

---

## 🎯 YouTube API가 필요한 이유

- **대시보드 BGM 재생**: 클래식, 피아노, 명상 음악 등 자동 재생
- **자동 검색**: 장르별로 YouTube에서 적합한 음악 검색
- **무료 사용 가능**: 일일 할당량 내에서 무료 사용

---

## 📋 Step 1: Google Cloud Console에서 API 키 발급

### 1-1. Google Cloud Console 접속
```
https://console.cloud.google.com/
```

- Google 계정으로 로그인
- 처음 사용하는 경우 약관 동의 필요

### 1-2. 프로젝트 생성

**새 프로젝트 만들기:**
1. 상단 프로젝트 선택 드롭다운 클릭
2. "새 프로젝트" 선택
3. 프로젝트 이름 입력 (예: `BH2025-WOWU`)
4. 조직 없음 (선택사항)
5. "만들기" 클릭

**기존 프로젝트 사용:**
- 이미 프로젝트가 있다면 선택하여 사용 가능

### 1-3. YouTube Data API v3 활성화

```
1. 왼쪽 메뉴 → "API 및 서비스" → "라이브러리"
2. 검색창에 "YouTube Data API v3" 입력
3. "YouTube Data API v3" 선택
4. "사용 설정" 버튼 클릭
```

### 1-4. API 키 생성

```
1. 왼쪽 메뉴 → "API 및 서비스" → "사용자 인증 정보"
2. 상단 "+ 사용자 인증 정보 만들기" 클릭
3. "API 키" 선택
4. API 키 자동 생성됨 (예: AIzaSyC9XYZ...)
5. "키 제한" 클릭하여 보안 설정 (권장)
```

### 1-5. API 키 제한 설정 (보안 강화)

**API 제한:**
```
1. 생성된 API 키 옆 편집(연필) 아이콘 클릭
2. "API 제한사항" 섹션
3. "키 제한" 선택
4. "YouTube Data API v3"만 체크
5. "저장" 클릭
```

**애플리케이션 제한 (선택사항):**
- HTTP 리퍼러: 특정 도메인만 허용
- IP 주소: 특정 서버 IP만 허용
- 개발 단계에서는 "없음" 선택 가능

---

## 📋 Step 2: 시스템에 API 키 등록

### 방법 A: 프론트엔드 시스템 설정 (추천)

#### 로컬 환경 (http://localhost:3000)

1. **로그인**
   ```
   아이디: admin
   비밀번호: kdt2025
   ```

2. **시스템 설정 메뉴**
   - 상단 네비게이션 → "⚙️ 시스템 설정" 클릭

3. **YouTube API 키 입력**
   - "YouTube API 키" 섹션 찾기
   - API 키 입력 (예: `AIzaSyC9XYZ...`)
   - "테스트" 버튼 클릭 (정상 작동 확인)
   - 하단 "💾 저장" 버튼 클릭

4. **BGM 장르 선택**
   - "백그라운드 뮤직 장르" 드롭다운
   - 원하는 장르 선택:
     - 클래식 (Classical Music)
     - 피아노 연주 (Piano Instrumental)
     - 명상 음악 (Meditation Music)
     - 고전 팝송 (Classic Pop)

#### 운영 서버 (Cafe24)

```bash
# SSH 접속
ssh root@your-server.com

# 브라우저에서 서버 IP로 접속
https://your-domain.com

# 동일한 방법으로 시스템 설정에서 등록
```

---

### 방법 B: 백엔드 .env 파일 (서버 전체 적용)

#### 로컬 환경

```bash
# .env 파일 수정
cd "G:\내 드라이브\11. DEV_23\51. Python_mp3등\BH2025_WOWU\backend"
notepad .env
```

**추가할 내용:**
```env
# YouTube API 설정
YOUTUBE_API_KEY=AIzaSyC9XYZ_your_actual_api_key_here
```

**백엔드 재시작:**
```bash
pm2 restart backend-server
```

#### 운영 서버

```bash
# SSH 접속
ssh root@your-server.com

# .env 파일 수정
cd /root/BH2025_WOWU/backend
nano .env

# 추가 (i 키로 편집 모드)
YOUTUBE_API_KEY=AIzaSyC9XYZ_your_actual_api_key_here

# 저장 (Ctrl+X, Y, Enter)

# 백엔드 재시작
pm2 restart backend-server
```

---

## 🧪 Step 3: API 키 테스트

### 프론트엔드에서 테스트

1. **시스템 설정** 페이지
2. YouTube API 키 입력 후 **"테스트"** 버튼 클릭
3. 성공 메시지 확인:
   ```
   ✅ API 키가 정상 작동합니다!
   ```

### BGM 재생 테스트

1. **대시보드** 이동
2. BGM이 자동 재생되는지 확인
3. 브라우저 콘솔 확인 (F12):
   ```
   ✅ YouTube BGM 로드 성공
   🎵 재생 중: [음악 제목]
   ```

---

## 📊 YouTube API 할당량 관리

### 무료 할당량

| 항목 | 할당량 |
|------|--------|
| **일일 할당량** | 10,000 단위 |
| **검색 1회** | 100 단위 |
| **비디오 정보** | 1 단위 |
| **하루 검색 가능 횟수** | 약 100회 |

### 할당량 확인

```
Google Cloud Console → API 및 서비스 → 할당량
```

### 할당량 초과 시

**증상:**
```
❌ YouTube API 오류: quotaExceeded
```

**해결책:**
1. **다음 날까지 대기** (자정 UTC 기준 초기화)
2. **할당량 증가 요청** (유료)
3. **임시 BGM 끄기**
   - 시스템 설정 → BGM 장르 → "BGM 끄기" 선택

---

## 🔧 문제 해결

### 문제 1: API 키 오류 (403 Forbidden)

**증상:**
```
❌ YouTube API 오류: 403 Forbidden
```

**원인:**
- YouTube Data API v3가 활성화되지 않음
- API 키 제한 설정 문제

**해결:**
```
1. Google Cloud Console 확인
2. YouTube Data API v3 활성화 여부 확인
3. API 키 제한 설정에서 YouTube Data API v3 허용 확인
```

### 문제 2: API 키 작동하지 않음

**증상:**
```
❌ YouTube API 키 테스트 실패
```

**해결:**
```bash
# 브라우저 콘솔(F12)에서 오류 확인
# API 키 다시 복사/붙여넣기 (공백 제거)
# 브라우저 캐시 삭제 (Ctrl+Shift+R)
```

### 문제 3: BGM이 재생되지 않음

**증상:**
- 장르 선택해도 음악 안 나옴

**해결:**
```
1. 시스템 설정에서 YouTube API 키 저장 확인
2. 브라우저 음소거 해제
3. BGM 볼륨 확인 (시스템 설정)
4. 브라우저 콘솔(F12)에서 오류 확인
```

### 문제 4: CORS 오류

**증상:**
```
Access to XMLHttpRequest has been blocked by CORS policy
```

**해결:**
- 정상적인 현상입니다 (YouTube iframe 사용으로 해결됨)
- 실제 재생에는 영향 없음

---

## 📋 체크리스트

### Google Cloud Console 설정

- [ ] Google Cloud Console 접속
- [ ] 프로젝트 생성 또는 선택
- [ ] YouTube Data API v3 활성화
- [ ] API 키 생성
- [ ] API 키 제한 설정 (보안)
- [ ] API 키 복사

### 시스템 등록

- [ ] 로그인 (admin / kdt2025)
- [ ] 시스템 설정 메뉴 접속
- [ ] YouTube API 키 입력
- [ ] API 키 테스트 성공
- [ ] 설정 저장
- [ ] BGM 장르 선택

### 동작 확인

- [ ] 대시보드 접속
- [ ] BGM 자동 재생 확인
- [ ] 볼륨 조절 가능 확인
- [ ] 브라우저 콘솔 오류 없음

---

## 💡 추가 팁

### BGM 볼륨 조절

```
시스템 설정 → BGM 볼륨 조절 → 슬라이더 (0-100%)
```

### BGM 끄기

```
시스템 설정 → 백그라운드 뮤직 장르 → "BGM 끄기" 선택
```

### 장르별 음악 예시

- **클래식**: 모차르트, 바흐, 베토벤 등
- **피아노**: 피아노 연주곡
- **명상**: 조용한 앰비언트 음악
- **고전 팝송**: 1960-1980년대 팝

---

## 🔗 참고 링크

| 항목 | URL |
|------|-----|
| Google Cloud Console | https://console.cloud.google.com/ |
| YouTube Data API v3 문서 | https://developers.google.com/youtube/v3 |
| API 키 관리 | https://console.cloud.google.com/apis/credentials |
| 할당량 확인 | https://console.cloud.google.com/apis/api/youtube.googleapis.com/quotas |

---

## 📞 지원

문제가 계속되면 다음을 확인해주세요:

1. **브라우저 콘솔** (F12) → 오류 메시지
2. **PM2 로그**
   ```bash
   pm2 logs backend-server --lines 50
   ```
3. **YouTube API 할당량** (Google Cloud Console)

---

**문서 작성일:** 2025-12-23  
**버전:** 1.0  
**대상 시스템:** KDT교육관리시스템 v3.2
