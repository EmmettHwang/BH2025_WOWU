# Cafe24 서버 MySQL 포트 개방 가이드

## 현재 상황
- DB 위치: Cafe24 서버 (114.202.247.97)
- 문제: 포트 3306이 외부에서 접근 불가
- 필요: 방화벽 포트 개방 + MySQL 외부 접속 허용

---

## 🔥 방화벽 종류 확인 및 설정

### 1단계: 방화벽 종류 확인

```bash
# Cafe24 서버에서 실행
ssh root@114.202.247.97

# 방화벽 종류 확인
systemctl status firewalld 2>/dev/null && echo "==> firewalld 사용 중" || echo "firewalld 없음"
systemctl status ufw 2>/dev/null && echo "==> ufw 사용 중" || echo "ufw 없음"
which iptables 2>/dev/null && echo "==> iptables 사용 가능" || echo "iptables 없음"
```

---

### 2단계: 방화벽 종류별 포트 개방

#### A) firewalld를 사용하는 경우 (CentOS/RHEL)

```bash
# 포트 3306 개방
firewall-cmd --permanent --add-port=3306/tcp

# 또는 MySQL 서비스로 개방
firewall-cmd --permanent --add-service=mysql

# 설정 적용
firewall-cmd --reload

# 확인
firewall-cmd --list-ports
firewall-cmd --list-services
```

#### B) ufw를 사용하는 경우 (Ubuntu/Debian)

```bash
# 포트 3306 개방
ufw allow 3306/tcp

# 확인
ufw status
```

#### C) iptables를 직접 사용하는 경우

```bash
# 포트 3306 개방
iptables -A INPUT -p tcp --dport 3306 -j ACCEPT

# 설정 저장 (Ubuntu/Debian)
netfilter-persistent save
# 또는
iptables-save > /etc/iptables/rules.v4

# 설정 저장 (CentOS 7 이하)
service iptables save

# 확인
iptables -L -n | grep 3306
```

#### D) 방화벽이 없는 경우

```bash
# Cafe24 호스팅 제어판에서 포트 개방 필요
# 웹 호스팅 관리 → 방화벽 설정 → 포트 추가
```

---

## 🗄️ MySQL/MariaDB 외부 접속 설정

### 3단계: MySQL 설정 파일 수정

```bash
# 설정 파일 찾기
find /etc -name "my.cnf" -o -name "*.cnf" 2>/dev/null | grep -E "(my.cnf|server.cnf)"

# 일반적인 위치:
# - /etc/my.cnf
# - /etc/mysql/my.cnf
# - /etc/mysql/mysql.conf.d/mysqld.cnf
# - /etc/my.cnf.d/server.cnf

# 설정 파일 편집
nano /etc/my.cnf
# 또는
nano /etc/mysql/mysql.conf.d/mysqld.cnf
```

**[mysqld] 섹션에 추가/수정:**
```ini
[mysqld]
# 모든 IP에서 접속 허용
bind-address = 0.0.0.0

# 또는 주석 처리
# bind-address = 127.0.0.1
```

---

### 4단계: MySQL 재시작

```bash
# MariaDB 재시작
systemctl restart mariadb

# 또는 MySQL 재시작
systemctl restart mysql

# 실행 확인
systemctl status mariadb
# 또는
systemctl status mysql

# 포트 리스닝 확인
netstat -tlnp | grep 3306
# 또는
ss -tlnp | grep 3306
```

**결과 예시:**
```
tcp        0      0 0.0.0.0:3306      0.0.0.0:*     LISTEN      1234/mysqld
```
- `0.0.0.0:3306` → ✅ 모든 IP에서 접속 가능
- `127.0.0.1:3306` → ❌ localhost만 접속 가능

---

### 5단계: MySQL 사용자 권한 부여

```bash
# MySQL 접속
mysql -u root -p
# 비밀번호: dodan1004~!@
```

**MySQL 프롬프트에서 실행:**
```sql
-- 현재 root 사용자 호스트 확인
SELECT Host, User FROM mysql.user WHERE User='root';

-- root@'%' (모든 IP) 권한이 없으면 추가
GRANT ALL PRIVILEGES ON bh2025.* TO 'root'@'%' IDENTIFIED BY 'dodan1004~!@';

-- 또는 특정 IP만 허용 (더 안전)
-- GRANT ALL PRIVILEGES ON bh2025.* TO 'root'@'샌드박스IP' IDENTIFIED BY 'dodan1004~!@';

-- 권한 적용
FLUSH PRIVILEGES;

-- 확인
SHOW GRANTS FOR 'root'@'%';

-- 종료
EXIT;
```

---

## 🧪 연결 테스트

### 6단계: Cafe24 서버에서 로컬 테스트

```bash
# 같은 서버 내에서 테스트
mysql -u root -p -h 127.0.0.1 -P 3306 bh2025 -e "SHOW TABLES;"

# 외부 IP로 테스트
mysql -u root -p -h 114.202.247.97 -P 3306 bh2025 -e "SHOW TABLES;"
```

### 7단계: 샌드박스에서 테스트

샌드박스로 돌아와서:
```bash
# Backend 재시작
pm2 restart bhhs-backend

# DB 연결 테스트
curl http://localhost:8000/health
```

---

## 📋 문제 해결 체크리스트

- [ ] MySQL/MariaDB 실행 중인가? (`systemctl status mariadb`)
- [ ] bind-address가 0.0.0.0인가? (`grep bind-address /etc/my.cnf`)
- [ ] 방화벽에서 3306 포트가 열려 있는가? (`firewall-cmd --list-ports`)
- [ ] MySQL에서 root@'%' 권한이 있는가? (`SELECT Host FROM mysql.user WHERE User='root';`)
- [ ] MySQL이 0.0.0.0:3306에서 리스닝 중인가? (`netstat -tlnp | grep 3306`)

---

## 🔐 보안 권장사항

### 방법 1: 특정 IP만 허용 (권장)

```sql
-- root@'%' 대신 샌드박스 IP만 허용
GRANT ALL PRIVILEGES ON bh2025.* TO 'root'@'샌드박스_IP' IDENTIFIED BY 'dodan1004~!@';

-- 방화벽도 특정 IP만 허용
firewall-cmd --permanent --add-rich-rule='rule family="ipv4" source address="샌드박스_IP" port protocol="tcp" port="3306" accept'
```

### 방법 2: 별도 사용자 생성 (더 권장)

```sql
-- root 대신 전용 사용자 생성
CREATE USER 'bhapp'@'%' IDENTIFIED BY 'secure_password';
GRANT ALL PRIVILEGES ON bh2025.* TO 'bhapp'@'%';
FLUSH PRIVILEGES;
```

그 다음 `.env` 파일 수정:
```bash
DB_USER=bhapp
DB_PASSWORD=secure_password
```

---

## 🎯 완료 후 최종 확인

```bash
# 1. Cafe24 서버에서
netstat -tlnp | grep 3306
mysql -u root -p -h 114.202.247.97 bh2025 -e "SELECT VERSION();"

# 2. 샌드박스에서
curl http://localhost:8000/health

# 예상 결과:
# {"status":"healthy","database":"connected"}
```

---

**작업 순서 요약:**
1. ✅ 방화벽 종류 확인
2. ✅ 포트 3306 개방
3. ✅ MySQL bind-address 변경
4. ✅ MySQL 재시작
5. ✅ root@'%' 권한 부여
6. ✅ 연결 테스트
