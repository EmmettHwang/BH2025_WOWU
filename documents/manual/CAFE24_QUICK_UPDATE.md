# Cafe24 서버 패키지 업데이트 가이드 (www.kdt2025.com)

## 🎯 현재 상황
- ✅ 서버 이미 배포되어 실행 중
- ✅ 도메인: www.kdt2025.com
- ✅ PM2로 관리 중
- 🔄 새로운 RAG 패키지 설치 필요

---

## 📋 Python 버전 확인

### 1. SSH 접속
```bash
ssh -p [포트] [사용자명]@[호스트]
```

### 2. Python 버전 확인
```bash
python3 --version
```

**예상 결과**:
- Python 3.9.x → ✅ 그대로 사용
- Python 3.10.x → ✅ 사용 가능
- Python 3.11.x → ✅ 사용 가능
- Python 3.12.x → ⚠️ 일부 패키지 호환 문제 가능

**권장**: Python 3.9 ~ 3.11 사이 버전 사용

---

## 🚀 빠른 업데이트 (추천)

### 프로젝트 디렉토리로 이동
```bash
cd ~/BH2025_WOWU  # 또는 실제 프로젝트 경로
```

### 한 번에 실행
```bash
git pull origin hun && \
source venv/bin/activate && \
cd backend && \
pip install -r requirements.txt --upgrade && \
cd .. && \
pm2 restart all
```

**완료!** 🎉

---

## 📝 단계별 상세 가이드

### 1. 코드 업데이트
```bash
cd ~/BH2025_WOWU
git pull origin hun
```

**예상 출력**:
```
remote: Enumerating objects...
Updating xxxxx..yyyyy
 backend/requirements.txt | 6 ++++++
 ...
```

### 2. 가상환경 활성화
```bash
source venv/bin/activate
```

**프롬프트 변경**: `(venv)` 접두사 표시됨

### 3. 패키지 업데이트
```bash
cd backend
pip install -r requirements.txt --upgrade
```

**소요 시간**: 
- 기존 패키지 대부분 설치되어 있으면: ~2-5분
- 새로운 RAG 패키지 설치 필요하면: ~10-20분

**주요 설치 패키지**:
```
langchain==0.1.0
langchain-community==0.0.10
sentence-transformers==2.3.1
huggingface-hub==0.20.3
```

### 4. PM2 재시작
```bash
cd ..
pm2 restart all
```

### 5. 확인
```bash
pm2 logs bh2025-backend --lines 50
```

**성공 로그**:
```
============================================================
🚀 BH2025 WOWU 백엔드 서버 시작
============================================================

📋 등록된 API 엔드포인트:

📁 Documents API:
  {'GET'} /api/documents/list
  ...

🤖 RAG API:
  {'GET'} /api/rag/status
  ...

[INFO] RAG 시스템 초기화 중...
✅ RAG 시스템 초기화 완료
```

---

## ⚡ 더 간편한 방법 (start-pm2.sh 사용)

### 자동 업데이트
```bash
cd ~/BH2025_WOWU
bash start-pm2.sh --update
```

이 명령어가 자동으로:
1. ✅ `git pull origin hun`
2. ✅ `pip install -r requirements.txt --upgrade`
3. ✅ `pm2 restart`
4. ✅ 로그 확인

---

## 🐛 문제 발생 시

### 패키지 설치 오류

**증상**: `ERROR: Could not install packages`

**해결**:
```bash
# 가상환경 활성화 확인
source venv/bin/activate

# pip 업그레이드
pip install --upgrade pip setuptools wheel

# torch 먼저 설치 (CPU 버전)
pip install torch==2.1.1 --index-url https://download.pytorch.org/whl/cpu

# 나머지 설치
pip install -r requirements.txt
```

### PM2 재시작 실패

**증상**: 서버가 시작되지 않음

**해결**:
```bash
# 로그 확인
pm2 logs bh2025-backend --lines 100

# 프로세스 완전 중지 후 재시작
pm2 delete bh2025-backend
pm2 start ecosystem.config.js
pm2 save
```

### Import 오류

**증상**: `ModuleNotFoundError: No module named 'langchain'`

**해결**:
```bash
source venv/bin/activate
pip install langchain==0.1.0 langchain-community==0.0.10
pm2 restart all
```

### 메모리 부족

**증상**: 서버가 자주 재시작됨

**해결**:
```bash
# ecosystem.config.js 수정
nano ecosystem.config.js

# max_memory_restart 증가 또는 workers 감소
# max_memory_restart: '2G'
# args: '... --workers 2'

pm2 restart all
```

---

## 📊 설치 진행률 확인

### 패키지 설치 중
```bash
# 다른 터미널에서 실시간 확인
watch -n 1 "pip list | grep -E 'langchain|sentence-transformers|faiss'"
```

### 메모리 사용량
```bash
free -m
```

### 디스크 사용량
```bash
df -h
```

---

## ✅ 체크리스트

### 업데이트 전
- [ ] 현재 서버 상태 확인 (`pm2 status`)
- [ ] Python 버전 확인 (`python3 --version`)
- [ ] 디스크 용량 확인 (`df -h`)
- [ ] 현재 브랜치 확인 (`git branch`)

### 업데이트 중
- [ ] `git pull origin hun` 실행
- [ ] 가상환경 활성화
- [ ] `pip install -r requirements.txt --upgrade`
- [ ] 에러 없이 설치 완료 확인

### 업데이트 후
- [ ] `pm2 restart all` 실행
- [ ] `pm2 logs` 로그 확인
- [ ] 브라우저에서 www.kdt2025.com 접속 테스트
- [ ] API 문서 확인: www.kdt2025.com/docs
- [ ] RAG 기능 테스트

---

## 🔄 롤백 (문제 발생 시)

### 이전 버전으로 되돌리기
```bash
cd ~/BH2025_WOWU
git log --oneline -5  # 최근 커밋 확인
git checkout [이전_커밋_해시]
pm2 restart all
```

### 패키지 다운그레이드
```bash
# 이전 requirements.txt 사용
git show HEAD~1:backend/requirements.txt > requirements.old.txt
pip install -r requirements.old.txt
pm2 restart all
```

---

## 💡 팁

### 백업
```bash
# 업데이트 전 백업
cd ~
tar -czf BH2025_backup_$(date +%Y%m%d_%H%M%S).tar.gz BH2025_WOWU/
```

### 무중단 업데이트
```bash
# PM2 reload (무중단)
pm2 reload bh2025-backend
```

### 로그 파일 정리
```bash
pm2 flush  # 모든 로그 삭제
```

---

## 📞 긴급 상황

### 서버 완전히 멈췄을 때
```bash
# 1. 모든 프로세스 중지
pm2 stop all

# 2. 프로세스 삭제
pm2 delete all

# 3. 재시작
pm2 start ecosystem.config.js

# 4. 저장
pm2 save
```

### Python 가상환경 재생성
```bash
cd ~/BH2025_WOWU
rm -rf venv
python3 -m venv venv
source venv/bin/activate
cd backend
pip install -r requirements.txt
cd ..
pm2 restart all
```

---

## 🎯 요약

### 정상적인 경우 (가장 흔함)
```bash
cd ~/BH2025_WOWU
git pull origin hun
source venv/bin/activate
cd backend
pip install -r requirements.txt --upgrade
cd ..
pm2 restart all
```

### start-pm2.sh 사용 (더 간단)
```bash
cd ~/BH2025_WOWU
bash start-pm2.sh --update
```

**끝!** 🎉

---

*최종 수정: 2026-01-05*
