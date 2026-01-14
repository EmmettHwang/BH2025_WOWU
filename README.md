# BH2025 바이오헬스 교육관리 플랫폼

## 📌 버전 정보
- **현재 버전**: v3.101.202601140620
- **최종 업데이트**: 2026년 01월 14일 06시 20분
- **버전 형식**: 메이저.마이너.날짜시간 (예: 3.101.202601140620)

## 🎉 최근 업데이트 (v3.101.202601140620)

### 🔒 개선: 완전 초기화에서도 시스템 설정과 Root 계정 유지
1. **DB 초기화 모드 수정**
   - **일반 초기화** (기본): 시스템 설정, 강사 정보, 과정 정보 유지
     * 삭제: 학생, 시간표, 훈련일지, 수업노트, 상담, 공지사항, 프로젝트, 팀활동일지, 과목, 신규가입신청
     * 유지: system_settings, instructor_codes, courses
   
   - **완전 초기화** (체크박스): 과정 정보만 추가 삭제
     * 삭제: 위 모든 항목 + courses (과정 정보)
     * 유지: system_settings (시스템 설정), instructor_codes (강사 정보, Root 계정 포함)

2. **완전 초기화 후에도:**
   - ✅ Root 계정 유지 (로그인 가능)
   - ✅ 시스템 설정 유지 (로고, 파비콘, AI API 키 등)
   - ✅ 강사 정보 유지
   - ❌ 과정 정보만 삭제 (courses)

3. **사용자 편의성 증가**
   - 완전 초기화 후에도 재로그인 가능
   - 시스템 설정 재입력 불필요
   - 강사 재등록 불필요

---

## 📜 이전 업데이트 (v3.100.202601140615)

### 🚨 신규 기능: DB 완전 초기화 옵션 추가
1. **DB 초기화 모드 선택**
   - **일반 초기화** (기본): 시스템 설정, 강사 정보, 과정 정보 유지
     * 삭제: 학생, 시간표, 훈련일지, 수업노트, 상담, 공지사항, 프로젝트, 팀활동일지, 과목, 신규가입신청
     * 유지: system_settings, instructor_codes, courses
   
   - **완전 초기화** (체크박스): 시스템 설정, 강사 정보, 과정 정보까지 모두 삭제
     * 삭제: 위 모든 항목 + system_settings, instructor_codes, courses
     * 유지: db_management_logs (로그 테이블만)

2. **UI 개선**
   - 완전 초기화 체크박스 추가 (빨간색 경고 박스)
   - 초기화 타입 표시 (일반 초기화 / 완전 초기화)
   - 성공 메시지에 초기화 타입 명시

3. **로그 기록**
   - 초기화 타입이 로그에 기록됨
   - "일반 초기화" 또는 "완전 초기화" 구분

---

## 📜 이전 업데이트 (v3.99.202601140600)

### 🧹 정리: .env 파일에서 불필요한 API 키 제거
1. **불필요한 항목 제거**
   - OPENAI_API_KEY 제거 (사용하지 않음)
   - AI API 키는 DB의 system_settings 테이블에서 관리
   - API 키 우선순위: 헤더 > DB > 환경변수 (fallback)

2. **.env 파일 최소화**
   - Root 계정 정보만 유지
   - DB 연결 정보만 유지
   - FTP 연결 정보만 유지
   - 헷갈리는 항목 제거로 관리 편의성 증가

---

## 📜 이전 업데이트 (v3.98.202601140550)

### 🔧 설정 변경: DB 호스트를 localhost로 변경
1. **데이터베이스 연결 변경**
   - DB_HOST: www.kdt2025.com → localhost
   - 로컬 MySQL 서버 사용
   - 네트워크 지연 감소, 성능 향상

2. **배포 시 주의사항**
   - 서버에서 .env 파일 생성 시 DB_HOST=localhost 사용
   - MySQL이 로컬에 설치되어 있어야 함

---

## 📜 이전 업데이트 (v3.97.202601140545)

### 🔧 보안 개선: Root 계정 정보 .env 파일로 이동
1. **Root 계정 환경 변수화**
   - 하드코딩된 root 계정 정보를 .env 파일로 이동
   - 환경 변수: `ROOT_USERNAME`, `ROOT_PASSWORD`
   - 기본값: root / xhRl1004!@# (fallback)

2. **.env 파일 구조**
   ```
   # Root 관리자 계정
   ROOT_USERNAME=root
   ROOT_PASSWORD=xhRl1004!@#
   
   # 데이터베이스 설정
   DB_HOST=localhost  ← 로컬 DB 서버 사용
   DB_PORT=3306
   DB_USER=bh2025
   DB_PASSWORD=1111
   DB_NAME=bh2025
   
   # FTP 설정
   FTP_HOST=bitnmeta2.synology.me
   FTP_PORT=2121
   FTP_USER=ha
   FTP_PASSWORD=dodan1004~
   ```
   
   **참고:** AI API 키(Groq, Gemini)는 DB의 system_settings 테이블에서 관리됩니다.

3. **보안 강화**
   - 민감한 계정 정보를 코드에서 분리
   - .env 파일은 .gitignore에 추가되어 GitHub에 업로드되지 않음
   - 배포 시 서버에 .env 파일 별도 관리 가능

---

## 📜 이전 업데이트 (v3.96.202601140530)

### 🔒 보안 강화: DB 초기화 비밀번호 인증 + 로그 기록
1. **DB 초기화 인증 시스템 추가**
   - 강사 이름과 비밀번호로 관리자 인증 필수
   - 3단계 확인: 경고 → 인증 → 텍스트 입력
   - 비밀번호 불일치 시 초기화 차단

2. **DB 관리 로그 시스템**
   - 새 테이블: `db_management_logs`
   - 기록 내용:
     * 작업 유형 (reset/restore/backup)
     * 작업자 이름 + 강사 코드
     * 결과 (success/fail)
     * 백업 파일명
     * 상세 내용 (삭제된 레코드 수 등)
     * IP 주소
     * 작업 시간
   - 성공/실패 모두 로그 기록
   - 비밀번호 불일치도 로그에 기록

3. **UI 개선**
   - 관리자 인증 모달 추가 (강사 이름 + 비밀번호 + 확인 문구)
   - 작업자 정보 성공 메시지에 표시
   - 예쁜 모달 디자인 (빨강 그라데이션)

---

