# 🌐 Nginx 502 에러 대신 준비 중 페이지 표시 설정

## 📋 목적

서버 재시작 시 `502 Bad Gateway` 에러 대신, 사용자에게 친화적인 **"서비스 준비 중"** 페이지를 표시합니다.

---

## ✨ 준비 중 페이지 미리보기

- 🚀 애니메이션 아이콘
- ⏱️ 예상 대기 시간 표시 (약 5-10분)
- 🔄 10초마다 자동 새로고침
- 💜 보라색 그라디언트 디자인
- 📱 반응형 (모바일 대응)

---

## 🚀 Cafe24 서버 설정 방법

### 1단계: 준비 중 페이지 HTML 파일 생성

```bash
# 디렉토리 생성
sudo mkdir -p /var/www/html

# HTML 파일 생성
sudo bash -c 'cat > /var/www/html/maintenance.html' << 'EOFHTML'
<!DOCTYPE html>
<html lang="ko">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>서비스 준비 중 - BH2025 WOWU</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 20px;
        }
        .container {
            background: white;
            border-radius: 20px;
            padding: 60px 40px;
            max-width: 600px;
            width: 100%;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
            text-align: center;
            animation: fadeInUp 0.6s ease-out;
        }
        @keyframes fadeInUp {
            from { opacity: 0; transform: translateY(30px); }
            to { opacity: 1; transform: translateY(0); }
        }
        .icon {
            width: 120px;
            height: 120px;
            margin: 0 auto 30px;
            position: relative;
        }
        .icon::before {
            content: '🚀';
            font-size: 80px;
            position: absolute;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            animation: bounce 2s infinite;
        }
        @keyframes bounce {
            0%, 100% { transform: translate(-50%, -50%) translateY(0); }
            50% { transform: translate(-50%, -50%) translateY(-10px); }
        }
        h1 {
            color: #333;
            font-size: 32px;
            margin-bottom: 20px;
            font-weight: 700;
        }
        .subtitle {
            color: #666;
            font-size: 18px;
            margin-bottom: 30px;
            line-height: 1.6;
        }
        .loading {
            display: flex;
            justify-content: center;
            gap: 10px;
            margin: 30px 0;
        }
        .dot {
            width: 12px;
            height: 12px;
            background: #667eea;
            border-radius: 50%;
            animation: pulse 1.4s infinite ease-in-out;
        }
        .dot:nth-child(1) { animation-delay: -0.32s; }
        .dot:nth-child(2) { animation-delay: -0.16s; }
        @keyframes pulse {
            0%, 80%, 100% {
                transform: scale(0.8);
                opacity: 0.5;
            }
            40% {
                transform: scale(1.2);
                opacity: 1;
            }
        }
        .info-box {
            background: #f8f9fa;
            border-radius: 12px;
            padding: 20px;
            margin-top: 30px;
        }
        .info-box p {
            color: #555;
            font-size: 14px;
            line-height: 1.8;
            margin-bottom: 10px;
        }
        .info-box p:last-child {
            margin-bottom: 0;
        }
        .status {
            display: inline-block;
            background: #ffd700;
            color: #333;
            padding: 8px 20px;
            border-radius: 20px;
            font-size: 14px;
            font-weight: 600;
            margin-top: 20px;
            animation: glow 2s infinite;
        }
        @keyframes glow {
            0%, 100% { box-shadow: 0 0 5px rgba(255,215,0,0.5); }
            50% { box-shadow: 0 0 20px rgba(255,215,0,0.8); }
        }
        .refresh-btn {
            display: inline-block;
            margin-top: 30px;
            padding: 14px 40px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            text-decoration: none;
            border-radius: 30px;
            font-weight: 600;
            transition: all 0.3s ease;
            cursor: pointer;
            border: none;
            font-size: 16px;
        }
        .refresh-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 10px 25px rgba(102, 126, 234, 0.4);
        }
        @media (max-width: 600px) {
            .container { padding: 40px 30px; }
            h1 { font-size: 26px; }
            .subtitle { font-size: 16px; }
        }
    </style>
    <script>
        // 자동 새로고침 (10초마다)
        setTimeout(function() {
            window.location.reload();
        }, 10000);
    </script>
</head>
<body>
    <div class="container">
        <div class="icon"></div>
        <h1>🎓 BH2025 WOWU</h1>
        <p class="subtitle">
            서비스를 준비하고 있습니다<br>
            AI 시스템을 초기화 중입니다
        </p>
        
        <div class="loading">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>
        
        <div class="status">🔧 시스템 초기화 중</div>
        
        <div class="info-box">
            <p>✨ <strong>RAG 시스템</strong>이 문서를 인덱싱하고 있습니다</p>
            <p>⏱️ 예상 대기 시간: <strong>약 5-10분</strong></p>
            <p>🔄 이 페이지는 10초마다 자동으로 새로고침됩니다</p>
        </div>
        
        <button class="refresh-btn" onclick="window.location.reload()">
            🔄 지금 새로고침
        </button>
    </div>
</body>
</html>
EOFHTML

# 파일 권한 설정
sudo chmod 644 /var/www/html/maintenance.html
```

