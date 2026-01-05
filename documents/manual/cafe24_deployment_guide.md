# Cafe24 배포 가이드

## 📋 목차
1. [간단한 배포 (방법 2 - 현재 사용 중)](#간단한-배포-방법-2)
2. [트러블슈팅](#트러블슈팅)

---

## 🚀 간단한 배포 (방법 2 - 현재 사용 중)

> **확정 방식**: Nginx가 Git 폴더를 직접 서빙

### 📋 배포 명령어

```bash
cd ~/BH2025_WOWU
git pull origin hun
pm2 restart all
```

**끝!** 🚀 (sudo 없음!)

---

### 📊 Nginx 설정

```nginx
location / {
    root /root/BH2025_WOWU/frontend;
    try_files $uri $uri/ /index.html;
    index index.html;
}
```

---

### 💡 빠른 배포 스크립트

`~/deploy.sh` 파일 생성:

```bash
cat > ~/deploy.sh << 'EOF'
#!/bin/bash
cd ~/BH2025_WOWU
echo "📥 최신 코드 가져오는 중..."
git pull origin hun
echo "🔄 백엔드 재시작 중..."
pm2 restart all
echo "✅ 배포 완료!"
pm2 status
EOF
chmod +x ~/deploy.sh
```

**이후 배포는:**
```bash
~/deploy.sh
```

---

## 🛠️ 트러블슈팅

### 문제 1: 403 Forbidden 에러

**원인**: Nginx가 `/root/` 폴더에 접근 권한 없음

**해결**:
```bash
# /root 폴더 권한 확인
ls -ld /root
# 출력: drwx------ (root만 접근 가능) → 문제!

# Nginx가 읽을 수 있도록 권한 추가
sudo chmod 755 /root
sudo chmod 755 /root/BH2025_WOWU
sudo chmod -R 755 /root/BH2025_WOWU/frontend

# Nginx 재시작
sudo systemctl reload nginx
```

---

### 문제 2: 404 Not Found

**원인**: 경로가 잘못되었거나 파일이 없음

**확인**:
```bash
# 파일 존재 확인
ls -la /root/BH2025_WOWU/frontend/index.html

# Nginx 설정 확인
sudo nginx -T | grep -A 5 "location /"
```

---

### 문제 3: 변경사항이 반영 안 됨

**원인**: 브라우저 캐시

**해결**:
```bash
# 1. 브라우저 강제 새로고침
# Chrome/Edge: Ctrl + Shift + R (Windows)
# Chrome/Edge: Cmd + Shift + R (Mac)

# 2. 또는 Nginx 캐시 클리어
sudo rm -rf /var/cache/nginx/*
sudo systemctl reload nginx
```

---

### 문제 4: PM2 프로세스 에러

**확인**:
```bash
# PM2 상태 확인
pm2 status

# 로그 확인
pm2 logs bh2025-backend --lines 50

# 재시작
pm2 restart all

# 또는 완전 재시작
pm2 delete all
cd ~/BH2025_WOWU
pm2 start ecosystem.config.cjs
```

---

## 📚 관련 파일

### Nginx 설정 파일
- **메인 설정**: `/etc/nginx/sites-enabled/kdt2025`
- **백업 파일**: `/etc/nginx/sites-enabled/kdt2025.backup.simplify`

### 프로젝트 경로
- **Git 저장소**: `/root/BH2025_WOWU/`
- **프론트엔드**: `/root/BH2025_WOWU/frontend/`
- **백엔드**: `/root/BH2025_WOWU/backend/`

### PM2 설정
- **설정 파일**: `~/BH2025_WOWU/ecosystem.config.cjs`
- **로그 폴더**: `~/BH2025_WOWU/logs/`

---

## 📖 추가 문서

- [RAG 인덱싱 FAQ](./RAG_INDEXING_FAQ.md)
- [RAG 504 타임아웃 해결](./RAG_504_TIMEOUT_FIX.md)
- [Nginx 502 유지보수 페이지](./NGINX_502_MAINTENANCE_PAGE.md)

---

## 🎯 체크리스트

### Nginx 설정 변경 시 (1회만)
- [ ] 설정 백업 완료
- [ ] `location /` 블록의 `root` 경로 변경
- [ ] `sudo nginx -t` 테스트 통과
- [ ] Nginx 재시작 완료
- [ ] 브라우저 접속 확인
- [ ] 강제 새로고침 후 정상 작동 확인

### 일반 배포 시 (매번)
- [ ] `git pull origin hun` 실행
- [ ] 충돌 없이 pull 완료
- [ ] `pm2 restart all` 실행
- [ ] PM2 상태 확인 (`pm2 status`)
- [ ] 브라우저 강제 새로고침
- [ ] 기능 정상 작동 확인

---

## 💡 팁

### 빠른 배포 스크립트 생성

```bash
# ~/deploy.sh 파일 생성
cat > ~/deploy.sh << 'EOF'
#!/bin/bash
cd ~/BH2025_WOWU
echo "📥 최신 코드 가져오는 중..."
git pull origin hun
echo "🔄 백엔드 재시작 중..."
pm2 restart all
echo "✅ 배포 완료!"
pm2 status
EOF

# 실행 권한 부여
chmod +x ~/deploy.sh

# 이후 배포는:
~/deploy.sh
```

---

## 🔐 보안 고려사항

### /root 폴더 권한
- Nginx가 읽을 수 있도록 `755` 권한 필요
- 하위 폴더도 읽기 권한 필요 (`chmod -R 755`)
- 쓰기 권한은 주지 않음 (보안)

### 대안: Symbolic Link
```bash
# /root 권한 변경이 우려된다면:
sudo ln -s /root/BH2025_WOWU/frontend /var/www/html/bh2025-link
# Nginx에서 /var/www/html/bh2025-link 사용
```

---

## 📞 문의

문제 발생 시:
1. 로그 확인: `pm2 logs --lines 100`
2. Nginx 로그: `sudo tail -50 /var/log/nginx/error.log`
3. 설정 확인: `sudo nginx -T | less`

---

**마지막 업데이트**: 2026-01-05  
**작성자**: AI Assistant  
**버전**: 2.0 (Nginx 간소화 버전)