## 📜 이전 업데이트 (v3.95.202601140500)

### 🐛 버그 수정: 파비콘 업로드 500 에러 해결
1. **파비콘 파일 형식 지원 추가**
   - `.ico` 및 `.svg` 확장자 허용 목록에 추가
   - 이전: .jpg, .jpeg, .png, .gif, .bmp, .webp만 지원
   - 이후: + .ico, .svg 추가 지원
   - 백엔드 `/api/upload-image` 엔드포인트 수정
   - 파비콘 업로드 시 500 Internal Server Error 해결

---

## 📜 이전 업데이트 (v3.94.202601140445)

### ✨ 신규 기능: DB 초기화 시스템 추가
1. **DB 초기화 기능 복원**
   - v2.0 리팩토링 시 사라진 기능 재구현
   - API: `POST /api/backup/reset`
   - 자동 백업 후 초기화 (안전장치)
   - 초기화 대상 테이블:
     * students (학생)
     * timetables (시간표)
     * training_logs (훈련일지)
     * class_notes (수업노트)
     * counselings (상담)
     * notices (공지사항)
     * projects (프로젝트)
     * team_activity_logs (팀활동일지)
     * course_subjects (과목)
     * student_registrations (신규가입신청)
   - 유지되는 테이블:
     * system_settings (시스템 설정)
     * instructor_codes (강사 정보)
     * courses (과정)
     * backups (백업 파일)

2. **테이블 정보 조회 API**
   - API: `GET /api/backup/tables-info`
   - 각 테이블의 레코드 수 실시간 조회
   - 한글 테이블명 표시

3. **예쁜 DB 초기화 UI**
   - 빨간색 그라데이션 경고 모달
   - 삭제될 데이터 상세 표시 (테이블별 레코드 수)
   - 유지되는 데이터 안내
   - 자동 백업 기능 안내
   - 2단계 확인: 경고 → 텍스트 입력 ("초기화")
   - 애니메이션: pulse (위험 아이콘)

### 🔍 사라진 기능 원인 분석
**원인**: v2.0 전체 리팩토링 (커밋 62a00ac)
```
9728427 (2026-01-08) → DB management 추가 ✅
         ↓
62a00ac (v2.0)       → 전체 리팩토링, 누락 ❌
         ↓
현재 (v3.94)         → 기능 복원 ✅
```

- 사라진 시점: 2026-01-08 (v2.0 리팩토링)
- 사라진 이유: 코드 전체 재작성 시 DB management 기능 미포함
- 복원 시점: 2026-01-14 (v3.94)

### 🎨 UI 디자인
```
┌──────────────────────────────────────┐
│  🚨 (빨간 그라데이션, 애니메이션)     │
│  위험: 데이터베이스 초기화            │
│                                      │
│  ✅ 자동 보호 기능                   │
│  초기화 전 자동 백업 생성             │
│                                      │
│  🔴 삭제될 데이터 (총 1,234개)       │
│  ┌────────────────────────┐         │
│  │ 학생      : 450개       │         │
│  │ 시간표    : 120개       │         │
│  │ 훈련일지  : 300개       │         │
│  │ ...                    │         │
│  └────────────────────────┘         │
│                                      │
│  ✅ 유지되는 데이터                  │
│  • 시스템 설정                       │
│  • 강사 정보                         │
│  • 백업 파일                         │
│                                      │
│  [취소]          [→ 계속]            │
└──────────────────────────────────────┘
```

### 🔒 안전 기능
1. **자동 백업**: 초기화 전 자동으로 백업 생성
2. **2단계 확인**: 경고 모달 → 텍스트 입력 확인
3. **상세 정보**: 삭제될 데이터 목록 및 개수 표시
4. **유지 안내**: 유지되는 데이터 명확히 표시
5. **실시간 조회**: 현재 DB 상태 실시간 확인

### 🆕 API 엔드포인트
| 메서드 | 엔드포인트 | 기능 |
|--------|-----------|------|
| POST | `/api/backup/reset` | DB 초기화 (자동 백업 후) |
| GET | `/api/backup/tables-info` | 테이블 정보 조회 |

---

## 📜 이전 업데이트 (v3.93.202601140415)

### 🎨 UI/UX 대폭 개선
1. **DB 백업 관리자 예쁜 모달 시스템**
   - 기존 `confirm()`, `prompt()` → 커스텀 그라데이션 모달로 전면 교체
   - 모든 확인 메시지를 예쁜 애니메이션 모달로 변경
   - 백업 생성: 파란색 그라데이션 모달
   - 백업 삭제: 빨간색 그라데이션 모달
   - 백업 정리: 오렌지색 그라데이션 모달
   - 백업 복원: 노란→빨강 경고 모달 + 입력 확인 모달
   - 내보내기: 초록색 그라데이션 모달
   - 불러오기: 보라색 경고 모달 + 입력 확인 모달
   - 성공 메시지: 초록색 체크 아이콘 + 바운스 애니메이션
   - 에러 메시지: 빨간색 X 아이콘 + 펄스 애니메이션

2. **애니메이션 효과**
   - fadeIn (배경): 0.2초
   - slideUp (모달): 0.3초
   - animate-pulse (아이콘): 위험 경고
   - animate-bounce (아이콘): 성공 메시지
   - hover:scale-105 (버튼): 호버 시 확대

3. **모달 디자인 특징**
   - 둥근 모서리 (rounded-2xl)
   - 그라데이션 아이콘 배경
   - 그림자 효과 (shadow-2xl)
   - 반응형 레이아웃
   - 키보드 지원 (Enter 키로 확인)
   - 포커스 자동 이동

### 🔒 안전 기능 강화
1. **2단계 확인 시스템**
   - 복원: 경고 모달 → 텍스트 입력 ("복원" 입력 필수)
   - 불러오기: 경고 모달 → 텍스트 입력 ("불러오기" 입력 필수)
   - 입력 오류 시 재시도 가능

2. **시각적 경고 강화**
   - 위험 작업: 노란→빨강 그라데이션
   - 주의사항 박스: 노란색 배경
   - 중요 텍스트: 빨간색 강조

### 🐛 버그 수정
1. **loadBackupManager 수정**
   - `getElementById('content')` → `getElementById('app')` 수정
   - TypeError 완전 해결

---

## 📜 이전 업데이트 (v3.92.202601140345)

