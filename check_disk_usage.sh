#!/bin/bash
# Cafe24 서버 디스크 사용량 확인 스크립트

echo "========================================="
echo "  Cafe24 서버 디스크 사용량 확인"
echo "========================================="
echo ""

echo "📊 전체 디스크 사용량:"
df -h | grep -E "Filesystem|/$"
echo ""

echo "📁 프로젝트 폴더 크기:"
cd ~/BH2025_WOWU
du -sh . 2>/dev/null || echo "프로젝트 폴더 없음"
echo ""

echo "📝 로그 파일 크기:"
du -sh backend/logs 2>/dev/null || echo "로그 폴더 없음"
echo ""

echo "🗑️  정리 가능한 파일:"
echo "- PM2 로그: pm2 flush"
echo "- 백엔드 로그: rm -f backend/logs/*.log"
echo "- 시스템 캐시: sudo apt clean && sudo apt autoremove"
echo ""

echo "========================================="
