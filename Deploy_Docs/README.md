# 📚 배포 문서 모음

BH2025 WOWU 프로젝트의 배포 및 서버 관리 관련 문서 모음입니다.

---

## 📖 문서 목록

### 1. 🚀 [전체 배포 가이드](./01_DEPLOYMENT_GUIDE.md)
완전히 새로운 서버에 프로젝트를 배포하는 전체 과정을 단계별로 설명합니다.

**주요 내용:**
- 배포 전체 순서 및 체크리스트
- 각 단계별 상세 설명
- 전체 명령어 스크립트
- 배포 후 확인 사항

**대상:** 새 서버에 처음 배포하는 경우

---

### 2. ⚙️ [서버 초기 설정](./02_SERVER_SETUP.md)
서버 임대 후 기본 환경을 설정하는 방법을 다룹니다.

**주요 내용:**
- 서버 업데이트 및 보안 설정
- 필수 패키지 설치 (Git, Python, Node.js)
- 방화벽 및 보안 설정
- 사용자 계정 관리

**대상:** 서버 관리자, DevOps

---

### 3. 🌐 [Nginx 설정](./03_NGINX_CONFIG.md)
Nginx 웹 서버 설치 및 설정 방법을 상세히 설명합니다.

**주요 내용:**
- Nginx 설치 및 기본 설정
- 프록시 설정 (포트 포워딩)
- 파일 업로드 크기 제한
- SSL/HTTPS 설정
- 설정 파일 예제

**대상:** 웹 서버 관리자

---

### 4. 🔧 [PM2 프로세스 관리](./04_PM2_MANAGEMENT.md)
PM2를 사용한 애플리케이션 프로세스 관리 가이드입니다.

**주요 내용:**
- PM2 설치 및 기본 사용법
- ecosystem.config.cjs 설정
- 프로세스 시작/중지/재시작
- 로그 관리
- 자동 시작 설정
- 모니터링

**대상:** 개발자, 운영팀

---

### 5. 🐛 [문제 해결 가이드](./05_TROUBLESHOOTING.md)
배포 및 운영 중 발생할 수 있는 문제들과 해결 방법을 정리했습니다.

**주요 내용:**
- 포트 충돌 문제
- 데이터베이스 연결 오류
- FTP 연결 문제
- 파일 업로드 오류
- 메모리/CPU 이슈
- 로그 확인 방법

**대상:** 모든 사용자

---

### 6. 🔄 [코드 업데이트 워크플로우](./06_UPDATE_WORKFLOW.md)
이미 배포된 서버에 새 코드를 업데이트하는 방법입니다.

**주요 내용:**
- Git을 통한 코드 업데이트
- 의존성 패키지 업데이트
- 서버 재시작 절차
- 배포 전 체크리스트
- 롤백 방법

**대상:** 개발자, 운영팀

---

### 7. 🔐 [보안 설정 가이드](./07_SECURITY_GUIDE.md)
서버 보안을 강화하는 방법을 다룹니다.

**주요 내용:**
- SSH 키 인증 설정
- 방화벽 설정 (UFW)
- SSL/TLS 인증서
- 환경변수 보안 관리
- 데이터베이스 보안
- 정기 보안 업데이트

**대상:** 서버 관리자, 보안 담당자

---

### 8. 📊 [모니터링 및 로그 관리](./08_MONITORING_LOGS.md)
서버 상태 모니터링 및 로그 관리 방법입니다.

**주요 내용:**
- PM2 모니터링
- Nginx 로그 분석
- 애플리케이션 로그
- 시스템 리소스 모니터링
- 알림 설정

**대상:** 운영팀, DevOps

---

## 🎯 시나리오별 가이드

### 📌 처음 서버를 배포하는 경우
1. [02_SERVER_SETUP.md](./02_SERVER_SETUP.md) - 서버 기본 설정
2. [01_DEPLOYMENT_GUIDE.md](./01_DEPLOYMENT_GUIDE.md) - 전체 배포
3. [03_NGINX_CONFIG.md](./03_NGINX_CONFIG.md) - Nginx 설정
4. [04_PM2_MANAGEMENT.md](./04_PM2_MANAGEMENT.md) - PM2 설정
5. [07_SECURITY_GUIDE.md](./07_SECURITY_GUIDE.md) - 보안 설정

### 📌 코드를 업데이트하는 경우
1. [06_UPDATE_WORKFLOW.md](./06_UPDATE_WORKFLOW.md) - 업데이트 절차
2. [04_PM2_MANAGEMENT.md](./04_PM2_MANAGEMENT.md) - 재시작 방법

### 📌 문제가 발생한 경우
1. [05_TROUBLESHOOTING.md](./05_TROUBLESHOOTING.md) - 문제 해결
2. [08_MONITORING_LOGS.md](./08_MONITORING_LOGS.md) - 로그 확인

### 📌 서버를 안전하게 관리하려는 경우
1. [07_SECURITY_GUIDE.md](./07_SECURITY_GUIDE.md) - 보안 설정
2. [08_MONITORING_LOGS.md](./08_MONITORING_LOGS.md) - 모니터링

---

## 🔗 관련 문서

### 프로젝트 루트 문서
- `README.md` - 프로젝트 전체 설명
- `LOCAL_DEVELOPMENT.md` - 로컬 개발 환경
- `CONDA_SETUP.md` - Conda 환경 설정
- `파일업로드_가이드.md` - 파일 업로드 안내
- `UPLOAD_CAPACITY_INFO.md` - 업로드 용량 정보

### 설정 파일
- `ecosystem.config.cjs` - PM2 설정
- `backend/main.py` - 백엔드 메인 파일
- `frontend/proxy-server.cjs` - 프론트엔드 프록시 서버

---

## 📞 지원

배포 관련 문제가 발생하면:

1. **문제 해결 가이드 확인**: [05_TROUBLESHOOTING.md](./05_TROUBLESHOOTING.md)
2. **로그 확인**: [08_MONITORING_LOGS.md](./08_MONITORING_LOGS.md)
3. **GitHub Issues**: https://github.com/EmmettHwang/BH2025_WOWU/issues

---

## 📝 문서 기여

배포 문서 개선을 위한 기여를 환영합니다!

1. 문서 수정 또는 추가
2. Pull Request 생성
3. 리뷰 및 반영

---

## 🔄 문서 업데이트 이력

| 날짜 | 버전 | 내용 |
|-----|------|-----|
| 2024-12-XX | 1.0.0 | 초기 배포 문서 작성 |

---

**마지막 업데이트**: 2024-12-XX  
**관리자**: EmmettHwang  
**프로젝트**: BH2025 WOWU - 바이오헬스교육관리시스템
