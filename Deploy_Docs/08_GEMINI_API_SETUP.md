# 🤖 Gemini API 키 설정 가이드

## 📋 개요

KDT교육관리시스템에서 AI 생기부 작성, AI 챗봇 등에 **Google Gemini API**를 사용합니다.

---

## 🎯 Gemini API vs OpenAI API

| 항목 | Gemini API | OpenAI API |
|------|------------|------------|
| **제공사** | Google | OpenAI |
| **무료 할당량** | ✅ 있음 (일일 1,500건) | ❌ 없음 (유료만) |
| **비용** | 무료 ~ $7/1M tokens | $0.50 ~ $10/1M tokens |
| **모델** | Gemini 2.0 Flash | GPT-4o, GPT-3.5 |
| **성능** | 빠름 | 매우 빠름 |
| **한국어 지원** | ✅ 우수 | ✅ 우수 |
| **추천** | ⭐ 무료 사용 | 고성능 필요 시 |

---

## 📋 Step 1: Google Cloud Console에서 API 키 발급

### 1-1. Google Cloud Console 접속

```
https://console.cloud.google.com/
```

- Google 계정으로 로그인
- 처음 사용하는 경우 약관 동의

### 1-2. 프로젝트 생성 (YouTube API와 동일 프로젝트 가능)

**새 프로젝트 만들기:**
1. 상단 프로젝트 선택 드롭다운 클릭
2. "새 프로젝트" 선택
3. 프로젝트 이름 입력 (예: `BH2025-WOWU`)
4. "만들기" 클릭

**기존 프로젝트 사용:**
- YouTube API를 이미 설정했다면 동일 프로젝트 사용 가능

### 1-3. Gemini API (Generative Language API) 활성화

```
1. 왼쪽 메뉴 → "API 및 서비스" → "라이브러리"
2. 검색창에 "Generative Language API" 입력
3. "Generative Language API" 선택
4. "사용 설정" 버튼 클릭
```

또는 직접 링크:
```
https://console.cloud.google.com/apis/library/generativelanguage.googleapis.com
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
4. "Generative Language API" 체크
5. "저장" 클릭
```

---

## 📋 Step 2: 시스템에 API 키 저장

### 방법: 백엔드 .env 파일

#### **로컬 환경:**

```bash
# backend/.env 파일 수정
cd "G:\내 드라이브\11. DEV_23\51. Python_mp3등\BH2025_WOWU\backend"
notepad .env
```

**추가할 내용:**
```env
# Google Gemini API 설정 (AI 생기부/챗봇용)
GOOGLE_CLOUD_TTS_API_KEY=AIzaSyC9XYZ_your_gemini_api_key_here
```

**⚠️ 중요:** 환경변수 이름이 `GOOGLE_CLOUD_TTS_API_KEY`입니다!  
(백엔드 코드에서 TTS API 키를 Gemini에도 함께 사용)

**저장 후 백엔드 재시작:**
```bash
pm2 restart backend-server
```

---

#### **운영 서버 (Cafe24):**

```bash
# SSH 접속
ssh root@your-server.com

# .env 파일 수정
cd /root/BH2025_WOWU/backend
nano .env
```

**추가:**
```env
# Google Gemini API 설정
GOOGLE_CLOUD_TTS_API_KEY=AIzaSyC9XYZ_your_gemini_api_key_here
```

**저장 및 재시작:**
```
Ctrl+X → Y → Enter
pm2 restart backend-server
```

---

## 🧪 API 키 테스트

### **AI 생기부 작성 테스트:**

1. **로그인** (`http://localhost:3000`)
2. **AI 메뉴** → **"AI 생기부 작성"**
3. 학생 선택
4. **"AI 생성"** 버튼 클릭
5. 생기부가 자동으로 생성되는지 확인

### **예진이 AI 챗봇 테스트:**

