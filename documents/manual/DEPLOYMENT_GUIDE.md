# Google Cloud Run 배포 가이드

## 📋 개요
이 가이드는 교육관리시스템을 Google Cloud Run에 배포하는 방법을 설명합니다.

## 🎯 배포 아키텍처
- **컨테이너**: Docker (FastAPI 백엔드 + Vanilla JS 프론트엔드)
- **플랫폼**: Google Cloud Run (서버리스, 자동 스케일링)
- **데이터베이스**: 외부 MySQL (bitnmeta2.synology.me:3307)
- **스토리지**: 외부 FTP (bitnmeta2.synology.me:2121)

## 📦 사전 준비

### 1. 필요한 도구 설치

```bash
# 1. Docker 설치
# Windows: https://www.docker.com/products/docker-desktop
# macOS: https://www.docker.com/products/docker-desktop
# Linux: sudo apt-get install docker.io

# 2. Google Cloud SDK 설치
# https://cloud.google.com/sdk/docs/install

# 설치 확인
docker --version
gcloud --version
```

### 2. Google Cloud 프로젝트 설정

```bash
# Google Cloud 로그인
gcloud auth login

# 프로젝트 생성 (또는 기존 프로젝트 사용)
gcloud projects create bhhs-edu-system --name="교육관리시스템"

# 프로젝트 설정
gcloud config set project bhhs-edu-system

# 필요한 API 활성화
gcloud services enable run.googleapis.com
gcloud services enable containerregistry.googleapis.com
gcloud services enable cloudbuild.googleapis.com

# 결제 계정 연결 (필수)
# https://console.cloud.google.com/billing 에서 설정
```

## 🚀 배포 단계

### 단계 1: 환경 변수 설정

```bash
# .env 파일 확인 (프로젝트 루트에 있어야 함)
cat .env

# 필요한 환경 변수:
# OPENAI_API_KEY=sk-...
# (데이터베이스 정보는 코드에 하드코딩되어 있음)
```

### 단계 2: Docker 이미지 빌드 및 테스트

```bash
# 프로젝트 루트로 이동
cd /path/to/webapp

# Docker 이미지 빌드
docker build -t bhhs-edu-system .

# 로컬에서 테스트
docker run -p 8080:8080 --env-file .env bhhs-edu-system

# 브라우저에서 확인: http://localhost:8080
```

### 단계 3: Google Container Registry에 이미지 푸시

```bash
# 프로젝트 ID 확인
PROJECT_ID=$(gcloud config get-value project)
echo $PROJECT_ID

# Docker 이미지 태그
docker tag bhhs-edu-system gcr.io/$PROJECT_ID/bhhs-edu-system:v1

# Google Container Registry에 푸시
docker push gcr.io/$PROJECT_ID/bhhs-edu-system:v1
```

### 단계 4: Cloud Run에 배포

```bash
# 환경 변수와 함께 배포
gcloud run deploy bhhs-edu-system \
  --image gcr.io/$PROJECT_ID/bhhs-edu-system:v1 \
  --platform managed \
  --region asia-northeast3 \
  --allow-unauthenticated \
  --port 8080 \
  --memory 512Mi \
  --cpu 1 \
  --timeout 300 \
  --max-instances 10 \
  --set-env-vars "OPENAI_API_KEY=sk-your-key-here"

# 배포 완료 후 URL 확인
# 예: https://bhhs-edu-system-xxxx-an.a.run.app
```

## 🔧 추가 설정

### 1. 커스텀 도메인 연결

```bash
# 도메인 매핑
gcloud run domain-mappings create \
  --service bhhs-edu-system \
  --domain edu.yourdomain.com \
  --region asia-northeast3

# DNS 레코드 추가 (도메인 제공업체에서)
# A 레코드: ghs.googlehosted.com
```

### 2. 환경 변수 업데이트

```bash
# 환경 변수 수정
gcloud run services update bhhs-edu-system \
  --update-env-vars "OPENAI_API_KEY=new-key" \
  --region asia-northeast3
```

### 3. 자동 스케일링 설정

```bash
# 최소/최대 인스턴스 설정
gcloud run services update bhhs-edu-system \
  --min-instances 0 \
  --max-instances 10 \
  --region asia-northeast3
```

## 📊 모니터링 및 로그

### 로그 확인

```bash
# 실시간 로그 스트리밍
gcloud run services logs read bhhs-edu-system \
  --region asia-northeast3 \
  --follow

# 최근 로그 50줄
gcloud run services logs read bhhs-edu-system \
  --region asia-northeast3 \
  --limit 50
```

### Cloud Console 모니터링

```
https://console.cloud.google.com/run/detail/asia-northeast3/bhhs-edu-system
```

## 💰 비용 예상

