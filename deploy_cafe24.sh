#!/bin/bash

# Cafe24 서버 자동 배포 스크립트
# 사용법: bash deploy_cafe24.sh

echo "======================================"
echo "  교육관리시스템 Cafe24 배포 스크립트"
echo "======================================"
echo ""

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 1. 프로젝트 디렉토리 확인
if [ ! -f "backend/main.py" ]; then
    echo -e "${RED}❌ 오류: backend/main.py 파일을 찾을 수 없습니다.${NC}"
    echo "프로젝트 루트 디렉토리에서 실행해주세요."
    exit 1
fi

echo -e "${GREEN}✅ 프로젝트 디렉토리 확인 완료${NC}"

# 2. Python 버전 확인
PYTHON_VERSION=$(python3.11 --version 2>/dev/null || python3 --version 2>/dev/null)
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Python 3.11이 설치되어 있지 않습니다.${NC}"
    echo "설치 명령어: sudo yum install python3.11 -y"
    exit 1
fi
echo -e "${GREEN}✅ Python 버전: $PYTHON_VERSION${NC}"

# 3. 가상환경 확인 및 생성
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚙️  가상환경 생성 중...${NC}"
    python3.11 -m venv venv
    if [ $? -ne 0 ]; then
        echo -e "${RED}❌ 가상환경 생성 실패${NC}"
        exit 1
    fi
    echo -e "${GREEN}✅ 가상환경 생성 완료${NC}"
else
    echo -e "${GREEN}✅ 가상환경 이미 존재함${NC}"
fi

# 4. 가상환경 활성화
echo -e "${YELLOW}⚙️  가상환경 활성화 중...${NC}"
source venv/bin/activate

# 5. 의존성 설치
echo -e "${YELLOW}⚙️  Python 패키지 설치 중...${NC}"
pip install --upgrade pip -q
pip install -r backend/requirements.txt -q
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ 패키지 설치 실패${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 패키지 설치 완료${NC}"

# 6. .env 파일 확인
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  .env 파일이 없습니다.${NC}"
    echo -e "${YELLOW}⚙️  .env 파일 생성 중...${NC}"
    read -p "OpenAI API Key를 입력하세요: " OPENAI_KEY
    cat > .env << EOF
OPENAI_API_KEY=$OPENAI_KEY
EOF
    echo -e "${GREEN}✅ .env 파일 생성 완료${NC}"
else
    echo -e "${GREEN}✅ .env 파일 확인 완료${NC}"
fi

# 7. PM2 확인
if ! command -v pm2 &> /dev/null; then
    echo -e "${YELLOW}⚠️  PM2가 설치되어 있지 않습니다.${NC}"
    echo "설치 명령어: npm install -g pm2"
    echo ""
    echo "PM2 없이 계속하시겠습니까? (y/n)"
    read -p "> " CONTINUE
    if [ "$CONTINUE" != "y" ]; then
        exit 1
    fi
    USE_PM2=false
else
    USE_PM2=true
    echo -e "${GREEN}✅ PM2 확인 완료${NC}"
fi

# 8. 포트 8000 확인 및 정리
echo -e "${YELLOW}⚙️  포트 8000 확인 중...${NC}"
PORT_PID=$(lsof -ti:8000 2>/dev/null)
if [ ! -z "$PORT_PID" ]; then
    echo -e "${YELLOW}⚠️  포트 8000이 사용 중입니다. 종료하시겠습니까? (y/n)${NC}"
    read -p "> " KILL_PORT
    if [ "$KILL_PORT" = "y" ]; then
        kill -9 $PORT_PID 2>/dev/null
        echo -e "${GREEN}✅ 기존 프로세스 종료 완료${NC}"
    fi
fi

# 9. 서비스 시작
echo ""
echo -e "${YELLOW}⚙️  서비스 시작 중...${NC}"
cd backend

if [ "$USE_PM2" = true ]; then
    # PM2로 시작
    pm2 delete bhhs-backend 2>/dev/null
    pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name bhhs-backend
    pm2 save
    
    echo ""
    echo -e "${GREEN}✅ 배포 완료!${NC}"
    echo ""
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo -e "${GREEN}🎉 교육관리시스템이 성공적으로 배포되었습니다!${NC}"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo ""
    echo "📊 서비스 상태 확인:"
    pm2 list
    echo ""
    echo "🔗 접속 URL:"
    echo "   http://$(hostname -I | awk '{print $1}'):8000"
    echo "   http://localhost:8000"
    echo ""
    echo "📝 유용한 명령어:"
    echo "   pm2 logs bhhs-backend     # 로그 확인"
    echo "   pm2 restart bhhs-backend  # 재시작"
    echo "   pm2 stop bhhs-backend     # 중지"
    echo "   pm2 delete bhhs-backend   # 삭제"
    echo ""
else
    # 일반 실행
    echo -e "${YELLOW}PM2 없이 실행합니다. Ctrl+C로 중지할 수 있습니다.${NC}"
    uvicorn main:app --host 0.0.0.0 --port 8000
fi
