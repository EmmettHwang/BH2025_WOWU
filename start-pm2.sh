#!/bin/bash
# ==================== PM2로 BH2025 서버 시작 ====================
# 사용법: bash start-pm2.sh [옵션]
# 옵션:
#   --setup    : 최초 설정 (가상환경 생성 및 패키지 설치)
#   --update   : 코드 업데이트 후 재시작
#   --stop     : 서버 중지
#   --restart  : 서버 재시작
#   --logs     : 로그 보기
#   --status   : 상태 확인

set -e

ACTION="start"

# 인자 파싱
if [ $# -gt 0 ]; then
    case $1 in
        --setup)
            ACTION="setup"
            ;;
        --update)
            ACTION="update"
            ;;
        --stop)
            ACTION="stop"
            ;;
        --restart)
            ACTION="restart"
            ;;
        --logs)
            ACTION="logs"
            ;;
        --status)
            ACTION="status"
            ;;
        *)
            echo "알 수 없는 옵션: $1"
            echo "사용법: bash start-pm2.sh [--setup|--update|--stop|--restart|--logs|--status]"
            exit 1
            ;;
    esac
fi

echo "============================================================"
echo "  BH2025 WOWU PM2 관리"
echo "  실행: $ACTION"
echo "============================================================"
echo ""

# Setup 모드
if [ "$ACTION" = "setup" ]; then
    echo "[1/5] Python 버전 확인..."
    python3 --version
    
    echo ""
    echo "[2/5] 가상환경 생성..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        echo "✅ 가상환경 생성 완료"
    else
        echo "✅ 가상환경이 이미 존재합니다"
    fi
    
    echo ""
    echo "[3/5] 패키지 설치..."
    source venv/bin/activate
    pip install --upgrade pip
    cd backend
    pip install -r requirements.txt
    cd ..
    
    echo ""
    echo "[4/5] 필수 디렉토리 생성..."
    mkdir -p backend/documents backend/uploads backend/vector_db logs
    
    echo ""
    echo "[5/5] 환경 설정 확인..."
    if [ ! -f "backend/.env" ]; then
        echo "⚠️  backend/.env 파일이 없습니다"
        echo "📝 backend/.env.example을 참고하여 설정하세요:"
        echo "   cp backend/.env.example backend/.env"
        echo "   nano backend/.env"
    else
        echo "✅ backend/.env 파일 확인 완료"
    fi
    
    echo ""
    echo "============================================================"
    echo "  ✅ 설정 완료!"
    echo "  다음: bash start-pm2.sh (서버 시작)"
    echo "============================================================"
    exit 0
fi

# Stop 모드
if [ "$ACTION" = "stop" ]; then
    echo "PM2 서버 중지 중..."
    pm2 stop bh2025-backend 2>/dev/null || echo "⚠️  실행 중인 서버가 없습니다"
    echo "✅ 완료"
    exit 0
fi

# Restart 모드
if [ "$ACTION" = "restart" ]; then
    echo "PM2 서버 재시작 중..."
    pm2 restart bh2025-backend
    echo "✅ 완료"
    echo ""
    echo "로그 확인: pm2 logs bh2025-backend"
    exit 0
fi

# Logs 모드
if [ "$ACTION" = "logs" ]; then
    pm2 logs bh2025-backend
    exit 0
fi

# Status 모드
if [ "$ACTION" = "status" ]; then
    pm2 status
    echo ""
    echo "상세 정보: pm2 show bh2025-backend"
    exit 0
fi

# Update 모드
if [ "$ACTION" = "update" ]; then
    echo "[1/4] 최신 코드 받기..."
    git pull origin hun
    
    echo ""
    echo "[2/4] 패키지 업데이트..."
    source venv/bin/activate
    cd backend
    pip install -r requirements.txt --upgrade
    cd ..
    
    echo ""
    echo "[3/4] PM2 재시작..."
    pm2 restart bh2025-backend
    
    echo ""
    echo "[4/4] 로그 확인..."
    sleep 2
    pm2 logs bh2025-backend --lines 50 --nostream
    
    echo ""
    echo "============================================================"
    echo "  ✅ 업데이트 완료!"
    echo "============================================================"
    exit 0
fi

# Start 모드 (기본)
echo "[1/4] PM2 설치 확인..."
if ! command -v pm2 &> /dev/null; then
    echo "❌ PM2가 설치되지 않았습니다"
    echo "설치: npm install -g pm2"
    exit 1
fi
echo "✅ PM2 확인 완료"

echo ""
echo "[2/4] .env 파일 확인..."
if [ ! -f "backend/.env" ]; then
    echo "❌ backend/.env 파일이 없습니다"
    echo "📝 설정 필요: bash start-pm2.sh --setup"
    exit 1
fi
echo "✅ 환경 설정 확인 완료"

echo ""
echo "[3/4] PM2로 서버 시작..."
pm2 start ecosystem.config.js

echo ""
echo "[4/4] 상태 확인..."
sleep 2
pm2 status

echo ""
echo "============================================================"
echo "  ✅ 서버 시작 완료!"
echo "============================================================"
echo ""
echo "📝 유용한 명령어:"
echo "  pm2 logs bh2025-backend        # 로그 보기"
echo "  pm2 restart bh2025-backend     # 재시작"
echo "  pm2 stop bh2025-backend        # 중지"
echo "  pm2 monit                      # 모니터링"
echo ""
echo "또는:"
echo "  bash start-pm2.sh --logs       # 로그 보기"
echo "  bash start-pm2.sh --restart    # 재시작"
echo "  bash start-pm2.sh --stop       # 중지"
echo "  bash start-pm2.sh --status     # 상태 확인"
echo "  bash start-pm2.sh --update     # 코드 업데이트 후 재시작"
echo ""
echo "============================================================"
