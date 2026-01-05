#!/bin/bash
# ==================== BH2025 WOWU 서버 중지 스크립트 ====================
# 사용법: bash stop.sh

echo "============================================================"
echo "  BH2025 WOWU 서버 중지"
echo "============================================================"
echo ""

# Python 프로세스 찾기
PIDS=$(ps aux | grep "uvicorn main:app" | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "⚠️  실행 중인 서버가 없습니다."
    exit 0
fi

echo "실행 중인 서버 프로세스:"
ps aux | grep "uvicorn main:app" | grep -v grep

echo ""
echo "프로세스 중지 중..."

for PID in $PIDS; do
    kill -15 $PID 2>/dev/null
    if [ $? -eq 0 ]; then
        echo "✅ PID $PID 중지됨"
    else
        echo "⚠️  PID $PID 중지 실패 (권한 문제일 수 있음)"
    fi
done

# 잠시 대기
sleep 2

# 여전히 실행 중이면 강제 종료
REMAINING=$(ps aux | grep "uvicorn main:app" | grep -v grep | awk '{print $2}')
if [ -n "$REMAINING" ]; then
    echo ""
    echo "⚠️  일부 프로세스가 여전히 실행 중입니다. 강제 종료 시도..."
    for PID in $REMAINING; do
        kill -9 $PID 2>/dev/null
        if [ $? -eq 0 ]; then
            echo "✅ PID $PID 강제 종료됨"
        fi
    done
fi

echo ""
echo "============================================================"
echo "  ✅ 서버 중지 완료"
echo "============================================================"
