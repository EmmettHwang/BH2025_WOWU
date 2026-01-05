#!/bin/bash
# ==================== BH2025 WOWU 서버 시작 스크립트 ====================
# Cafe24 리눅스 서버 배포용
# 사용법: bash start.sh [옵션]
# 옵션:
#   --port PORT    : 포트 번호 (기본: 8000)
#   --workers NUM  : 워커 수 (기본: 4)
#   --reload       : 개발 모드 (코드 변경 시 자동 재시작)

set -e

# 기본 설정
PORT=8000
WORKERS=4
RELOAD_FLAG=""

# 인자 파싱
while [[ $# -gt 0 ]]; do
    case $1 in
        --port)
            PORT="$2"
            shift 2
            ;;
        --workers)
            WORKERS="$2"
            shift 2
            ;;
        --reload)
            RELOAD_FLAG="--reload"
            shift
            ;;
        *)
            echo "알 수 없는 옵션: $1"
            echo "사용법: bash start.sh [--port PORT] [--workers NUM] [--reload]"
            exit 1
            ;;
    esac
done

echo "============================================================"
echo "  BH2025 WOWU 서버 시작"
echo "============================================================"
echo ""

# 1. 가상환경 확인
if [ ! -d "venv" ]; then
    echo "❌ 가상환경이 없습니다. 먼저 setup.sh를 실행하세요."
    echo "   bash setup.sh"
    exit 1
fi

# 2. 가상환경 활성화
echo "[1/3] 가상환경 활성화..."
source venv/bin/activate
echo "✅ 가상환경 활성화 완료"
echo ""

# 3. .env 파일 확인
echo "[2/3] 환경 설정 확인..."
if [ ! -f "backend/.env" ]; then
    echo "❌ backend/.env 파일이 없습니다."
    echo "📝 .env.example을 참고하여 설정하세요:"
    echo "   cp backend/.env.example backend/.env"
    echo "   nano backend/.env"
    exit 1
fi
echo "✅ 환경 설정 확인 완료"
echo ""

# 4. 서버 시작
echo "[3/3] 서버 시작..."
echo ""
echo "설정:"
echo "  포트: $PORT"
echo "  워커: $WORKERS"
if [ -n "$RELOAD_FLAG" ]; then
    echo "  모드: 개발 모드 (자동 재시작)"
else
    echo "  모드: 운영 모드"
fi
echo ""
echo "============================================================"
echo "  ✅ 서버 URL: http://0.0.0.0:$PORT"
echo "  📚 API 문서: http://0.0.0.0:$PORT/docs"
echo "============================================================"
echo ""

cd backend

if [ -n "$RELOAD_FLAG" ]; then
    # 개발 모드
    uvicorn main:app --host 0.0.0.0 --port $PORT --reload
else
    # 운영 모드
    uvicorn main:app --host 0.0.0.0 --port $PORT --workers $WORKERS
fi