1. **AI 챗봇 모델 선택** 드롭다운
2. **"🐶 예진이 만나기"** 선택
3. **모델 선택:** `gemini` (드롭다운에서 선택)
4. 메시지 입력 후 전송
5. AI 응답 확인

---

## 📊 .env 파일 전체 예시

`backend/.env` 파일:

```env
# 데이터베이스 설정
DB_HOST=kdt2025.com
DB_PORT=3306
DB_USER=iyrc
DB_PASSWORD=dodan1004~!@
DB_NAME=bh2025

# FTP 서버 설정
FTP_HOST=bitnmeta2.synology.me
FTP_PORT=2121
FTP_USER=ha
FTP_PASSWORD=dodan1004~

# Google Gemini API 설정 (AI 생기부/챗봇용) ⬅️ 여기!
GOOGLE_CLOUD_TTS_API_KEY=AIzaSyC9XYZ_your_gemini_api_key_here

# YouTube API 설정 (선택사항)
YOUTUBE_API_KEY=AIzaSyDDHyFYoFghliC_another_key_here
```

**💡 참고:** YouTube API 키와 Gemini API 키는 **다른 키**를 사용해야 합니다!  
(제한 설정이 다르기 때문)

---

## 📊 Gemini API 할당량 관리

### 무료 할당량 (Gemini 2.0 Flash)

| 항목 | 무료 할당량 |
|------|------------|
| **분당 요청** | 15 RPM |
| **일일 요청** | 1,500 RPM |
| **월간 토큰** | 무제한 |
| **비용** | **무료** ✅ |

### 유료 플랜

| 모델 | 비용 (1M tokens) |
|------|------------------|
| Gemini 2.0 Flash | $0.075 (input), $0.30 (output) |
| Gemini 1.5 Pro | $1.25 (input), $5.00 (output) |

### 할당량 확인

```
Google Cloud Console → API 및 서비스 → 할당량
https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas
```

### 할당량 초과 시

**증상:**
```
❌ Gemini API 오류: 429 Resource Exhausted
```

**해결책:**
1. **분당 요청 제한 (15 RPM)**: 1~2분 대기 후 재시도
2. **일일 요청 제한 (1,500 RPM)**: 다음 날까지 대기 또는 유료 플랜 전환
3. **임시 해결:** AI 생성 빈도 줄이기

---

## 🔧 문제 해결

### 문제 1: API 키 오류 (400 Bad Request)

**증상:**
```
❌ Gemini API 오류: API Key not found
```

**원인:**
- Generative Language API가 활성화되지 않음
- API 키가 잘못됨

**해결:**
```
1. Google Cloud Console 확인
2. Generative Language API 활성화 여부 확인
3. API 키 제한 설정에서 Generative Language API 허용 확인
4. .env 파일에 GOOGLE_CLOUD_TTS_API_KEY 올바르게 입력 확인
5. 백엔드 재시작
```

---

### 문제 2: API 키 작동하지 않음

**증상:**
```
❌ Gemini API 키가 설정되지 않았습니다
```

**해결:**
```bash
# 1. .env 파일 확인
cd backend
cat .env | grep GOOGLE_CLOUD

# 2. 환경변수 이름 확인
# GOOGLE_CLOUD_TTS_API_KEY=... 형식인지 확인

# 3. 앞뒤 공백 제거

# 4. 백엔드 재시작
pm2 restart backend-server

# 5. 로그 확인
pm2 logs backend-server --lines 50
```

---

### 문제 3: 403 Forbidden

**증상:**
```
❌ Gemini API 오류: 403 Forbidden
```

**원인:**
- API 키 제한 설정 문제
- IP 또는 리퍼러 제한

**해결:**
```
1. Google Cloud Console → 사용자 인증 정보
2. API 키 편집
3. "애플리케이션 제한사항" → "없음" 선택 (개발 단계)
4. "API 제한사항" → "Generative Language API"만 선택
5. 저장
```

