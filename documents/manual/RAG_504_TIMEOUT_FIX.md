# RAG 504 Gateway Timeout 에러 해결 가이드

## 🔴 문제 상황

### 증상
1. **504 Gateway Timeout 에러** 발생
   ```
   POST https://www.kdt2025.com/api/rag/index-document 504 (Gateway Time-out)
   ```

2. **앞뒤가 안 맞는 결과**
   - 에러 로그: "RAG 인덱싱 실패"
   - 화면 표시: "업로드 완료" ✅ (잘못된 메시지)

3. **긴 처리 시간**
   - RAG 인덱싱이 너무 오래 걸림 (1~2분)
   - Nginx 기본 타임아웃(60초) 초과

---

## 🎯 해결 방법

### 1️⃣ Nginx 타임아웃 설정 증가

#### 명령어
```bash
# Cafe24 서버에서 실행

# 1. 백업
sudo cp /etc/nginx/sites-enabled/kdt2025 /etc/nginx/sites-enabled/kdt2025.backup.$(date +%Y%m%d)

# 2. 설정 편집
sudo nano /etc/nginx/sites-enabled/kdt2025
```

#### 수정 내용
`location /api/` 블록 안에 아래 3줄 추가:

```nginx
location /api/ {
    proxy_pass http://localhost:8000;
    proxy_http_version 1.1;
    proxy_set_header Upgrade $http_upgrade;
    proxy_set_header Connection 'upgrade';
    proxy_set_header Host $host;
    proxy_cache_bypass $http_upgrade;
    proxy_set_header X-Real-IP $remote_addr;
    proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto $scheme;
    
    # ⭐ RAG 처리를 위한 타임아웃 증가 (추가!)
    proxy_read_timeout 300s;      # 읽기 타임아웃: 5분
    proxy_connect_timeout 300s;   # 연결 타임아웃: 5분
    proxy_send_timeout 300s;      # 전송 타임아웃: 5분
}
```

#### 적용
```bash
# 3. 설정 테스트
sudo nginx -t

# 4. Nginx 재시작
sudo systemctl reload nginx
```

---

### 2️⃣ 프론트엔드 업데이트

```bash
cd ~/BH2025_WOWU
git pull origin hun
sudo cp -r ~/BH2025_WOWU/frontend/* /var/www/html/bh2025/
sudo chown -R www-data:www-data /var/www/html/bh2025
```

#### 브라우저 강제 새로고침
- **Windows/Linux**: `Ctrl + Shift + R`
- **Mac**: `Cmd + Shift + R`

---

## ✅ 변경 사항

### Before (문제)
| 항목 | 값 | 문제 |
|------|-----|------|
| Nginx 타임아웃 | 60초 | RAG 처리 중 504 에러 |
| 프론트엔드 타임아웃 | 기본값 | Nginx보다 짧음 |
| 에러 처리 | try-catch로 무시 | 실패해도 "업로드 완료" 표시 |

### After (해결)
| 항목 | 값 | 효과 |
|------|-----|------|
| Nginx 타임아웃 | **300초 (5분)** | 긴 처리도 대기 |
| 프론트엔드 타임아웃 | **300초 (5분)** | Nginx와 동일 |
| 에러 처리 | **에러 throw** | 실패 시 제대로 된 에러 메시지 |

---

## 🧪 테스트 방법

### 1. PDF 업로드
1. https://www.kdt2025.com 접속
2. 로그인
3. **문서 관리** 탭
4. 큰 PDF 파일 선택 (10MB 이상)
5. "RAG 시스템에 인덱싱?" → **예**

### 2. 확인 사항
- ✅ 504 에러 없이 처리 완료
- ✅ 프로그레스바가 0% → 90% → 100% 진행
- ✅ 애니메이션이 백엔드 완료까지 반복
- ✅ 완료 시 "업로드 완료" 메시지
- ✅ 실패 시 에러 메시지 (504가 아닌 실제 에러)

### 3. 실패 시 확인
```bash
# Nginx 에러 로그
sudo tail -50 /var/log/nginx/error.log

# 백엔드 로그
pm2 logs bh2025-backend --lines 50
```

---

## 📊 성능 개선

| 항목 | Before | After |
|------|--------|-------|
| 최대 처리 시간 | 60초 (504 에러) | 300초 (5분) |
| 에러 표시 | ❌ 잘못된 메시지 | ✅ 정확한 에러 |
| 사용자 경험 | 혼란스러움 | 명확함 |

---

## 🔧 추가 최적화 (선택사항)

### 백엔드 RAG 처리 속도 개선

만약 여전히 느리다면, 백엔드에서 다음을 고려:

1. **배치 크기 조정**
   - 임베딩 생성 시 배치 크기 증가

2. **GPU 활용**
   - CUDA 사용 가능 시 GPU로 임베딩 생성

3. **문서 청크 크기 조정**
   - 너무 작은 청크는 처리 시간 증가

---

## 📝 커밋 정보

- **커밋 해시**: `80f7305`
- **브랜치**: `hun`
- **GitHub**: https://github.com/EmmettHwang/BH2025_WOWU/commit/80f7305

---

## 💡 주의사항

1. **Nginx 타임아웃 설정**은 서버 재시작 후에도 유지됩니다.
2. 프론트엔드는 브라우저 캐시 때문에 **강제 새로고침** 필요.
3. 타임아웃이 길어지면 사용자가 기다리는 시간도 길어지므로, **애니메이션**이 중요합니다.

---

## 🎉 완료!

이제 RAG 인덱싱이 오래 걸려도 504 에러 없이 정상 처리됩니다! 🚀
