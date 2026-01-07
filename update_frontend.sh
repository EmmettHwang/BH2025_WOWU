#!/bin/bash

# Frontend 업데이트 스크립트
# Cafe24 서버에서 실행: bash update_frontend.sh

echo "🚀 Frontend 업데이트 시작..."

# 색상 정의
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Git pull
echo -e "${YELLOW}📥 GitHub에서 최신 코드 가져오는 중...${NC}"
git pull origin main
if [ $? -ne 0 ]; then
    echo -e "${RED}❌ Git pull 실패${NC}"
    exit 1
fi
echo -e "${GREEN}✅ 최신 코드 다운로드 완료${NC}"

# 2. Frontend 프로세스 확인
echo -e "${YELLOW}🔍 Frontend 프로세스 확인 중...${NC}"
FRONTEND_PID=$(ps aux | grep "python.*3000" | grep -v grep | awk '{print $2}')

if [ ! -z "$FRONTEND_PID" ]; then
    echo -e "${YELLOW}⚠️  기존 Frontend 프로세스 종료 중... (PID: $FRONTEND_PID)${NC}"
    kill -9 $FRONTEND_PID
    sleep 2
    echo -e "${GREEN}✅ 기존 프로세스 종료 완료${NC}"
fi

# 3. Frontend 재시작
echo -e "${YELLOW}🚀 Frontend 시작 중...${NC}"
cd frontend
nohup python3 -m http.server 3000 --bind 0.0.0.0 > /tmp/frontend.log 2>&1 &
NEW_PID=$!
sleep 2

# 4. 프로세스 확인
if ps -p $NEW_PID > /dev/null; then
    echo -e "${GREEN}✅ Frontend 시작 완료 (PID: $NEW_PID)${NC}"
else
    echo -e "${RED}❌ Frontend 시작 실패${NC}"
    exit 1
fi

# 5. 서비스 테스트
echo -e "${YELLOW}🧪 서비스 테스트 중...${NC}"
sleep 1
HTTP_CODE=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/)

if [ "$HTTP_CODE" = "200" ]; then
    echo -e "${GREEN}✅ Frontend 정상 작동 (HTTP $HTTP_CODE)${NC}"
else
    echo -e "${RED}❌ Frontend 응답 없음 (HTTP $HTTP_CODE)${NC}"
    exit 1
fi

# 6. Nginx 리로드 (선택사항)
if command -v nginx &> /dev/null; then
    echo -e "${YELLOW}🔄 Nginx 설정 리로드 중...${NC}"
    nginx -t && systemctl reload nginx
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Nginx 리로드 완료${NC}"
    fi
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo -e "${GREEN}🎉 업데이트 완료!${NC}"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🔗 접속 URL:"
echo "   http://114.202.247.97/"
echo ""
echo "📱 PWA 테스트:"
echo "   1. 모바일/데스크톱 브라우저로 접속"
echo "   2. 주소창의 '설치' 또는 '+' 버튼 확인"
echo "   3. 홈 화면에 추가하여 앱처럼 사용"
echo ""
echo "🔍 확인 명령어:"
echo "   curl http://localhost:3000/manifest.json"
echo "   curl -I http://localhost:3000/icon-192x192.png"
echo "   tail -f /tmp/frontend.log"
echo ""
