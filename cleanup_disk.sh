#!/bin/bash
# Cafe24 서버 디스크 정리 스크립트

echo "========================================="
echo "  Cafe24 서버 디스크 정리 시작"
echo "========================================="
echo ""

# 현재 디스크 사용량
echo "📊 정리 전 디스크 사용량:"
df -h | grep -E "Filesystem|/$"
echo ""

# 1. PM2 로그 정리
echo "🧹 1. PM2 로그 정리..."
pm2 flush
echo "✅ PM2 로그 정리 완료"
echo ""

# 2. 백엔드 로그 정리
echo "🧹 2. 백엔드 로그 정리..."
cd ~/BH2025_WOWU
rm -f backend/logs/*.log 2>/dev/null
echo "✅ 백엔드 로그 정리 완료"
echo ""

# 3. Python 캐시 삭제
echo "🧹 3. Python 캐시 파일 삭제..."
find ~/BH2025_WOWU -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null
find ~/BH2025_WOWU -name "*.pyc" -delete 2>/dev/null
find ~/BH2025_WOWU -name "*.pyo" -delete 2>/dev/null
echo "✅ Python 캐시 정리 완료"
echo ""

# 4. Git 객체 정리
echo "🧹 4. Git 저장소 최적화..."
cd ~/BH2025_WOWU
git gc --aggressive --prune=now 2>/dev/null
echo "✅ Git 저장소 최적화 완료"
echo ""

# 5. 시스템 캐시 정리
echo "🧹 5. 시스템 캐시 정리..."
sudo apt clean 2>/dev/null
sudo apt autoremove -y 2>/dev/null
echo "✅ 시스템 캐시 정리 완료"
echo ""

# 6. 저널 로그 정리 (7일치만 보관)
echo "🧹 6. 시스템 로그 정리..."
sudo journalctl --vacuum-time=7d 2>/dev/null
echo "✅ 시스템 로그 정리 완료"
echo ""

# 정리 후 디스크 사용량
echo "========================================="
echo "📊 정리 후 디스크 사용량:"
df -h | grep -E "Filesystem|/$"
echo ""

echo "========================================="
echo "✅ 디스크 정리 완료!"
echo "========================================="
echo ""

# 큰 파일 목록 표시
echo "📁 남아있는 큰 디렉토리 TOP 10:"
cd ~
du -sh * 2>/dev/null | sort -hr | head -10
echo ""

echo "💡 추가 정리가 필요하면:"
echo "   - node_modules 삭제: rm -rf ~/BH2025_WOWU/node_modules"
echo "   - 오래된 문서 삭제: rm -rf ~/BH2025_WOWU/documents/*"
echo "   - MySQL 로그 정리: sudo mysql -e \"PURGE BINARY LOGS BEFORE DATE_SUB(NOW(), INTERVAL 3 DAY);\""
echo ""
