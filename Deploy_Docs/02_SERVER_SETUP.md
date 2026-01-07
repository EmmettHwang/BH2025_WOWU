# ⚙️ 서버 초기 설정 가이드

새로운 서버를 임대한 후 기본 환경을 안전하게 설정하는 방법입니다.

---

## 📋 목차

1. [서버 접속](#서버-접속)
2. [시스템 업데이트](#시스템-업데이트)
3. [필수 패키지 설치](#필수-패키지-설치)
4. [보안 설정](#보안-설정)
5. [방화벽 설정](#방화벽-설정)
6. [사용자 계정 관리](#사용자-계정-관리)
7. [시스템 설정](#시스템-설정)

---

## 🔐 서버 접속

### SSH로 접속

```bash
# 기본 SSH 접속 (포트 22)
ssh root@your-server-ip

# 포트 지정
ssh -p 22 root@your-server-ip

# 일반 사용자로 접속
ssh username@your-server-ip
```

### 비밀번호 변경 (처음 접속 시 권장)

```bash
# root 비밀번호 변경
passwd

# 다른 사용자 비밀번호 변경
passwd username
```

---

## 🔄 시스템 업데이트

### Ubuntu/Debian

```bash
# 패키지 목록 업데이트
sudo apt update

# 설치된 패키지 업그레이드
sudo apt upgrade -y

# 전체 시스템 업그레이드
sudo apt full-upgrade -y

# 불필요한 패키지 제거
sudo apt autoremove -y
sudo apt autoclean
```

### CentOS/RHEL

```bash
# 패키지 업데이트
sudo yum update -y

# 또는 (CentOS 8+)
sudo dnf update -y
```

---

## 📦 필수 패키지 설치

### 기본 개발 도구

```bash
# Ubuntu/Debian
sudo apt install -y \
    curl \
    wget \
    git \
    vim \
    nano \
    build-essential \
    software-properties-common \
    apt-transport-https \
    ca-certificates \
    gnupg \
    lsb-release
```

### 시스템 모니터링 도구

```bash
# htop - 시스템 모니터링
sudo apt install -y htop

# net-tools - 네트워크 도구
sudo apt install -y net-tools

# ncdu - 디스크 사용량 분석
sudo apt install -y ncdu
```

---

## 🛡️ 보안 설정

### 1. SSH 보안 강화

```bash
# SSH 설정 파일 편집
sudo nano /etc/ssh/sshd_config
```

**권장 설정:**
```conf
# SSH 포트 변경 (선택사항, 기본 22에서 변경)
Port 2222

# root 로그인 비활성화 (일반 사용자 생성 후)
PermitRootLogin no

# 비밀번호 인증 비활성화 (SSH 키 설정 후)
PasswordAuthentication no

# 빈 비밀번호 비활성화
PermitEmptyPasswords no

# X11 포워딩 비활성화
X11Forwarding no

# 최대 인증 시도 횟수
MaxAuthTries 3

# 로그인 유예 시간
LoginGraceTime 60
```

```bash
# SSH 재시작
sudo systemctl restart sshd

# 새 터미널에서 접속 테스트 후 기존 터미널 종료
```

### 2. SSH 키 인증 설정

#### 로컬 컴퓨터에서 키 생성

```bash
# ED25519 키 생성 (권장)
ssh-keygen -t ed25519 -C "your-email@example.com"

# RSA 키 생성 (구버전 호환)
ssh-keygen -t rsa -b 4096 -C "your-email@example.com"
```

#### 서버에 공개 키 복사

```bash
# 자동 복사 (로컬에서 실행)
ssh-copy-id -p 22 root@your-server-ip

# 수동 복사
cat ~/.ssh/id_ed25519.pub | ssh root@your-server-ip "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys"
```

#### 서버에서 권한 설정

```bash
# .ssh 디렉토리 권한
chmod 700 ~/.ssh

# authorized_keys 파일 권한
chmod 600 ~/.ssh/authorized_keys
```

### 3. Fail2Ban 설치 (무차별 대입 공격 방어)

```bash
# Fail2Ban 설치
sudo apt install -y fail2ban

# 설정 파일 복사
sudo cp /etc/fail2ban/jail.conf /etc/fail2ban/jail.local

# 설정 편집
sudo nano /etc/fail2ban/jail.local
```

**권장 설정:**
```ini
[DEFAULT]
bantime  = 3600      # 차단 시간 (1시간)
findtime = 600       # 감지 시간 (10분)
maxretry = 5         # 최대 시도 횟수

[sshd]
enabled = true
port = ssh
logpath = /var/log/auth.log
```

```bash
# Fail2Ban 시작 및 자동 시작 설정
sudo systemctl start fail2ban
sudo systemctl enable fail2ban

# 상태 확인
sudo fail2ban-client status
sudo fail2ban-client status sshd
```

---

## 🔥 방화벽 설정

### UFW (Uncomplicated Firewall)

```bash
# UFW 설치 (Ubuntu는 기본 설치됨)
sudo apt install -y ufw

# 기본 정책: 들어오는 연결 차단, 나가는 연결 허용
sudo ufw default deny incoming
sudo ufw default allow outgoing

# SSH 포트 허용 (반드시 먼저!)
sudo ufw allow 22/tcp
# 또는 SSH 포트를 변경했다면
sudo ufw allow 2222/tcp

# HTTP/HTTPS 허용
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# 개발용 포트 허용 (선택사항)
sudo ufw allow 3000/tcp  # Frontend
sudo ufw allow 8000/tcp  # Backend

# UFW 활성화
sudo ufw enable

# 상태 확인
sudo ufw status verbose

# 규칙 번호와 함께 확인
sudo ufw status numbered
```

### 특정 IP만 허용

```bash
# 특정 IP에서만 SSH 접속 허용
sudo ufw allow from 203.0.113.100 to any port 22

# IP 범위 허용
sudo ufw allow from 203.0.113.0/24 to any port 22
```

### 규칙 삭제

```bash
# 번호로 삭제
sudo ufw status numbered
sudo ufw delete 3

# 직접 삭제
sudo ufw delete allow 3000/tcp
```

---

## 👤 사용자 계정 관리

### 새 사용자 추가

```bash
# 사용자 추가
sudo adduser deploy

# sudo 권한 부여
sudo usermod -aG sudo deploy

# 사용자 확인
id deploy
groups deploy
```

### SSH 키 복사 (root → 일반 사용자)

```bash
# root에서 실행
sudo rsync --archive --chown=deploy:deploy ~/.ssh /home/deploy
```

### 사용자 전환 테스트

```bash
# 일반 사용자로 전환
su - deploy

# sudo 테스트
sudo apt update
```

---

## ⚙️ 시스템 설정

### 시간대 설정

```bash
# 현재 시간 확인
date

# 시간대 목록 확인
timedatectl list-timezones

# 서울 시간대로 설정
sudo timedatectl set-timezone Asia/Seoul

# 확인
timedatectl
```

### 호스트명 변경

```bash
# 현재 호스트명 확인
hostname

# 호스트명 변경
sudo hostnamectl set-hostname bh2025-server

# /etc/hosts 파일 수정
sudo nano /etc/hosts
```

**/etc/hosts 예시:**
```
127.0.0.1 localhost
127.0.1.1 bh2025-server

# IPv6
::1 localhost ip6-localhost ip6-loopback
```

### 스왑 메모리 설정 (RAM이 부족한 경우)

```bash
# 현재 스왑 확인
free -h

# 2GB 스왑 파일 생성
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# 영구 설정
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab

# 스왑 사용 정도 조정 (기본 60, 낮을수록 RAM 우선)
sudo sysctl vm.swappiness=10
echo 'vm.swappiness=10' | sudo tee -a /etc/sysctl.conf

# 확인
free -h
```

### 자동 보안 업데이트

```bash
# unattended-upgrades 설치
sudo apt install -y unattended-upgrades

# 설정
sudo dpkg-reconfigure -plow unattended-upgrades

# 수동 설정
sudo nano /etc/apt/apt.conf.d/50unattended-upgrades
```

---

## 📊 시스템 모니터링

### 기본 명령어

```bash
# CPU, 메모리, 프로세스 확인
htop

# 디스크 사용량
df -h

# 디렉토리별 사용량
du -sh /*
ncdu /

# 네트워크 연결 확인
netstat -tulnp
# 또는
ss -tulnp

# 실시간 로그 확인
sudo tail -f /var/log/syslog
sudo tail -f /var/log/auth.log
```

### 시스템 정보 확인

```bash
# OS 버전
cat /etc/os-release
lsb_release -a

# 커널 버전
uname -r

# CPU 정보
lscpu

# 메모리 정보
free -h

# 디스크 정보
lsblk
fdisk -l
```

---

## ✅ 초기 설정 체크리스트

### 필수 설정
- [ ] 서버 접속 확인
- [ ] root 비밀번호 변경
- [ ] 시스템 업데이트
- [ ] 필수 패키지 설치
- [ ] 방화벽 설정 (UFW)
- [ ] SSH 포트 허용 확인

### 보안 설정
- [ ] SSH 키 인증 설정
- [ ] SSH 비밀번호 로그인 비활성화
- [ ] root 로그인 비활성화
- [ ] Fail2Ban 설치
- [ ] 일반 사용자 계정 생성
- [ ] sudo 권한 설정

### 추가 설정
- [ ] 시간대 설정
- [ ] 호스트명 설정
- [ ] 스왑 메모리 설정
- [ ] 자동 보안 업데이트
- [ ] 모니터링 도구 설치

---

## 🔧 일반적인 문제 해결

### SSH 접속 안 됨

```bash
# SSH 서비스 상태 확인
sudo systemctl status sshd

# SSH 재시작
sudo systemctl restart sshd

# 방화벽 규칙 확인
sudo ufw status

# SSH 포트 확인
sudo netstat -tlnp | grep sshd
```

### UFW 활성화 후 SSH 접속 안 됨

```bash
# 콘솔/VNC로 접속 필요
# SSH 포트 허용
sudo ufw allow 22/tcp

# UFW 재시작
sudo ufw disable
sudo ufw enable
```

### 디스크 공간 부족

```bash
# 디스크 사용량 확인
df -h

# 큰 파일 찾기
sudo du -ah / | sort -rh | head -20

# 로그 파일 정리
sudo journalctl --vacuum-time=3d
sudo apt autoremove -y
sudo apt autoclean
```

---

## 🔗 다음 단계

서버 기본 설정이 완료되면:

1. [전체 배포 가이드](./01_DEPLOYMENT_GUIDE.md) - 프로젝트 배포
2. [보안 설정 가이드](./07_SECURITY_GUIDE.md) - 고급 보안 설정

---

## 📞 참고 자료

- Ubuntu Server Guide: https://ubuntu.com/server/docs
- UFW 문서: https://help.ubuntu.com/community/UFW
- Fail2Ban 문서: https://www.fail2ban.org/

---

**작성자**: EmmettHwang  
**마지막 업데이트**: 2024-12-XX  
**버전**: 1.0.0
