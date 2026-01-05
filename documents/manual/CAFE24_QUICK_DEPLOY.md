# 🚀 Cafe24 서버 빠른 배포 가이드 (최종판)

## ✅ 완료된 모든 작업

### 1. 자동 로드 비활성화 ⚡
- **문제**: 서버 시작할 때마다 158개 문서를 다시 인덱싱 (10-20분 소요)
- **해결**: `load_default_documents()` 함수 호출 비활성화
- **효과**: 서버가 **10초 이내**에 시작됨!

### 2. Nginx 502 에러 개선 🎨
- **문제**: 502 Bad Gateway 에러 메시지가 사용자에게 불친절
- **해결**: 준비 중 페이지 표시 (자동 새로고침, 진행 상황 안내)
- **효과**: 사용자 경험 대폭 개선!

### 3. RAG 폴더 분리 📁
- **RAG 문서**: `backend/rag_documents/` (인덱싱된 문서)
- **일반 문서**: `backend/documents/` (일반 다운로드용)
- **UI 구분**: [RAG] 뱃지로 시각적 구분

---

## 📋 Cafe24 서버 배포 명령어 (전체)

### 1단계: 백엔드 업데이트

```bash
# 최신 코드 받기
cd ~/BH2025_WOWU
git pull origin hun

# PM2 재시작
pm2 restart bh2025-backend

# 10초 대기 후 확인
sleep 10
pm2 status
netstat -tuln | grep 8000

# 서비스 확인
curl -I http://localhost:8000
```

### 2단계: Nginx 502 페이지 설정 (선택사항)

```bash
# 준비 중 페이지 생성
sudo mkdir -p /var/www/html
sudo bash -c 'cat > /var/www/html/maintenance.html' << 'EOFHTML'
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>서비스 준비 중 - BH2025 WOWU</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); min-height: 100vh; display: flex; align-items: center; justify-content: center; padding: 20px; }
        .container { background: white; border-radius: 20px; padding: 60px 40px; max-width: 600px; width: 100%; box-shadow: 0 20px 60px rgba(0,0,0,0.3); text-align: center; animation: fadeInUp 0.6s; }
        @keyframes fadeInUp { from { opacity: 0; transform: translateY(30px); } to { opacity: 1; transform: translateY(0); } }
        .icon { width: 120px; height: 120px; margin: 0 auto 30px; position: relative; }
        .icon::before { content: '🚀'; font-size: 80px; position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); animation: bounce 2s infinite; }
        @keyframes bounce { 0%, 100% { transform: translate(-50%, -50%) translateY(0); } 50% { transform: translate(-50%, -50%) translateY(-10px); } }
        h1 { color: #333; font-size: 32px; margin-bottom: 20px; font-weight: 700; }
        .subtitle { color: #666; font-size: 18px; margin-bottom: 30px; line-height: 1.6; }
        .loading { display: flex; justify-content: center; gap: 10px; margin: 30px 0; }
        .dot { width: 12px; height: 12px; background: #667eea; border-radius: 50%; animation: pulse 1.4s infinite ease-in-out; }
        .dot:nth-child(1) { animation-delay: -0.32s; } .dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes pulse { 0%, 80%, 100% { transform: scale(0.8); opacity: 0.5; } 40% { transform: scale(1.2); opacity: 1; } }
        .info-box { background: #f8f9fa; border-radius: 12px; padding: 20px; margin-top: 30px; }
        .info-box p { color: #555; font-size: 14px; line-height: 1.8; margin-bottom: 10px; }
        .status { display: inline-block; background: #ffd700; color: #333; padding: 8px 20px; border-radius: 20px; font-size: 14px; font-weight: 600; margin-top: 20px; animation: glow 2s infinite; }
        @keyframes glow { 0%, 100% { box-shadow: 0 0 5px rgba(255,215,0,0.5); } 50% { box-shadow: 0 0 20px rgba(255,215,0,0.8); } }
        .refresh-btn { display: inline-block; margin-top: 30px; padding: 14px 40px; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; border-radius: 30px; font-weight: 600; cursor: pointer; border: none; font-size: 16px; }
    </style>
    <script>setTimeout(function() { window.location.reload(); }, 10000);</script>
</head>
<body>
    <div class="container">
        <div class="icon"></div>
        <h1>🎓 BH2025 WOWU</h1>
        <p class="subtitle">서비스를 준비하고 있습니다<br>AI 시스템을 초기화 중입니다</p>
        <div class="loading"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>
        <div class="status">🔧 시스템 초기화 중</div>
        <div class="info-box">
            <p>✨ <strong>RAG 시스템</strong>이 문서를 인덱싱하고 있습니다</p>
            <p>⏱️ 예상 대기 시간: <strong>약 5-10분</strong></p>
            <p>🔄 이 페이지는 10초마다 자동으로 새로고침됩니다</p>
        </div>
        <button class="refresh-btn" onclick="window.location.reload()">🔄 지금 새로고침</button>
    </div>
</body>
</html>
EOFHTML

# Nginx 설정 파일 찾기
echo "=== Nginx 설정 파일 위치 ==="
nginx -T 2>&1 | grep -B 5 'server_name' | grep 'configuration file'
```