---

### 2단계: Nginx 설정 파일 찾기

```bash
# Nginx 설정 파일 위치 확인
nginx -T 2>&1 | grep -B 5 'server_name' | grep 'configuration file'

# 일반적인 위치들:
ls -la /etc/nginx/sites-enabled/
ls -la /etc/nginx/sites-available/
ls -la /etc/nginx/conf.d/
```

**예상 결과**:
```
# configuration file /etc/nginx/sites-enabled/default:
# 또는
# configuration file /etc/nginx/conf.d/default.conf:
```

---

### 3단계: Nginx 설정에 502 에러 페이지 추가

위에서 찾은 설정 파일을 편집합니다:

```bash
# 예시: /etc/nginx/sites-enabled/default 를 편집
sudo nano /etc/nginx/sites-enabled/default
```

**server 블록 안에 다음 내용 추가**:

```nginx
server {
    listen 80;
    server_name www.kdt2025.com kdt2025.com;
    
    # ... 기존 설정 ...
    
    # 502 에러 발생 시 준비 중 페이지로 리다이렉트
    error_page 502 /maintenance.html;
    
    location = /maintenance.html {
        root /var/www/html;
        internal;
    }
    
    # ... 나머지 설정 ...
}
```

---

### 4단계: Nginx 설정 테스트 및 재시작

```bash
# 설정 문법 검사
sudo nginx -t

# 설정 적용 (리로드)
sudo nginx -s reload

# 또는 재시작
sudo systemctl reload nginx
```

**예상 출력**:
```
nginx: the configuration file /etc/nginx/nginx.conf syntax is ok
nginx: configuration file /etc/nginx/nginx.conf test is successful
```

---

## 🔍 동작 확인

### 1. 백엔드 중지 상태에서 테스트

```bash
# 백엔드 잠깐 중지
pm2 stop bh2025-backend

# 브라우저에서 접속
# http://www.kdt2025.com
# → "서비스 준비 중" 페이지가 보여야 함!

# 백엔드 재시작
pm2 start bh2025-backend
```

### 2. 브라우저 확인

- ✅ **502 Bad Gateway** 대신 **준비 중 페이지** 표시
- ✅ 10초마다 자동 새로고침
- ✅ 서버 시작되면 자동으로 정상 페이지로 전환

---

## 📊 설정 전/후 비교

### 설정 전 (502 에러)
```
502 Bad Gateway
nginx/1.18.0 (Ubuntu)
```
❌ 사용자에게 불친절
❌ 에러처럼 보임
❌ 수동 새로고침 필요

