# 로컬 DB 설정 가이드

## 📋 복구한 DB 정보를 입력해주세요

### MySQL/MariaDB인 경우:
```bash
cd /home/user/webapp/backend
nano .env
```

**.env 파일 수정:**
```bash
# 로컬 MySQL/MariaDB
DB_HOST=localhost
DB_PORT=3306
DB_USER=root  # 또는 복구한 사용자명
DB_PASSWORD=your_password
DB_NAME=bh2025

# FTP는 기존 유지
FTP_HOST=bitnmeta2.synology.me
FTP_PORT=2121
FTP_USER=ha
FTP_PASSWORD=dodan1004~

# OpenAI (필요시)
# OPENAI_API_KEY=your_key
```

### PostgreSQL인 경우:
```bash
# backend/main.py에서 pymysql 대신 psycopg2 사용 필요
# .env 파일:
DB_HOST=localhost
DB_PORT=5432
DB_USER=postgres
DB_PASSWORD=your_password
DB_NAME=bh2025
```

### SQLite인 경우:
```bash
# backend/main.py 수정 필요 (PyMySQL → sqlite3)
# .env 파일:
DB_PATH=/home/user/webapp/database/bh2025.db
```

## 🔧 백엔드 재시작

```bash
# .env 수정 후
cd /home/user/webapp
pm2 restart bhhs-backend

# 로그 확인
pm2 logs bhhs-backend --nostream

# DB 연결 테스트
curl http://localhost:8000/health
```

## 🧪 DB 연결 테스트

```bash
# MySQL인 경우
mysql -u root -p -h localhost -P 3306 bh2025 -e "SHOW TABLES;"

# PostgreSQL인 경우
psql -h localhost -p 5432 -U postgres -d bh2025 -c "\dt"

# SQLite인 경우
sqlite3 /path/to/bh2025.db ".tables"
```

## ❓ 필요한 정보

1. **DB 종류**: MySQL / PostgreSQL / SQLite / 기타
2. **호스트**: localhost (기본)
3. **포트**: 3306 (MySQL) / 5432 (PostgreSQL) / 없음 (SQLite)
4. **데이터베이스명**: bh2025 (기본)
5. **사용자명**: ?
6. **비밀번호**: ?

정보를 알려주시면 정확한 설정을 도와드리겠습니다!