### 무료 할당량 (매월)
- 요청 수: 200만 건
- CPU 시간: 360,000 vCPU-초
- 메모리: 360,000 GiB-초
- 네트워크(송신): 1 GiB

### 초과 시 요금
- 요청: $0.40 / 백만 건
- CPU: $0.00002400 / vCPU-초
- 메모리: $0.00000250 / GiB-초

**예상 비용**: 소규모 사용 시 무료 할당량 내에서 운영 가능

## 🔐 보안 고려사항

### 1. 데이터베이스 보안
```bash
# Cloud SQL Proxy 사용 권장 (현재는 외부 MySQL 직접 연결)
# 외부 MySQL 서버의 방화벽 설정 확인
# Cloud Run의 IP 주소를 MySQL 서버 화이트리스트에 추가
```

### 2. 환경 변수 보안
```bash
# Secret Manager 사용 (권장)
# 1. Secret 생성
echo -n "sk-your-openai-key" | gcloud secrets create openai-api-key --data-file=-

# 2. Cloud Run에 권한 부여
gcloud run services add-iam-policy-binding bhhs-edu-system \
  --member=serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com \
  --role=roles/secretmanager.secretAccessor \
  --region asia-northeast3

# 3. Secret 사용하여 배포
gcloud run deploy bhhs-edu-system \
  --image gcr.io/$PROJECT_ID/bhhs-edu-system:v1 \
  --update-secrets OPENAI_API_KEY=openai-api-key:latest \
  --region asia-northeast3
```

### 3. 인증 추가
```bash
# 퍼블릭 액세스 제거 (인증 필요)
gcloud run services remove-iam-policy-binding bhhs-edu-system \
  --member="allUsers" \
  --role="roles/run.invoker" \
  --region asia-northeast3
```

## 🔄 업데이트 및 재배포

### 코드 변경 후 재배포

```bash
# 1. Docker 이미지 재빌드
docker build -t gcr.io/$PROJECT_ID/bhhs-edu-system:v2 .

# 2. 푸시
docker push gcr.io/$PROJECT_ID/bhhs-edu-system:v2

# 3. 재배포
gcloud run deploy bhhs-edu-system \
  --image gcr.io/$PROJECT_ID/bhhs-edu-system:v2 \
  --region asia-northeast3

# 또는 자동 재배포 (git push 시)
# Cloud Build 트리거 설정 권장
```

### 롤백

```bash
# 이전 버전으로 롤백
gcloud run services update-traffic bhhs-edu-system \
  --to-revisions REVISION_NAME=100 \
  --region asia-northeast3
```

## 🧪 테스트

### 배포 후 테스트

```bash
# 배포된 URL 가져오기
SERVICE_URL=$(gcloud run services describe bhhs-edu-system \
  --region asia-northeast3 \
  --format 'value(status.url)')

# 헬스 체크
curl $SERVICE_URL/health

# API 테스트
curl $SERVICE_URL/api/instructor-codes

# 프론트엔드 확인
echo "Open: $SERVICE_URL"
```

## 🚨 트러블슈팅

### 1. 이미지 빌드 실패
```bash
# Docker 빌드 로그 확인
docker build -t test . --no-cache --progress=plain

# 의존성 문제
pip install -r backend/requirements.txt
```

### 2. 배포 실패
```bash
# Cloud Run 로그 확인
gcloud run services logs read bhhs-edu-system --region asia-northeast3 --limit 100

# 서비스 상세 정보
gcloud run services describe bhhs-edu-system --region asia-northeast3
```

### 3. 데이터베이스 연결 실패
```bash
# MySQL 서버 접근 가능 확인
telnet bitnmeta2.synology.me 3307

# Cloud Run에서 외부 접속 확인
# 방화벽 규칙 확인 필요
```

### 4. 메모리 부족
```bash
# 메모리 증가
gcloud run services update bhhs-edu-system \
  --memory 1Gi \
  --region asia-northeast3
```

## 📚 참고 자료

- [Cloud Run 공식 문서](https://cloud.google.com/run/docs)
- [Cloud Run 가격 계산기](https://cloud.google.com/products/calculator)
- [FastAPI 배포 가이드](https://fastapi.tiangolo.com/deployment/docker/)
- [Docker 공식 문서](https://docs.docker.com/)

## 🎯 대안 배포 방법

### Google App Engine
```bash
# app.yaml 생성 후
gcloud app deploy
```

### Google Compute Engine (VM)
- 더 많은 제어가 필요한 경우
- 영구 스토리지 필요 시

### Google Kubernetes Engine (GKE)
- 대규모 트래픽 처리
- 복잡한 마이크로서비스 아키텍처

---

**작성일**: 2025-11-14  
**버전**: 1.0  
**프로젝트**: 교육관리시스템 v3.3