### 설정 후 (준비 중 페이지)
```
🎓 BH2025 WOWU
서비스를 준비하고 있습니다
AI 시스템을 초기화 중입니다
✨ RAG 시스템이 문서를 인덱싱하고 있습니다
⏱️ 예상 대기 시간: 약 5-10분
🔄 10초마다 자동 새로고침
```
✅ 사용자 친화적
✅ 진행 상황 알림
✅ 자동 새로고침

---

## 🚨 주의사항

1. **internal 지시어**: `internal;`을 사용하여 `/maintenance.html`을 직접 접근할 수 없게 함 (502 에러 시만 표시)
2. **경로 확인**: `/var/www/html/maintenance.html` 파일이 존재하는지 확인
3. **권한 확인**: nginx가 해당 파일을 읽을 수 있는지 확인 (`chmod 644`)
4. **백업**: Nginx 설정 변경 전 백업 권장
   ```bash
   sudo cp /etc/nginx/sites-enabled/default /etc/nginx/sites-enabled/default.backup
   ```

---

## 🔧 트러블슈팅

### 문제 1: 여전히 502 에러가 보임

**해결**:
```bash
# Nginx 설정 재확인
sudo nginx -t

# Nginx 완전 재시작
sudo systemctl restart nginx

# maintenance.html 파일 확인
ls -la /var/www/html/maintenance.html
```

### 문제 2: 준비 중 페이지가 계속 보임

**원인**: 백엔드가 정상 시작되지 않음

**해결**:
```bash
# PM2 상태 확인
pm2 status

# 포트 확인
netstat -tuln | grep 8000

# 백엔드 로그 확인
pm2 logs bh2025-backend --lines 50
```

### 문제 3: 페이지 스타일이 깨짐

**원인**: HTML 파일 생성 시 따옴표 문제

**해결**: 위의 heredoc 방식 (`cat > ... << 'EOFHTML'`)을 정확히 사용

---

## 📝 전체 명령어 요약 (한 번에 실행)

```bash
# 1. 준비 중 페이지 생성
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

# 2. Nginx 설정 파일 찾기
echo "=== Nginx 설정 파일 위치 ==="
nginx -T 2>&1 | grep -B 5 'server_name' | grep 'configuration file'

# 3. 다음 메시지 확인 후, 해당 파일을 편집하여 error_page 설정 추가
echo ""
echo "다음 단계:"
echo "1. 위에서 찾은 Nginx 설정 파일을 편집"
echo "2. server 블록 안에 다음 내용 추가:"
echo ""
echo "    error_page 502 /maintenance.html;"
echo "    location = /maintenance.html {"
echo "        root /var/www/html;"
echo "        internal;"
echo "    }"
echo ""
echo "3. sudo nginx -t 로 설정 검사"
echo "4. sudo nginx -s reload 로 적용"
```

---

## ✅ 설정 완료 체크리스트

- [ ] `/var/www/html/maintenance.html` 파일 생성 완료
- [ ] Nginx 설정 파일에 `error_page 502` 추가 완료
- [ ] `sudo nginx -t` 문법 검사 통과
- [ ] `sudo nginx -s reload` 적용 완료
- [ ] 백엔드 중지 후 브라우저 테스트 완료
- [ ] 준비 중 페이지 정상 표시 확인
- [ ] 자동 새로고침 동작 확인

---

## 🎯 최종 효과

- ✨ **사용자 경험 개선**: 에러 대신 친절한 안내 메시지
- ⏱️ **대기 시간 안내**: 언제 다시 시도해야 하는지 명확히 알림
- 🔄 **자동 복구**: 서버 시작되면 자동으로 정상 페이지로 전환
- 📱 **모바일 대응**: 모든 디바이스에서 깔끔한 표시

---

## 📅 작성 정보

- **작성일**: 2026-01-05
- **버전**: 1.0
- **관련 커밋**: 7dc2aa4
- **브랜치**: hun
