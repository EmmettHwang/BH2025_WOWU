#!/bin/bash
# ==================== BH2025 WOWU 서버 셋업 스크립트 ====================
# Cafe24 리눅스 서버 배포용
# 사용법: bash setup.sh

set -e  # 에러 발생 시 중단

echo "============================================================"
echo "  BH2025 WOWU 서버 셋업"
echo "  Cafe24 리눅스 배포용"
echo "============================================================"
echo ""

# 1. Python 버전 확인
echo "[1/7] Python 버전 확인..."
python3 --version
if [ $? -ne 0 ]; then
    echo "❌ Python3가 설치되지 않았습니다."
    exit 1
fi
echo "✅ Python3 확인 완료"
echo ""

# 2. 가상환경 생성
echo "[2/7] Python 가상환경 생성..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ 가상환경 생성 완료"
else
    echo "✅ 가상환경이 이미 존재합니다"
fi
echo ""

# 3. 가상환경 활성화
echo "[3/7] 가상환경 활성화..."
source venv/bin/activate
echo "✅ 가상환경 활성화 완료"
echo ""

# 4. pip 업그레이드
echo "[4/7] pip 업그레이드..."
pip install --upgrade pip
echo "✅ pip 업그레이드 완료"
echo ""

# 5. 필수 패키지 설치
echo "[5/7] 필수 패키지 설치..."
cd backend

# 먼저 기본 패키지 설치
pip install wheel setuptools

# requirements.txt 설치
if [ -f "requirements.txt" ]; then
    echo "📦 requirements.txt 설치 중..."
    pip install -r requirements.txt
    echo "✅ requirements.txt 설치 완료"
else
    echo "❌ requirements.txt를 찾을 수 없습니다"
    exit 1
fi

cd ..
echo ""

# 6. 필수 디렉토리 생성
echo "[6/7] 필수 디렉토리 생성..."
mkdir -p backend/documents
mkdir -p backend/uploads
mkdir -p backend/vector_db
mkdir -p backend/logs
echo "✅ 필수 디렉토리 생성 완료"
echo ""

# 7. 환경 변수 파일 확인
echo "[7/7] 환경 변수 파일 확인..."
if [ ! -f "backend/.env" ]; then
    if [ -f "backend/.env.example" ]; then
        echo "⚠️  .env 파일이 없습니다."
        echo "📝 .env.example을 참고하여 backend/.env 파일을 생성하세요."
        echo ""
        echo "   cp backend/.env.example backend/.env"
        echo "   nano backend/.env  # 설정 값 입력"
        echo ""
    else
        echo "⚠️  .env.example 파일도 없습니다."
    fi
else
    echo "✅ .env 파일 확인 완료"
fi
echo ""

# 완료
echo "============================================================"
echo "  ✅ 셋업 완료!"
echo "============================================================"
echo ""
echo "📝 다음 단계:"
echo "  1. backend/.env 파일 설정 (cp backend/.env.example backend/.env)"
echo "  2. 데이터베이스 정보 입력"
echo "  3. API 키 입력 (GROQ_API_KEY 필수)"
echo "  4. 서버 시작: bash start.sh"
echo ""
echo "============================================================"