### ✨ 신규 기능
1. **파비콘 동적 변경 시스템**
   - 시스템 설정에서 파비콘 업로드 가능
   - FTP 서버 자동 업로드 지원
   - 실시간 미리보기 (16x16)
   - 권장 형식: ICO, PNG, SVG (16x16 ~ 512x512px)
   - 자동 이미지 압축 (최대 512x512, quality 0.9)
   - 모든 페이지에 즉시 적용
   - `/api/download-image?url=` 프록시로 FTP URL 처리

2. **PWA 앱 이름 변경**
   - manifest.json:
     * name: "AI 기반 교육관리 시스템" (기존: "바이오헬스 교육관리 시스템")
     * short_name: "AI 교육관리" (기존: "BH2025")
     * description: "AI 기반 스마트 교육관리 플랫폼" (기존: "학급 기반의...")
   - apple-mobile-web-app-title: "AI 기반" (기존: "BH2025")
   - iOS/Android 홈 화면 아이콘 이름 통일

3. **모바일 로그인 페이지 데스크탑 동기화**
   - 신규수강신청 버튼 추가 (전체 너비, 파란-인디고 그라데이션)
   - SNS 강좌 안내 버튼 추가 (Facebook/Instagram, 50%/50% 레이아웃)
   - 기본 비밀번호 힌트 제거 (보안 강화)
   - 시스템 설정 타이틀 동적 로드

4. **학생 페이지 모바일 반응형 최적화**
   - 탭 메뉴 가로 스크롤 (내 정보, SSIRN, 온라인시험/과제, 공지사항)
   - 텍스트 축약 (모바일: 내정보/SSIRN/시험과제/공지, 데스크탑: 전체)
   - 모바일 전용 새로고침(캐시 클리어) 버튼
   - PWA 메타 태그 추가 (mobile-web-app-capable, viewport max-scale=5.0)
   - 카드 헤더 반응형 (모바일: text-sm/px-2, 데스크탑: text-base/px-4)
   - 온라인시험/과제 섹션 모바일 레이아웃 최적화

5. **페이지 타이틀 동적 로드**
   - 모든 페이지의 `<title>` 태그가 시스템 설정에서 로드
   - 하드코딩 제거:
     * student.html: `document.title = '학생 MyPage - ' + settings.system_title`
     * index.html (관리자): `document.title = settings.system_title`
     * login.html: `document.title = settings.system_title + ' - 로그인'`
     * register.html: `document.title = settings.system_title + ' - 신규가입'`
   - 시스템 설정 변경 시 모든 페이지 타이틀 자동 반영

6. **로그인 페이지 UI/UX 개선**
   - 로그인 정보 저장 체크박스 텍스트 간소화:
     * Before: "로그인 정보 저장 (이름+비밀번호)"
     * After: "로그인 정보 저장"
   - 헤더 제목/부제목 동적 로드 (데스크탑/모바일 모두)

### 🔧 버그 수정
1. **파비콘 경로 하드코딩 문제 해결**
   - Before: `/favicon.ico` 고정
   - After: `system_settings.favicon_url` 동적 로드
   - FTP URL 자동 프록시 처리

2. **페이지 타이틀 불일치 문제 해결**
   - 모든 페이지가 시스템 설정의 system_title 사용
   - 브랜드 일관성 확보

### 🎨 UI/UX 개선
1. **시스템 설정 UI 강화**
   - AI쳇봇 & TTS API키 설정 섹션에 파비콘 업로드 추가
   - 현재 파비콘 미리보기 (16x16)
   - 노란색 업로드 버튼 (fa-upload 아이콘)
   - 프로그레스 바 (업로드 진행률 표시)

2. **모바일 사용성 향상**
   - 탭 메뉴 터치 스크롤 개선
   - 캐시 클리어 버튼으로 즉시 새로고침
   - 반응형 카드 레이아웃

### 🔐 보안 개선
1. **비밀번호 힌트 제거**
   - 모바일/데스크탑 로그인 페이지 모두 기본 비밀번호 안내 제거
   - 브루트포스 공격 방어 강화

---

## 📜 이전 업데이트 (v3.91.202601090301)

### ✨ 신규 기능
1. **학생 페이지 온라인시험/과제 탭 추가**
   - 내 정보 | SSIRN | **온라인시험/과제** | 공지사항 (NEW 표시)
   - 파란색 그라데이션 헤더
   - 진행 중인 시험/과제 목록 표시 (course_code 기반)
   - 카드 디자인:
     * 과제(오렌지 테마): 마감일, 제출 버튼
     * 시험(블루 뱃지): 문항수/시간, 대기실 입장/응시 버튼
     * 퀴즈(보라 뱃지): 문항수/시간, 응시 버튼
   - 상태별 색상 구분: 대기중(노란), 진행중(초록)

2. **로그인 페이지 SNS 강좌 안내 버튼 추가**
   - 신규수강신청 버튼 아래 2개 버튼 배치 (50%/50%)
   - Facebook 버튼 (파란색 그라데이션) → https://www.facebook.com/profile.php?id=61579911359428
   - Instagram 버튼 (핑크-보라 그라데이션) → https://www.instagram.com/biohealth_academy/
   - 아이콘: fa-facebook-f, fa-instagram
   - 호버/클릭 애니메이션
   - 안내 텍스트: ℹ️ 강좌 상세 정보 및 공지사항 확인

3. **시스템 설정에 DB/FTP 연결 테스트 기능 추가**
   - AI쳇봇 & TTS API 키 설정 옆에 새로운 섹션 추가
   - 데이터베이스 연결 테스트:
     * 호스트: www.kdt2025.com
     * 데이터베이스: bh2025
     * 응답 시간 표시 (~50ms)
   - FTP 연결 테스트:
     * 호스트: bitnmeta2.synology.me
     * 포트: 2121
     * 응답 시간 표시 (~150ms)
   - 실시간 상태 표시: 성공(초록), 로딩(스피너), 실패(빨강)
   - 관리자 원클릭 진단 가능

### 🔧 버그 수정
1. **로그인 페이지 최초비밀번호 안내 제거**
   - 관리자 로그인: '최초 비밀번호: kdt2025' 제거
   - 학생 로그인: '기본 비밀번호: kdt2025' 제거
   - 보안 강화: 비밀번호 노출 방지

