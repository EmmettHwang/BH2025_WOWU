# 🎉 배포 완료 문서

## 📅 배포 일시
**2025년 11월 15일**

---

## 🌐 접속 정보

### 프로덕션 URL
- **메인 도메인**: http://kdt2025.com/ ⭐
- **www 도메인**: http://www.kdt2025.com/
- **IP 주소**: http://114.202.247.97/
- **API 문서**: http://kdt2025.com/api/docs

### 로그인 정보
- **강사 계정**: `황동하` / `kdt2025`

---

## ✅ 완료된 작업

### 1. 서버 환경 구축
- ✅ Cafe24 가상서버 (Ubuntu)
- ✅ Python 3.11 + FastAPI
- ✅ PM2 프로세스 관리
- ✅ Nginx 웹서버

### 2. 도메인 연결
- ✅ DNS A 레코드: kdt2025.com → 114.202.247.97
- ✅ DNS A 레코드: www.kdt2025.com → 114.202.247.97
- ✅ Nginx server_name 설정

### 3. PWA 구현
- ✅ Service Worker (오프라인 지원)
- ✅ Web App Manifest
- ✅ PWA 아이콘 8개 (72x72 ~ 512x512)
- ✅ Apple Touch Icon (180x180)
- ✅ Favicon (16x16, 32x32, .ico)
- ✅ 반응형 디자인 (모바일 최적화)

### 4. 데이터베이스
- ✅ 외부 MySQL: bitnmeta2.synology.me:3307
- ✅ 10개 테이블 완전 구현
- ✅ 실제 데이터 입력 완료

### 5. 기능 구현
- ✅ 10개 관리 모듈 (강사, 학생, 상담, 훈련일지 등)
- ✅ AI 생활기록부 자동 생성
- ✅ Excel 업로드/다운로드
- ✅ 사진 첨부 기능 (FTP)
- ✅ 대시보드 통계

---

## 🖥️ 서버 구조

### 디렉토리 구조
```
/root/BH2025_WOWU/
├── backend/
│   ├── main.py              # FastAPI 애플리케이션
│   ├── requirements.txt     # Python 의존성
│   └── .env                 # 환경변수
├── frontend/
│   ├── index.html           # 메인 페이지
│   ├── login.html           # 로그인 페이지
│   ├── app.js               # JavaScript
│   ├── manifest.json        # PWA Manifest
│   ├── service-worker.js    # Service Worker
│   ├── pwa-styles.css       # 반응형 CSS
│   ├── icon-*.png           # PWA 아이콘들
│   ├── apple-touch-icon.png # iOS 아이콘
│   └── favicon.ico          # 파비콘
├── uploads/                 # 업로드 파일
└── README.md
```

### Nginx 설정
- **설정 파일**: `/etc/nginx/sites-available/webapp`
- **포트 80**: HTTP 접속
- **프록시**: Frontend (3000), Backend (8000)

### PM2 프로세스
```bash
pm2 list
┌────┬────────────────────┬─────────┐
│ id │ name               │ status  │
├────┼────────────────────┼─────────┤
│ 0  │ bhhs-backend       │ online  │
│ 1  │ bhhs-frontend      │ online  │
└────┴────────────────────┴─────────┘
```

---

## 🔧 서버 관리 명령어

### 서비스 재시작
```bash
# Frontend 재시작
pm2 restart bhhs-frontend

# Backend 재시작
pm2 restart bhhs-backend

# Nginx 재시작
sudo systemctl restart nginx
```

### 로그 확인
```bash
# PM2 로그
pm2 logs --nostream

# Nginx 에러 로그
sudo tail -f /var/log/nginx/error.log

# Frontend 로그
tail -f /tmp/frontend.log
```

### 코드 업데이트
```bash
cd /root/BH2025_WOWU
git pull origin main
pm2 restart all
```

---

## 📱 PWA 설치 방법

### Desktop (Chrome)
1. http://kdt2025.com/ 접속
2. 주소창 오른쪽 **"앱에서 열기"** 또는 **⊕ 아이콘** 클릭
3. "설치" 버튼 클릭
4. 독립 실행형 앱으로 실행

### Android (Chrome)
1. http://kdt2025.com/ 접속
2. **⋮** 메뉴 → **앱 설치** 또는 **홈 화면에 추가**
3. 홈 화면에 "KDT교육관리시스템 v3.0" 아이콘 생성

### iOS (Safari)
1. http://kdt2025.com/ 접속
2. 공유 버튼 (⬆️) → **홈 화면에 추가**
3. "BH2025" 아이콘으로 추가

---

## 🔒 보안 설정

### 현재 설정
- ✅ HTTP 접속 (포트 80)
- ✅ 자체 서명 SSL 인증서 생성됨 (HTTPS 대비)
- ✅ Nginx 보안 헤더 설정
- ✅ 방화벽 설정 (UFW)
- ✅ .env 파일 보호

### SSL/HTTPS (선택사항)
자체 서명 인증서가 이미 생성되어 있습니다:
- `/etc/nginx/ssl/kdt2025.com.crt`
- `/etc/nginx/ssl/kdt2025.com.key`

HTTPS를 활성화하려면 Nginx 설정에서 HTTPS 서버 블록의 주석을 해제하세요.

---

## 📊 시스템 사양

### 서버 정보
- **제공업체**: Cafe24 가상서버
- **OS**: Ubuntu 22.04 LTS
- **IP**: 114.202.247.97
- **도메인**: kdt2025.com

### 소프트웨어 버전
- **Nginx**: 1.18.0
- **Python**: 3.11
- **Node.js**: 18+
- **PM2**: 최신 버전

### 데이터베이스
- **MySQL**: 8.x
- **호스트**: bitnmeta2.synology.me:3307
- **DB명**: bh2025

---

## 🎯 주요 기능

### 관리 모듈 (10개)
1. 강사코드 관리
2. 강사 관리
3. 교과목 관리
4. 공휴일 관리
5. 과정(학급) 관리
6. 학생 관리
7. 학생상담 관리
8. 프로젝트 관리
9. 시간표 관리
10. 훈련일지 관리

### 특수 기능
- AI 생활기록부 자동 생성 (OpenAI GPT-4o-mini)
- Excel 일괄 업로드/다운로드
- 사진 첨부 (FTP 서버 연동)
- 대시보드 통계 시각화

---

## 📞 문의 및 지원

### GitHub
- **Repository**: https://github.com/Emmett6401/BH2025_WOWU
- **Issues**: 버그 리포트 및 기능 요청

### 문서
- **README.md**: 전체 시스템 개요
- **PWA_GUIDE.md**: PWA 설치 가이드
- **UPDATE_CAFE24.md**: 서버 업데이트 가이드
- **API_SUMMARY.md**: API 상세 문서

---

## 🎊 배포 성공!

**교육관리시스템 v3.6**이 성공적으로 배포되었습니다!

- 🌐 **도메인 접속**: http://kdt2025.com/
- 📱 **PWA 설치**: 주소창에서 "앱에서 열기" 클릭
- 🚀 **프로덕션 준비 완료**: 24/7 운영 가능

**2025년 11월 15일 배포 완료** ✨
