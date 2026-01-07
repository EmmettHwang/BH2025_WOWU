# 🌐 Nginx 설정 가이드

Nginx 웹 서버 설치, 설정 및 관리 방법입니다.

---

## 📋 목차

1. [Nginx 소개](#nginx-소개)
2. [설치](#설치)
3. [기본 설정](#기본-설정)
4. [프록시 설정](#프록시-설정)
5. [SSL/HTTPS 설정](#sslhttps-설정)
6. [성능 최적화](#성능-최적화)
7. [문제 해결](#문제-해결)

---

## 🎯 Nginx 소개

Nginx는 고성능 웹 서버이자 리버스 프록시 서버입니다.

**주요 기능:**
- 정적 파일 서빙
- 리버스 프록시
- 로드 밸런싱
- SSL/TLS 종단
- HTTP/2 지원

---

## 📥 설치

### Ubuntu/Debian

```bash
# Nginx 설치
sudo apt update
sudo apt install -y nginx

# 버전 확인
nginx -v

# 서비스 시작
sudo systemctl start nginx
sudo systemctl enable nginx

# 상태 확인
sudo systemctl status nginx
```

### 방화벽 설정

```bash
# HTTP/HTTPS 허용
sudo ufw allow 'Nginx Full'

# 또는 개별 설정
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
```

---

## ⚙️ 기본 설정

### 디렉토리 구조

```
/etc/nginx/
├── nginx.conf              # 메인 설정 파일
├── sites-available/        # 사이트 설정 파일
├── sites-enabled/          # 활성화된 사이트 (심볼릭 링크)
├── conf.d/                 # 추가 설정
└── snippets/               # 재사용 가능한 설정 조각
```

### nginx.conf 기본 설정

```bash
sudo nano /etc/nginx/nginx.conf
```

**권장 설정:**
```nginx
user www-data;
worker_processes auto;
pid /run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    # 기본 설정
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    server_tokens off;
    
    # 파일 업로드 크기 제한
    client_max_body_size 100M;
    client_body_buffer_size 128k;
    
    # MIME types
    include /etc/nginx/mime.types;
    default_type application/octet-stream;
    
    # 로깅
    access_log /var/log/nginx/access.log;
    error_log /var/log/nginx/error.log warn;
    
    # Gzip 압축
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_types text/plain text/css text/xml text/javascript application/json application/javascript application/xml+rss;
    
    # Virtual Host 설정 포함
    include /etc/nginx/conf.d/*.conf;
    include /etc/nginx/sites-enabled/*;
}
```

---

## 🔀 프록시 설정

### BH2025 WOWU 프로젝트 설정

```bash
# 설정 파일 생성
sudo nano /etc/nginx/sites-available/bh2025
```

**전체 설정:**
```nginx
# HTTP 서버
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;
    
    # 파일 업로드 크기 제한 (100MB)
    client_max_body_size 100M;
    client_body_buffer_size 128k;
    
    # 업로드 타임아웃
    client_body_timeout 300s;
    
    # 로그 파일
    access_log /var/log/nginx/bh2025_access.log;
    error_log /var/log/nginx/bh2025_error.log;
    
    # 프론트엔드 (포트 3000)
    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        
        # WebSocket 지원
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        
        # 헤더 설정
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        proxy_cache_bypass $http_upgrade;
        
        # 타임아웃
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
    
    # 백엔드 API (포트 8000)
    location /api/ {
        proxy_pass http://localhost:8000;
        proxy_http_version 1.1;
        
        # 헤더 설정
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # 대용량 파일 업로드 타임아웃
        proxy_connect_timeout 600s;
        proxy_send_timeout 600s;
        proxy_read_timeout 600s;
        send_timeout 600s;
        
        # 버퍼 설정
        proxy_buffering off;
        proxy_request_buffering off;
    }
    
    # 정적 파일 직접 서빙 (선택사항)
    location /static/ {
        alias /root/BH2025_WOWU/frontend/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }
    
    # Favicon
    location = /favicon.ico {
        log_not_found off;
        access_log off;
    }
    
    # Robots.txt
    location = /robots.txt {
        log_not_found off;
        access_log off;
    }
}
```

### 설정 활성화

```bash
# 심볼릭 링크 생성
sudo ln -s /etc/nginx/sites-available/bh2025 /etc/nginx/sites-enabled/

# 기본 설정 비활성화
sudo rm /etc/nginx/sites-enabled/default

# 설정 테스트
sudo nginx -t

# Nginx 재시작
sudo systemctl restart nginx
```

---

## 🔐 SSL/HTTPS 설정

### Certbot으로 Let's Encrypt 인증서 발급

```bash
# Certbot 설치
sudo apt install -y certbot python3-certbot-nginx

# 인증서 자동 발급 및 설정
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# 이메일 입력
# 약관 동의
# 자동으로 Nginx 설정 업데이트됨
```

### 수동 SSL 설정

**Certbot이 추가하는 설정:**
```nginx
server {
    listen 443 ssl http2;
    listen [::]:443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    # SSL 인증서
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # SSL 설정
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_prefer_server_ciphers on;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_session_cache shared:SSL:10m;
    ssl_session_timeout 10m;
    
    # HSTS (선택사항)
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    
    # 나머지 설정은 HTTP와 동일
    # ...
}

# HTTP -> HTTPS 리다이렉트
server {
    listen 80;
    listen [::]:80;
    server_name yourdomain.com www.yourdomain.com;
    
    return 301 https://$server_name$request_uri;
}
```

### 인증서 자동 갱신

```bash
# 자동 갱신 테스트
sudo certbot renew --dry-run

# Cron 작업 확인 (자동 등록됨)
sudo systemctl status certbot.timer

# 수동 갱신
sudo certbot renew
```

---

## ⚡ 성능 최적화

### 캐싱 설정

```nginx
# 정적 파일 캐싱
location ~* \.(jpg|jpeg|png|gif|ico|css|js|svg|woff|woff2|ttf|eot)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
    access_log off;
}

# API 캐싱 (선택적)
location /api/public/ {
    proxy_pass http://localhost:8000;
    proxy_cache my_cache;
    proxy_cache_valid 200 302 10m;
    proxy_cache_valid 404 1m;
}
```

### Gzip 압축 강화

```nginx
http {
    gzip on;
    gzip_vary on;
    gzip_comp_level 6;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/x-javascript
        image/svg+xml;
}
```

---

## 🔧 Nginx 관리 명령어

```bash
# 상태 확인
sudo systemctl status nginx

# 시작/중지/재시작
sudo systemctl start nginx
sudo systemctl stop nginx
sudo systemctl restart nginx

# 설정 리로드 (다운타임 없음)
sudo systemctl reload nginx

# 설정 테스트
sudo nginx -t

# 로그 확인
sudo tail -f /var/log/nginx/access.log
sudo tail -f /var/log/nginx/error.log

# 특정 사이트 로그
sudo tail -f /var/log/nginx/bh2025_access.log
```

---

## 🐛 문제 해결

### 503 Bad Gateway

**원인**: 백엔드 서버가 응답하지 않음

```bash
# PM2 상태 확인
pm2 status

# 포트 확인
netstat -tlnp | grep 8000
netstat -tlnp | grep 3000

# 백엔드 로그 확인
pm2 logs backend-server
```

### 413 Request Entity Too Large

**원인**: 파일 업로드 크기 제한

```bash
# Nginx 설정 확인
sudo grep -r "client_max_body_size" /etc/nginx/

# 설정 수정
sudo nano /etc/nginx/nginx.conf
# 또는
sudo nano /etc/nginx/sites-available/bh2025

# client_max_body_size 100M; 추가

# Nginx 재시작
sudo systemctl reload nginx
```

### 설정 파일 문법 오류

```bash
# 상세한 오류 확인
sudo nginx -t

# 백업에서 복원
sudo cp /etc/nginx/nginx.conf.backup /etc/nginx/nginx.conf
```

---

## 📊 로그 분석

```bash
# 실시간 액세스 로그
sudo tail -f /var/log/nginx/access.log

# 에러 로그
sudo tail -f /var/log/nginx/error.log

# 특정 IP 필터링
sudo grep "192.168.1.100" /var/log/nginx/access.log

# 404 에러 확인
sudo grep " 404 " /var/log/nginx/access.log

# 가장 많이 접속한 IP
sudo awk '{print $1}' /var/log/nginx/access.log | sort | uniq -c | sort -rn | head -10
```

---

## ✅ 체크리스트

- [ ] Nginx 설치
- [ ] 기본 설정 (`nginx.conf`)
- [ ] 사이트 설정 (`sites-available/bh2025`)
- [ ] 심볼릭 링크 생성
- [ ] 파일 업로드 크기 설정 (100MB)
- [ ] 프록시 타임아웃 설정
- [ ] 방화벽 허용 (80, 443)
- [ ] 설정 테스트 (`nginx -t`)
- [ ] SSL 인증서 (선택)
- [ ] 자동 갱신 설정

---

## 🔗 관련 문서

- [전체 배포 가이드](./01_DEPLOYMENT_GUIDE.md)
- [PM2 관리](./04_PM2_MANAGEMENT.md)
- [문제 해결](./05_TROUBLESHOOTING.md)

---

## 📚 참고 자료

- Nginx 공식 문서: https://nginx.org/en/docs/
- Certbot 가이드: https://certbot.eff.org/
- Mozilla SSL Config: https://ssl-config.mozilla.org/

---

**작성자**: EmmettHwang  
**마지막 업데이트**: 2024-12-XX  
**버전**: 1.0.0