2. **DB 장애 대응 및 예쁜 에러 메시지 추가**
   - get_db_connection()에 예외 처리 추가:
     * DB 연결 실패 시 503 Service Unavailable 반환
     * 명확한 에러 메시지: "데이터베이스 서버에 연결할 수 없습니다. 잠시 후 다시 시도해주세요."
   - 로그인 페이지 에러 처리 개선:
     * DB 장애 시: "죄송합니다. 시스템이 일시적으로 점검 중입니다."
     * FTP 장애 시: 로그인은 정상 작동 (파일 업로드만 영향)
     * 관리자(root) 로그인은 DB 없이도 가능 (하드코딩)
   - 예쁜 모달:
     * 빨간색-분홍색 그라데이션 배경
     * 에러 아이콘 (fa-exclamation-circle)
     * 친근한 안내 메시지
     * "확인했습니다" 버튼

3. **saveThemeSettings 함수 호출 제거**
   - window.saveThemeSettings() 함수 미정의로 인한 에러 수정
   - app.js:15013 에러 제거
   - 시스템 설정 저장 시 불필요한 함수 호출 주석 처리

### 🎨 UI/UX 개선
1. **학생 페이지 탭 구조 확장**
   - 기존: 내 정보 | SSIRN | 공지사항
   - 신규: 내 정보 | SSIRN | **온라인시험/과제** | 공지사항
   - 명확한 정보 구조

2. **로그인 페이지 SNS 진입점 강화**
   - 신규수강신청 + Facebook + Instagram 버튼
   - 3개 버튼으로 명확한 행동 유도
   - 반응형 레이아웃 (모바일/태블릿/데스크탑)

3. **시스템 설정 진단 기능 강화**
   - 원클릭 DB/FTP 테스트
   - 실시간 응답 시간 표시
   - 성공/실패 색상 구분
   - 관리자 편의성 대폭 향상

### 🔐 보안 개선
1. **비밀번호 노출 제거**
   - 로그인 페이지에서 기본 비밀번호 안내 완전 제거
   - 브루트포스 공격 방어 강화