---

### 문제 4: 429 Too Many Requests

**증상:**
```
❌ Gemini API 오류: 429 Resource Exhausted
```

**원인:**
- 분당 요청 제한 (15 RPM) 초과
- 일일 요청 제한 (1,500 RPM) 초과

**해결:**
```
1. 1~2분 대기 후 재시도
2. AI 생성 빈도 줄이기
3. 필요 시 유료 플랜 전환
```

---

## 📋 체크리스트

### Google Cloud Console 설정

- [ ] Google Cloud Console 접속
- [ ] 프로젝트 생성 또는 선택
- [ ] Generative Language API 활성화
- [ ] API 키 생성
- [ ] API 키 제한 설정 (보안)
- [ ] API 키 복사

### 시스템 등록

- [ ] backend/.env 파일 수정
- [ ] GOOGLE_CLOUD_TTS_API_KEY 추가
- [ ] 백엔드 재시작 (pm2 restart backend-server)
- [ ] PM2 로그 확인 (오류 없음)

### 동작 확인

- [ ] 로그인 (admin / kdt2025)
- [ ] AI 생기부 작성 테스트
- [ ] 예진이 AI 챗봇 테스트 (gemini 모델)
- [ ] 브라우저 콘솔 오류 없음
- [ ] AI 응답 정상 생성

---

## 🎯 Gemini vs OpenAI 선택 가이드

### **Gemini 추천 상황:**
- ✅ 무료로 사용하고 싶을 때
- ✅ 일일 1,500건 이하 요청
- ✅ 한국어 AI 생기부 작성
- ✅ 빠른 응답 속도 필요

### **OpenAI 추천 상황:**
- ✅ 더 높은 품질의 AI 응답 필요
- ✅ 하루 1,500건 이상 요청
- ✅ 복잡한 추론 작업
- ✅ GPT-4o의 고급 기능 필요

---

## 💡 비용 절약 팁

### **1. 무료 Gemini API 사용 (강력 추천)**
```env
# .env 파일에 Gemini API만 설정
GOOGLE_CLOUD_TTS_API_KEY=your_gemini_api_key
# OPENAI_API_KEY는 주석 처리 또는 제거
```

### **2. 토큰 제한 설정**
- 백엔드 코드에서 `max_tokens` 조정
- 불필요하게 긴 응답 방지

### **3. 캐싱 활용**
- 동일한 학생의 생기부는 캐시된 결과 재사용
- 중복 요청 방지

---

## 🔗 참고 링크

| 항목 | URL |
|------|-----|
| 🤖 Google AI Studio | https://aistudio.google.com/ |
| ☁️ Google Cloud Console | https://console.cloud.google.com/ |
| 📚 Gemini API 문서 | https://ai.google.dev/docs |
| 🔑 API 키 관리 | https://console.cloud.google.com/apis/credentials |
| 📊 할당량 확인 | https://console.cloud.google.com/apis/api/generativelanguage.googleapis.com/quotas |

---

## 🎯 지금 설정하세요!

### **로컬 환경 설정 (5분):**

```bash
# 1. Gemini API 키 발급
# https://console.cloud.google.com/apis/credentials

# 2. .env 파일 수정
cd "G:\내 드라이브\11. DEV_23\51. Python_mp3등\BH2025_WOWU\backend"
notepad .env

# 3. 다음 줄 추가:
# GOOGLE_CLOUD_TTS_API_KEY=AIzaSyC9XYZ_your_key_here

# 4. 저장 후 백엔드 재시작
pm2 restart backend-server

# 5. 브라우저에서 테스트
# http://localhost:3000 → AI 생기부 작성
```

---

**Gemini API 키를 발급받고 `.env` 파일에 추가한 후 결과를 알려주세요!** 🚀

**문서 작성일:** 2025-12-23  
**버전:** 1.0  
**대상 시스템:** KDT교육관리시스템 v3.2