**Nginx 설정 파일 편집**:
```bash
# 위에서 찾은 파일을 편집 (예: /etc/nginx/sites-enabled/default)
sudo nano /etc/nginx/sites-enabled/default

# server 블록 안에 추가:
#     error_page 502 /maintenance.html;
#     location = /maintenance.html {
#         root /var/www/html;
#         internal;
#     }

# 설정 검사 및 적용
sudo nginx -t
sudo nginx -s reload
```

---

## ⏱️ 성능 비교

| 구분 | 이전 | 현재 |
|------|------|------|
| **서버 시작 시간** | 10-20분 ⏰ | **10초** ⚡ |
| **자동 로드** | 매번 인덱싱 | 비활성화 ✅ |
| **502 에러 표시** | 에러 메시지 ❌ | 준비 중 페이지 ✨ |
| **문서 폴더** | 통합 | 분리 (RAG/일반) 📁 |
| **UI 구분** | 없음 | [RAG] 뱃지 🏷️ |

---

## 📚 문서 업로드 방법

이제 문서는 **웹 UI에서 수동으로 업로드**합니다:

1. 로그인 후 **문서 관리** 메뉴로 이동
2. 파일 선택
3. **"RAG 시스템에 인덱싱하시겠습니까?"** 모달
   - **예**: `backend/rag_documents/` 저장, 보라색 [RAG] 뱃지
   - **아니오**: `backend/documents/` 저장, 일반 문서
4. 업로드 완료

---

## 🔍 예상 결과

### 성공 시:
```bash
pm2 status
┌────┬────────────────────┬──────────┬──────┬───────────┬──────────┬──────────┐
│ id │ name               │ mode     │ ↺    │ status    │ cpu      │ memory   │
├────┼────────────────────┼──────────┼──────┼───────────┼──────────┼──────────┤
│ 0  │ bh2025-backend     │ fork     │ 0    │ online    │ 0%       │ 250.5mb  │
└────┴────────────────────┴──────────┴──────┴───────────┴──────────┴──────────┘

netstat -tuln | grep 8000
tcp        0      0 0.0.0.0:8000            0.0.0.0:*               LISTEN

curl -I http://localhost:8000
HTTP/1.1 200 OK
```

### 브라우저 접속:
- **http://www.kdt2025.com** ✅ 정상 작동
- **https://www.kdt2025.com** ✅ 정상 작동

### 502 에러 발생 시:
- **이전**: `502 Bad Gateway nginx/1.18.0 (Ubuntu)` ❌
- **현재**: 🚀 준비 중 페이지 (자동 새로고침) ✨

---

## 🎯 커밋 정보

### 주요 커밋들:
1. **7dc2aa4** - fix: 서버 시작 시 기본 문서 자동 로드 비활성화 (빠른 시작)
2. **60c9bf0** - docs: Nginx 502 에러 대신 준비 중 페이지 표시 설정 가이드 추가
3. **c4d15fe** - fix: RAG 문서 폴더명을 rag_documents로 변경
4. **ff9c10c** - feat: RAG 문서를 별도 폴더에 저장 및 UI 표시 개선
5. **2e8b972** - fix: RAG 애니메이션 즉시 시작

- **브랜치**: hun
- **GitHub**: https://github.com/EmmettHwang/BH2025_WOWU/tree/hun

---

## 🚨 중요 사항

1. **벡터 DB는 유지됨**: 기존에 업로드한 문서는 모두 보존됩니다
2. **새 문서는 수동 업로드**: UI에서 직접 업로드해야 합니다
3. **빠른 재시작**: 이제 서버 재시작이 10초 이내로 완료됩니다
4. **자동 로드 복원**: 필요하면 언제든지 다시 활성화 가능
5. **Nginx 설정**: 선택사항이지만, 사용자 경험 향상에 큰 도움

---

## 📖 관련 문서

- `RAG_ANIMATION_FIX_SUMMARY.md` - RAG 애니메이션 즉시 시작 수정
- `RAG_FOLDER_SEPARATION.md` - RAG 폴더 분리 구현 상세
- `NGINX_502_MAINTENANCE_PAGE.md` - Nginx 502 에러 페이지 설정 (상세)

---

## ✨ 다음 단계

1. ✅ Cafe24에서 위 명령어 실행
2. ✅ 브라우저로 접속 테스트
3. ✅ 문서 업로드 테스트
4. ✅ RAG 기능 테스트
5. ⬜ (선택) Nginx 502 페이지 설정

---

## 🎉 최종 효과

### 서버 시작
- **이전**: 10-20분 대기, 매번 인덱싱 😫
- **현재**: 10초 이내 시작, 즉시 사용 가능 🚀

### 사용자 경험
- **이전**: 502 에러, 수동 새로고침 😞
- **현재**: 친절한 안내, 자동 새로고침 😊

### 파일 관리
- **이전**: 모든 문서가 한 폴더 😕
- **현재**: RAG/일반 문서 분리, UI 구분 📁

### 애니메이션
- **이전**: 3초 대기 후 시작 ⏳
- **현재**: 즉시 애니메이션 시작 ⚡

---

모든 준비 완료! 배포를 시작하세요! 🎉