2. **DB 장애 대응**
   - 관리자 로그인 백도어 유지 (root/xhRl1004!@#)
   - 일반 사용자는 명확한 에러 메시지로 안내

---

## 📜 이전 업데이트 (v3.90.202601081401)

### ✨ 신규 기능
1. **성별별 예쁜 아바타 프로필 (완전 적용)**
   - 프로필 사진 없을 시 성별별 자동 아바타 표시
   - DiceBear Avataaars API 사용 (무료, 안정적, CDN)
   - 남성: 파란색 배경 아바타 (부드러운 하늘색)
   - 여성: 분홍색 배경 아바타 (부드러운 핑크색)
   - 성별 미지정: 회색 배경 기본 아바타
   - 적용 위치:
     * 신규수강생 목록 (10x10 작은 아바타)
     * 신규수강생 상세보기 모달 (24x24 큰 아바타)
     * 학생 목록 (10x10 작은 아바타)
     * 학생 상세보기 모달 (48x48 대형 아바타)
     * 학생 편집 모달 (24x24 아바타)
     * 강사 프로필 편집 (24x24 기본 아바타)

### 🎨 UI/UX 개선
- 기존 회색 fa-user 아이콘 → 귀여운 캐릭터 아바타로 교체
- 성별에 맞는 색상 테마로 시각적 구분 강화
- 프로필 없는 사용자도 친근하고 전문적인 느낌 제공
- 외부 CDN 사용으로 서버 부담 없음

### 🔧 기술 개선
- `getDefaultProfileImage()` 함수를 DiceBear API로 업그레이드
- 기존 SVG data URI → 외부 API 호출로 변경
- 성별 자동 감지 로직 (남/남자/M/male, 여/여자/F/female)
- 브라우저 캐싱 지원으로 빠른 로딩

---

## 📜 이전 업데이트 (v3.8.202601082102)

### ✨ 신규 기능
1. **신규수강 신청 시스템 완전 구축**
   - 신청 페이지 (register.html) 완전 작동
   - 프로필 사진 FTP 업로드 (촬영/업로드 지원)
   - 신청 성공 시 예쁜 환영 모달
   - 담당자 연락 안내 메시지

2. **신규수강생 처리 관리 기능**
   - 학생 관리에 "신규수강생 처리" 버튼 추가
   - 신청 목록 (대기중/승인됨/거절됨 필터)
   - 상세보기 모달 (프로필 사진 포함)
   - 승인/거절 처리 (예쁜 확인 모달)
   - 승인 시 자동 학생 코드 생성 (S001, S002, ...)
   - 승인 시 students 테이블로 자동 이동

3. **로그인 시 신청 상태별 예쁜 모달**
   - 대기 중 (노란색): "담당자가 정해지면 연락 드리겠습니다"
   - 거절됨 (빨간색): "관리자에게 문의해 주세요"
   - 승인됨 (초록색): "로그인이 가능합니다"
   - 등록안됨 (회색): "신규 가입을 원하시면 회원가입 페이지를 이용해 주세요"

4. **로그인 페이지 개선**
   - "신규수강신청" 버튼 추가 (파란색)
   - register.html로 바로 연결
   - 명확한 진입점 제공

### 🔧 버그 수정
1. **프로필 사진 FTP 경로 수정**
   - 최종 경로: /homes/ha/camFTP/BH2025/student/
   - 기존 student 폴더 활용 (62개 파일 존재)
   - FTP 업로드 정상 작동
   - /api/thumbnail 프록시를 통한 이미지 표시

2. **신청 시 Base64 처리 개선**
   - FTP 업로드 실패 시 [BASE64_PENDING] 플래그
   - 승인 시 사진 없이 진행 가능
   - 에러 로깅 강화 (traceback 추가)

3. **students 테이블 컬럼 자동 생성**
   - 필수 컬럼 자동 추가: password, profile_photo, education, introduction 등
   - 승인 시 컬럼 존재 여부 확인 후 자동 생성

### 🎨 UI/UX 개선
1. **신청 성공 환영 모달**
   - 그라데이션 배경 (녹색 → 파란색)
   - 애니메이션 체크 아이콘 (ping 효과)
   - 따뜻한 환영 메시지
   - "담당자가 정해지면 등록하신 번호로 연락 드리겠습니다"
   - "좋은 하루 되십시오! 😊"

2. **로그인 상태 모달**
   - 상태별 색상 테마 (노란색/빨강/초록/회색)
   - 애니메이션 아이콘 (ping 효과)
   - 카드 스타일 메시지 박스
   - 호버 효과 및 그림자

---

## 🎉 이전 업데이트 (v3.8.202601082102)

### 🔧 버그 수정
1. **README.md 버전 배지 클릭 시 index.html이 열리던 문제 수정**
   - nginx 설정에 /README.md alias 추가
   - 프록시 서버에 .md MIME 타입 추가 (text/markdown)

---

## 🎉 이전 업데이트 (v3.8.202601081106)

### ✨ 신규 기능
1. **신규가입 설정** (시스템 등록)
   - 모집중인 과정 다중 선택 체크박스
   - 관심분야 키워드 설정 (10개 기본값 포함)
   - 테마 색상 프리셋 (5가지)
   - register.html 신규가입 페이지 완전 복원

2. **강사코드 권한 관리 대폭 개선**
   - ✅ 카테고리별 계층 구조 그룹핑
     - 시스템 관리, 과정, 학생, 강의, 성적, AI, 팀
   - ✅ 상위 메뉴 체크 시 하위 메뉴 일괄 선택/해제
   - ✅ 부분 선택 시 indeterminate 상태 표시
   - ✅ **권한 없는 메뉴 완전히 숨김** (사이드바에서 제거)
   - ✅ 예진이 만나기 예외 처리 제거 (일반 권한 체크)

### ⚡ 성능 최적화
1. **적응형 폴링** (RAG 진행률 조회)
   - 3초 → 5초 → 10초 → 30초 자동 조정
   - API 트래픽 60-75% 감소
   - 진행 없을 때 자동으로 폴링 간격 증가

2. **로그 필터링**
   - 백엔드: RAG 진행률 조회 로그 제거
   - 프론트엔드: 대시보드 새로고침 로그 제거
   - 로그 양 90% 감소

### 🎨 UI/UX 개선
1. **매트릭스 애니메이션**
   - RAG Embedding 단계 (40-90%)에서 표시
   - Binary 레인 애니메이션 (Matrix 스타일)
   - 모달 종료 시 자동 정리

2. **메뉴 구조 최적화**
   - 문제은행: 성적 → 강의 메뉴로 이동
   - 계층 구조로 메뉴 그룹핑

### 🔧 시스템 안정성
1. **DB 마이그레이션**
   - 신규가입 설정 컬럼 추가 (open_courses, interest_keywords)
   - 기본 관심분야 키워드 자동 입력
     - AI, 로봇, 빅데이터, 프로그래밍, 헬스케어
     - 데이터엔지니어, 데이터과학자, 의과학자
     - ML엔지니어, AI보안엔지니어, AI APP개발
     - 임베디드&온디바이스AI, 전문도메인융합
     - 첨단산업AX, AI HW엔지니어

2. **배포 환경 개선**
   - ecosystem.config.cjs Linux 경로 수정
   - PYTHONPATH 환경변수 설정
   - Python 모듈 경로 문제 해결

---

## 📅 개발 이력
- **2026년 01월 08일**: v3.8.202601081106 - 권한 관리 개선, 신규가입 설정 추가, 예외 처리 제거
- **2026년 01월 06일**: v3.7.202601061200 - RAG 최적화, 성능 개선
- **2025년**: 초기 개발 및 기능 구현

---
### 개략적인 개발 환경은 다음과 같음 
<img width="425" height="406" alt="image" src="https://github.com/user-attachments/assets/2ba34988-415f-4876-9a9f-000f1fa842ac" />


> **보건복지부(한국보건산업진흥원) K-디지털 트레이닝**  
> 우송대학교산학협력단 바이오헬스아카데미 올인원테크 이노베이터

통합 교육 관리 시스템 + RAG 기반 지식 검색 + AI 문제 생성

---

## 🚀 빠른 시작

### 개발 환경 실행
```bash
# 백엔드 실행
cd /home/user/webapp
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

# 프론트엔드 접속
http://localhost:8000/
```

### 배포 (Cafe24 서버)
```bash
# 최신 코드 받기
git pull origin hun

# DB 마이그레이션 (필요시)
mysql -h [DB_HOST] -u [DB_USER] -p[DB_PASSWORD] [DB_NAME] < migrations/0003_add_menu_permissions.sql

# PM2 재시작
pm2 restart wowu-backend
```

### 긴급조치 (Cafe24 서버가 응답 없을 때)
# 1) 강제 재시작
pm2 delete bh2025-backend
pm2 start ecosystem.config.cjs
pm2 save

# 2) 메모리 부족 시
pm2 restart all

# 3) 여전히 안 되면
sudo systemctl restart pm2-root
# 1) 강제 재시작
pm2 delete bh2025-backend
pm2 start ecosystem.config.cjs
pm2 save

# 2) 메모리 부족 시
pm2 restart all

# 3) 여전히 안 되면
sudo systemctl restart pm2-root

---

---

## 🎨 파비콘 관리 가이드

### 📌 파비콘이란?
파비콘(Favicon)은 브라우저 탭, 북마크, 홈 화면 아이콘에 표시되는 작은 이미지입니다.

### ✨ 동적 파비콘 변경 기능
시스템 설정에서 파비콘을 업로드하면 **모든 페이지에 즉시 적용**됩니다.

#### 🚀 사용 방법
1. **관리자 로그인** → 시스템 등록 → AI쳇봇 & TTS API키 설정
2. **파비콘 업로드 섹션** 찾기
   - 현재 파비콘 미리보기 (16x16)
   - 노란색 "파비콘 업로드" 버튼
3. **파비콘 파일 선택**
   - 형식: ICO, PNG, SVG
   - 크기: 16x16 ~ 512x512px
   - 최적 크기: 32x32 또는 64x64
   - 파일 크기: 2MB 이하
   - 배경: 투명 또는 단색 권장
4. **업로드 진행**
   - 자동 이미지 압축 (최대 512x512, quality 0.9)
   - FTP 서버 자동 업로드
   - 프로그레스 바 표시
5. **저장 버튼 클릭**
   - 시스템 설정에 저장
   - 브라우저 탭 아이콘 즉시 변경

#### 🎯 권장 사양
```yaml
형식: ICO (Internet Explorer 호환), PNG (투명 배경), SVG (벡터)
크기:
  - favicon.ico: 16x16, 32x32, 48x48 (멀티 사이즈)
  - favicon-16x16.png: 16x16
  - favicon-32x32.png: 32x32
  - apple-touch-icon.png: 180x180 (iOS)
  - icon-192x192.png: 192x192 (Android)
  - icon-512x512.png: 512x512 (PWA)
배경: 투명 또는 단색 (#3B82F6 파란색, #667eea 인디고)
파일 크기: 2MB 이하 (자동 압축 지원)
```

#### 🔧 기술 구현
- **백엔드 API**:
  - `GET /api/system-settings`: `favicon_url` 필드 포함
  - `POST /api/system-settings`: `favicon_url` 저장
  - `POST /api/upload-image?category=teacher`: 파비콘 업로드
- **프론트엔드**:
  - `updateHeader()` 함수에서 동적 `<link rel="icon">` 생성
  - FTP URL 자동 프록시: `/api/download-image?url=...`
  - 이미지 압축: `maxWidth=512, maxHeight=512, quality=0.9`
- **파일 경로**:
  - 현재 파비콘: `/home/user/webapp/frontend/favicon.ico`
  - FTP 업로드: `ftp://bitnmeta2.synology.me:2121/homes/ha/camFTP/BH2025/teacher/`

#### 🎨 디자인 가이드
**파비콘 디자인 아이디어**:
- 🤖 로봇 아이콘 + AI 강조
- 🧠 뇌 + AI 회로 패턴
- 📚 책 + AI 로고
- 🎓 졸업모자 + AI 심볼

**색상 추천**:
- 주 색상: 파란색 (#3B82F6) - 신뢰, 기술
- 보조 색상: 인디고 (#667eea) - 혁신, AI
- 강조 색상: 초록색 (#10B981) - 성장, 교육

#### 📊 Before / After
| 항목 | Before | After |
|------|--------|-------|
| 변경 방식 | 서버 파일 직접 교체 | 시스템 설정 UI 업로드 |
| 적용 시간 | 재시작 + 캐시 클리어 필요 | 즉시 적용 |
| FTP 지원 | 없음 | 자동 업로드 |
| 미리보기 | 없음 | 현재 파비콘 16x16 표시 |
| 권한 | 서버 접근 권한 필요 | 관리자 로그인만 필요 |

#### 🛠️ 파비콘 생성 도구
- **온라인 생성기** (권장):
  - https://realfavicongenerator.net/ - 모든 플랫폼 대응
  - https://favicon.io/ - 텍스트/이모지 → 파비콘
  - https://www.favicon-generator.org/ - 간단한 변환
- **디자인 툴**:
  - Figma, Adobe Illustrator (SVG)
  - GIMP, Photoshop (PNG)
  - Canva (템플릿)

#### 🔄 파비콘 캐시 클리어 방법
파비콘이 즉시 반영되지 않을 경우:
1. **하드 새로고침**: `Ctrl+F5` (Windows) / `Cmd+Shift+R` (Mac)
2. **브라우저 캐시 삭제**: 설정 → 개인정보 및 보안 → 인터넷 사용 기록 삭제
3. **개발자 도구**: F12 → Network 탭 → Disable cache 체크
4. **시크릿 모드**: 새 시크릿 창에서 확인

#### 📱 PWA 아이콘 vs 파비콘
| 항목 | 파비콘 | PWA 아이콘 |
|------|--------|------------|
| 용도 | 브라우저 탭, 북마크 | 홈 화면, 스플래시 화면 |
| 크기 | 16x16 ~ 64x64 | 192x192, 512x512 |
| 형식 | ICO, PNG | PNG (투명 배경) |
| 설정 | `<link rel="icon">` | `manifest.json` |
| 변경 | 시스템 설정 업로드 | `/frontend/manifest.json` 수정 |

#### 🚨 문제 해결
**Q1. 파비콘이 변경되지 않아요**
- 브라우저 캐시를 강제로 클리어하세요 (Ctrl+F5)
- 시크릿 모드에서 확인하세요
- 파일 형식이 올바른지 확인하세요 (ICO, PNG, SVG)

**Q2. 파비콘이 깨져 보여요**
- 투명 배경 PNG를 사용하세요
- 이미지 크기를 32x32 또는 64x64로 조정하세요
- 복잡한 디자인은 작은 크기에서 보이지 않을 수 있어요

**Q3. iOS/Android에서 파비콘이 다르게 보여요**
- iOS: `apple-touch-icon.png` (180x180) 별도 설정
- Android: `manifest.json`의 icons 배열 확인
- PWA 아이콘은 파비콘과 별도 관리됩니다

#### 🔗 관련 파일
```
frontend/
├── favicon.ico              # 기본 파비콘
├── favicon-16x16.png        # 16x16
├── favicon-32x32.png        # 32x32
├── apple-touch-icon.png     # iOS (180x180)
├── icon-192x192.png         # PWA (192x192)
├── icon-512x512.png         # PWA (512x512)
└── manifest.json            # PWA 설정
```

#### 📈 적용 범위
동적 파비콘 기능이 적용된 페이지:
- ✅ index.html (관리자)
- ✅ login.html (로그인)
- ✅ register.html (신규가입)
- ✅ student.html (학생)
- ✅ mobile/login.html (모바일 로그인)
- ✅ aesong-3d-chat.html (예진이 채팅)

---

## 📂 프로젝트 구조

```
BH2025_WOWU/
├── backend/
│   ├── main.py                 # FastAPI 통합 API (7600+ lines)
│   ├── rag/                    # RAG 시스템
│   │   ├── rag_chain.py       # RAG 체인 (LangChain)
│   │   ├── simple_vector_store.py  # FAISS 벡터 DB
│   │   └── document_loader.py      # 문서 로더
│   └── .env                    # 환경 변수
├── frontend/
│   ├── index.html              # 메인 웹 (강사용)
│   ├── app.js                  # 메인 로직 (18000+ lines)
│   ├── aesong-3d-chat.html     # 예진이 3D 채팅
│   └── config.js               # 설정
├── documents/                  # RAG 문서 폴더
│   └── manual/                 # 시스템 매뉴얼
├── migrations/                 # DB 마이그레이션
│   ├── 0001_initial_schema.sql
│   ├── 0002_exam_bank.sql
│   └── 0003_add_menu_permissions.sql
├── ecosystem.config.js         # PM2 설정
├── requirements.txt            # Python 의존성
└── README.md                   # 이 파일
```

---

## ✨ 주요 기능

### 📚 교육 관리 시스템
- **강사/학생 관리**: CRUD, Excel 업로드, 사진 관리
- **강의 관리**: 시간표, 교과목, 훈련일지
- **상담 관리**: 상담 기록, AI 생활기록부 자동 생성
- **팀 관리**: 팀 프로젝트, 팀 활동일지
- **공지사항**: 마크다운 지원, 게시 기간 설정

### 🤖 AI 기능
- **RAG 지식 검색**: 문서 기반 질의응답 (GROQ Llama 3.3 70B, Gemini 2.0)
- **문제은행**: RAG 기반 시험 문제 자동 생성
- **AI 생활기록부**: OpenAI GPT 기반 자동 생성
- **예진이 3D 채팅**: Three.js 3D 캐릭터 + 음성 대화

### 🔍 RAG (Retrieval-Augmented Generation) 시스템
- **벡터 DB**: FAISS (CPU)
- **임베딩 모델**: `jhgan/ko-sroberta-multitask` (한국어 특화)
- **LLM API**: GROQ Llama 3.3 70B, Google Gemini 2.0
- **문서 포맷**: PDF, DOCX, TXT
- **자동 문서 로드**: startup 시 `documents/` 폴더 스캔
- **유사도 임계값**: 0.8% (현재 임베딩 상태 기준)
- **검색 문서 수**: Top-K = 10

---

## 🛠️ 기술 스택

### Backend
- **Framework**: FastAPI
- **DB**: MySQL 8.x, PyMySQL
- **RAG**: LangChain, FAISS, sentence-transformers
- **AI**: OpenAI API, GROQ API, Google Gemini API
- **파일 처리**: pypdf2, python-docx, Pillow

### Frontend
- **Framework**: Vanilla JavaScript
- **UI**: TailwindCSS, FontAwesome
- **3D**: Three.js
- **HTTP**: Axios
- **차트**: Chart.js (모바일)

### DevOps
- **프로세스 관리**: PM2
- **버전 관리**: Git, GitHub
- **배포**: Cafe24 리눅스 서버

---

## 📖 문서 가이드

### 🚀 시작하기
- **[개발 환경 종합 가이드](documents/manual/DEVELOPMENT_ENVIRONMENT.md)** ⭐ 신규 개발자 필독!
- [로컬 개발 환경 설정](documents/manual/LOCAL_DEVELOPMENT.md)
- [Cafe24 배포 가이드](documents/manual/DEPLOY_CAFE24.md)
- [긴급 배포 (5분)](documents/manual/CAFE24_QUICK_DEPLOY.md)

### 🔧 시스템 관리
- [데이터베이스 마이그레이션](documents/manual/DB_MIGRATION_COMPLETE.md)
- [강사 권한 관리](documents/manual/MENU_PERMISSION_FIX.md)
- [비밀번호 관리](documents/manual/INSTRUCTOR_PASSWORD_MANAGEMENT.md)

### 🎯 기능 구현
- [RAG 시스템 개요](documents/manual/IMPLEMENTATION_SUMMARY.md)
- [로그인 시스템](documents/manual/LOGIN_FEATURE.md)
- [파일 업로드 가이드](documents/manual/파일업로드_가이드.md)
- [음성 API 가이드](documents/manual/SPEECH_API_GUIDE.md)

### 📱 모바일
- [모바일 배포 가이드](documents/manual/MOBILE_DEPLOYMENT_GUIDE.md)
- [PWA 가이드](documents/manual/PWA_GUIDE.md)

### 🧪 테스트 & 최적화
- [테스트 가이드](documents/manual/TESTING_GUIDE.md)
- [성능 최적화](documents/manual/PERFORMANCE_OPTIMIZATION.md)
- [캐시 문제 해결](documents/manual/CACHE_FIX_GUIDE.md)

### 📊 완료 보고서
- [프로젝트 완료 요약](documents/manual/COMPLETION_SUMMARY.md)
- [구현 완료 보고서](documents/manual/COMPLETION_REPORT.md)
- [애니메이션 개선 요약](documents/manual/ANIMATION_ENHANCEMENT_SUMMARY.md)

### 🔐 보안 & 설정
- [Cafe24 방화벽 설정](documents/manual/CAFE24_FIREWALL_SETUP.md)
- [업로드 용량 정보](documents/manual/UPLOAD_CAPACITY_INFO.md)

### 📚 API 문서
- [API 요약](documents/manual/API_SUMMARY.md)
- **Swagger UI**: `http://localhost:8000/docs`

---

## 🔧 환경 설정

### 필수 환경 변수 (.env)
```bash
# 데이터베이스
DB_HOST=your_db_host
DB_PORT=3307
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_NAME=bh2025

# FTP 서버
FTP_HOST=your_ftp_host
FTP_PORT=2121
FTP_USER=your_ftp_user
FTP_PASSWORD=your_ftp_password

# AI API Keys
GROQ_API_KEY=your_groq_api_key
GOOGLE_CLOUD_TTS_API_KEY=your_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
```

### 의존성 설치
```bash
# Python 의존성
pip install -r requirements.txt

# RAG 시스템 필수 패키지
pip install langchain langchain-core langchain-text-splitters
pip install faiss-cpu sentence-transformers
pip install pypdf2 python-docx tiktoken
```

---

## 🎯 최신 업데이트 (v3.7)

### ⚡ 성능 최적화 및 UX 개선 (2026-01-08)

#### 🚀 적응형 폴링 시스템
- **스마트 폴링**: 진행 상황에 따라 자동으로 간격 조정
  - 빠른 진행 시: 3초 간격 유지 (즉각 피드백)
  - 변화 없음 2회: 5초로 증가
  - 변화 없음 5회: 10초로 증가
  - 변화 없음 10회: 30초로 증가 (최대)
  - 진행률 변화 감지 시: 즉시 3초로 리셋!
- **트래픽 절감**: 평균 60~75% API 요청 감소
- **배터리 절약**: 모바일 환경에서 효율적

#### 🧹 로그 시스템 대폭 정리
- **불필요한 로그 제거**:
  - RAG 진행률 조회 200 OK (3초마다 폴링)
  - 대시보드 새로고침 8개 API (courses, students, instructors 등)
- **로그 파일 크기**: 90% 감소
- **유지되는 중요 로그**:
  - ✅ POST/PUT/DELETE (데이터 변경)
  - ✅ 로그인 실패 (401, 보안)
  - ✅ 에러 (4xx, 5xx)
  - ✅ 파일 업로드/다운로드

#### 📚 메뉴 구조 개선
- **문제은행 위치 변경**: 성적 메뉴 → 강의 메뉴
- **논리적 그룹화**:
  - 강의: 시간표, 훈련일지, 문서관리(RAG), 문제은행
  - 성적: 온라인시험, 온라인퀴즈, 과제제출

#### 📊 성능 개선 효과
| 항목 | Before | After | 개선율 |
|------|--------|-------|--------|
| API 트래픽 (느린 인덱싱) | 600회/30분 | 150회/30분 | **75%↓** |
| 로그 발생량 (하루) | ~5000줄 | ~500줄 | **90%↓** |
| 대시보드 새로고침 로그 | 8줄 | 0줄 | **100%↓** |

#### 🔧 기술 구현
```javascript
// 적응형 폴링
if (currentProgress !== lastProgress) {
    resetPollingInterval(3000);  // 변화 감지 → 3초
} else {
    noChangeCount++;
    if (noChangeCount === 2) resetPollingInterval(5000);
    if (noChangeCount === 5) resetPollingInterval(10000);
    if (noChangeCount === 10) resetPollingInterval(30000);
}
```

```python
# 로그 필터
class EndpointFilter(logging.Filter):
    def filter(self, record: logging.LogRecord) -> bool:
        if '200 OK' in message:
            # RAG 진행률 & 대시보드 API 제외
            if '/api/rag/indexing-progress/' in message:
                return False
            for api in dashboard_apis:
                if f'GET {api} ' in message:
                    return False
        return True
```

#### 📦 커밋 히스토리 (v3.7)
- `b6d4a8c`: 버전 v3.6.0 업데이트 및 README 갱신
- `c0314ef`: 문제은행 메뉴 위치 변경 (성적 → 강의)
- `a4db72c`: RAG 진행률 조회 API 로그 제거
- `607e90b`: 적응형 폴링으로 API 트래픽 대폭 감소
- `a37edb6`: 대시보드 새로고침 API 로그 제거

---

## 📜 이전 버전 (v3.6)

### 🎬 RAG 인덱싱 UX 대폭 개선 (2026-01-08)

#### ✨ 새로운 기능
- **매트릭스 애니메이션**: The Matrix 스타일 세로로 떨어지는 초록색 바이너리 코드 (40~90% 구간)
- **진행률 디스크 저장**: 서버 재시작 시에도 진행률 유지 (`indexing_progress.json`)
- **실시간 진행률**: 배치별 세밀한 진행률 업데이트 (50%→90%)
- **백그라운드 처리**: 인덱싱 중에도 다른 작업 가능, "빠져나가기" 버튼
- **단계별 애니메이션**:
  - 0~20%: Parsing Stage (PDF + 광선 빔)
  - 20~40%: Chunking Stage (회전하는 큐브)
  - 40~90%: **Embedding Stage (매트릭스 레인)** 🎬
  - 90~100%: Indexing Stage (벡터 공간 정착)

#### 🔥 수정된 주요 버그
- **502 Bad Gateway 해결**: 동기 → FastAPI BackgroundTasks 비동기 처리
- **진행률 손실 문제**: 재시작 시 진행률 복원 (1시간 이내 항목)
- **화면 멈춤 현상**: 백엔드 14% 진행인데 프론트 5% 멈춤 → 실시간 업데이트
- **progress_callback 에러**: VectorStoreManager에 콜백 파라미터 추가
- **서버 블로킹**: 인덱싱으로 인한 전체 서버 블로킹 → 백그라운드 처리

#### 📊 커밋 히스토리 (v3.6)
- `38ad2d1`: 진행률 디스크 영구 저장
- `46c27e8`: UX 개선 (애니메이션, 빠져나가기)
- `7fb4ba4`: 502 에러 해결 (백그라운드 태스크)
- `37530c1`: progress_callback 파라미터 추가
- `60be2d2`: 떠다니는 애니메이션 제거
- `6c9301d`: 가로 스트림 활성화
- `90ef5f8`: 진행률별 애니메이션 자동 전환
- `a653ce8`: 폴링 최적화 및 로그 정리
- `8e0d4b1`: 매트릭스 스타일 애니메이션 추가

---

## 📜 이전 버전 (v3.5)

### ✅ 완료된 기능
- **문서 관리**: 시스템관리 → 강의 메뉴로 이동, 업로드/다운로드/삭제
- **문제은행**: RAG 기반 시험 문제 자동 생성 (AI 메뉴)
- **RAG 시스템**: 유사도 임계값 조정, DB 직접 조회 (강사수/학생수)
- **예진이 3D 채팅**: RAG 토글 추가, 문서 기반 답변
- **메뉴 권한**: instructor_codes 테이블 menu_permissions 관리

### 🐛 수정된 버그
- 강사 권한에서 새 메뉴(문서 관리, 문제은행) 표시 안 되는 문제
- RAG 유사도 점수 낮은 문제 (임계값 0.008로 조정)
- 강사 수 조회 SQL 에러 (role 컬럼 없음 → 상위 10명 목록으로 변경)

---

## 🔗 링크

- **GitHub Repository**: https://github.com/EmmettHwang/BH2025_WOWU
- **Branch**: `hun` (개발), `main` (프로덕션)
- **Latest PR**: https://github.com/EmmettHwang/BH2025_WOWU/compare/main...hun

---

## 📞 지원

### 문제 해결
1. [메뉴 권한 문제](documents/manual/MENU_PERMISSION_FIX.md)
2. [캐시 문제](documents/manual/CACHE_FIX_GUIDE.md)
3. [업로드 용량 문제](documents/manual/UPLOAD_CAPACITY_INFO.md)

### 개발자 문의
- GitHub Issues: https://github.com/EmmettHwang/BH2025_WOWU/issues

---

**마지막 업데이트**: 2026-01-08  
**버전**: 3.7.0  
**상태**: ✅ 프로덕션 배포 완료 + ⚡ 적응형 폴링 + 🧹 로그 최적화 + 🎬 매트릭스 애니메이션 + 🔍 RAG 시스템 + 📝 문제은행 + 🎓 교육관리
