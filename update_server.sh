#!/bin/bash

# Cafe24 서버 업데이트 스크립트 (실제 경로 반영)
# 사용법: bash update_server.sh

echo "🚀 KDT 교육관리시스템 업데이트 시작..."

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m'

# 현재 디렉토리 확인
CURRENT_DIR=$(pwd)
echo -e "${BLUE}📂 현재 위치: $CURRENT_DIR${NC}"

# BH2025_WOWU 디렉토리 찾기
if [ -d "/root/BH2025_WOWU" ]; then
    PROJECT_DIR="/root/BH2025_WOWU"
elif [ -d "~/BH2025_WOWU" ]; then
    PROJECT_DIR="~/BH2025_WOWU"
elif [ -d "/var/www/webapp" ]; then
    PROJECT_DIR="/var/www/webapp"
else
    echo -e "${RED}❌ 프로젝트 디렉토리를 찾을 수 없습니다.${NC}"
    echo "다음 위치를 확인하세요:"
    echo "  - /root/BH2025_WOWU"
    echo "  - ~/BH2025_WOWU"
    echo "  - /var/www/webapp"
    exit 1
fi

echo -e "${GREEN}✅ 프로젝트 디렉토리: $PROJECT_DIR${NC}"
cd "$PROJECT_DIR" || exit 1

# 1. Git pull
echo ""
echo -e "${YELLOW}📥 GitHub에서 최신 코드 가져오는 중...${NC}"
git pull origin main
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Git pull 실패${NC}"
    echo "수동으로 실행하세요: git pull origin main"
    exit 1
fi
echo -e "${GREEN}✅ 최신 코드 다운로드 완료${NC}"

# 2. Frontend 프로세스 확인 및 재시작
echo ""
echo -e "${YELLOW}🔍 Frontend 프로세스 확인 중...${NC}"

# Python HTTP 서버 찾기
FRONTEND_PID=$(ps aux | grep "python.*3000" | grep -v grep | awk '{print $2}')

if [ ! -z "$FRONTEND_PID" ]; then
    echo -e "${YELLOW}⚠️  기존 Frontend 프로세스 종료 중... (PID: $FRONTEND_PID)${NC}"
    kill -9 $FRONTEND_PID
    sleep 2
    echo -e "${GREEN}✅ 기존 프로세스 종료 완료${NC}"
else
    echo -e "${BLUE}ℹ️  실행 중인 Frontend 프로세스 없음${NC}"
fi

# 3. Frontend 시작
echo ""
echo -e "${YELLOW}🚀 Frontend 시작 중...${NC}"
cd "$PROJECT_DIR/frontend" || exit 1

# 가상환경 활성화 (있는 경우)
if [ -f "../venv/bin/activate" ]; then
    source ../venv/bin/activate
    echo -e "${GREEN}✅ Python 가상환경 활성화${NC}"
fi

# nohup으로 백그라운드 실행
nohup python3 -m http.server 3000 --bind 0.0.0.0 > /tmp/frontend.log 2>&1 &
NEW_PID=$!
sleep 3

# 4. 프로세스 확인
if ps -p $NEW_PID > /dev/null 2>&1; then
    echo -e "${GREEN}✅ Frontend 시작 완료 (PID: $NEW_PID)${NC}"
else
    echo -e "${RED}❌ Frontend 시작 실패${NC}"
    echo "로그 확인: tail -f /tmp/frontend.log"
    exit 1
fi

# 5. 서비스 테스트
echo ""
echo -e "${YELLOW}🧪 서비스 테스트 중...${NC}"
sleep 2

HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/)
if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Frontend 정상 작동 (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ Frontend 응답 없음 (HTTP $HTTP_CODE)${NC}"
    echo "로그 확인: tail -f /tmp/frontend.log"
    exit 1
fi

# 6. PWA 파일 확인
echo ""
echo -e "${YELLOW}📱 PWA 파일 확인 중...${NC}"
cd "$PROJECT_DIR/frontend"

# 아이콘 파일 확인
ICON_COUNT=$(ls -1 icon-*.png 2>/dev/null | wc -l)
if [ $ICON_COUNT -eq 8 ]; then
    echo -e "${GREEN}✅ PWA 아이콘 8개 확인됨${NC}"
    ls -lh icon-*.png | awk '{print "   - " $9 " (" $5 ")"}'
else
    echo -e "${YELLOW}⚠️  PWA 아이콘 일부 누락 (발견: ${ICON_COUNT}개 / 필요: 8개)${NC}"
fi

# Apple Touch Icon 확인
if [ -f "apple-touch-icon.png" ]; then
    SIZE=$(ls -lh apple-touch-icon.png | awk '{print $5}')
    echo -e "${GREEN}✅ Apple Touch Icon 확인됨 ($SIZE)${NC}"
else
    echo -e "${YELLOW}⚠️  Apple Touch Icon 누락${NC}"
fi

# Favicon 확인
if [ -f "favicon.ico" ]; then
    echo -e "${GREEN}✅ Favicon 확인됨${NC}"
else
    echo -e "${YELLOW}⚠️  Favicon 누락${NC}"
fi

# 7. Nginx 리로드 (선택사항)
if command -v nginx &> /dev/null; then
    echo ""
    echo -e "${YELLOW}🔄 Nginx 설정 리로드 중...${NC}"
    nginx -t 2>/dev/null
    if [ $? -eq 0 ]; then
        systemctl reload nginx 2>/dev/null
        if [ $? -eq 0 ]; then
            echo -e "${GREEN}✅ Nginx 리로드 완료${NC}"
        fi
    fi
fi

# 8. 최종 결과
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 업데이트 완료!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔗 접속 URL:"
echo "   http://114.202.247.97/"
echo "   http://kdt2025.cafe24.com/ (도메인 연결 시)"
echo ""
echo "📱 PWA 테스트:"
echo "   1. Chrome/Safari 브라우저로 접속"
echo "   2. F12 → Application → Manifest (아이콘 확인)"
echo "   3. 주소창 '설치' 버튼 → 홈 화면에 추가"
echo ""
echo "🔍 확인 명령어:"
echo "   curl http://localhost:3000/manifest.json"
echo "   curl -I http://localhost:3000/icon-192x192.png"
echo "   tail -f /tmp/frontend.log"
echo "   ps aux | grep python | grep 3000"
echo ""
echo "🔄 Backend 재시작 (필요시):"
echo "   cd $PROJECT_DIR/backend"
echo "   pm2 restart bhhs-backend"
echo ""
