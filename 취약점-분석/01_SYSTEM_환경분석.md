# 01. SYSTEM 환경분석

> 진단 전 대상 시스템의 기본 정보를 수집하는 단계. 포트·데몬·계정 분석으로 진단 범위 확정.

---

## 1. 가상환경 구성 (VirtualBox)

```
1. https://www.virtualbox.org/ 접속 → 다운로드 및 설치
2. 환경 설정 → 호스트 키 조합 단축키 설정
3. 가상이미지 "새로 만들기"로 VM 생성
4. 가상이미지 구동 확인
5. Local PC IP 주소 확인
6. Putty로 가상 머신 SSH 접근
```

---

## 2. 기본정보 수집

진단 대상의 플랫폼과 버전을 파악.

| 항목 | 내용 |
|------|------|
| **OS** | Platform 명 & 버전 (예: CentOS 6.x) |
| **DBMS** | Platform 명 & 버전 (예: MySQL 5.x) |
| **WEB Server** | Platform 명 & 버전 (예: Apache 2.x) |
| **WAS** | Platform 명 & 버전 (예: Tomcat) |

---

## 3. 포트 분석

**명령어**
```bash
netstat -tlnp
```

**출력 예시**
```
Proto  Local Address       State    PID/Program name
tcp    0.0.0.0:3306        LISTEN   2000/mysqld
tcp    0.0.0.0:111         LISTEN   1437/rpcbind
tcp    0.0.0.0:22          LISTEN   1861/sshd
tcp    127.0.0.1:631       LISTEN   1538/cupsd
tcp    127.0.0.1:25        LISTEN   2102/master
```

**분석 정리 양식**

| Proto | Local Address | Well Known 여부 | Program name | 비고 |
|-------|--------------|-----------------|--------------|------|
| tcp | 0.0.0.0:22 | Y (ssh) | sshd | SSH 연결 Port |
| tcp | 0.0.0.0:3306 | Y (mysql) | mysqld | DBMS 서비스 Port |

> 불필요하게 열린 포트, 외부(0.0.0.0)로 노출된 서비스 포트를 식별.

### 포트 기본 개념

| 구분 | 범위 | 설명 |
|------|------|------|
| **Well-Known Port** | 0 ~ 1023 | 표준 서비스 예약 포트 (SSH 22, HTTP 80 등). root만 바인딩 가능 |
| **Registered Port** | 1024 ~ 49151 | 등록 포트 (MySQL 3306, Tomcat 8080 등) |
| **Dynamic/Private Port** | 49152 ~ 65535 | 클라이언트 임시 포트, 동적 할당 |

**바인딩 주소(Local Address)의 의미**

| 표기 | 의미 | 보안 관점 |
|------|------|----------|
| `0.0.0.0:포트` | 모든 인터페이스에서 접근 허용 (외부 노출) | ⚠️ 외부 접근 가능 — 방화벽·접근제어 필요 |
| `127.0.0.1:포트` | 로컬(루프백)에서만 접근 | 🟢 외부 차단됨, 상대적으로 안전 |
| `10.0.0.x:포트` | 특정 내부 IP에서만 접근 | 내부망 한정 |

### 주요 Well-Known 포트 및 보안 위험

| 포트 | 프로토콜 | 서비스 | 데몬 | 보안 위험 / 진단 항목 |
|:---:|:---:|------|------|------|
| 21 | TCP | FTP | vsftpd, proftpd | 평문 전송 → 계정 스니핑. 익명 접속(U-35). SFTP/FTPS 권장 |
| 22 | TCP | SSH | sshd | 안전(암호화). root 직접접속 차단(U-01), 무차별 대입 대비 |
| 23 | TCP | Telnet | telnetd | ⚠️ 평문 전송. 비활성화 대상(U-52) → SSH 대체 |
| 25 | TCP | SMTP | sendmail, postfix | 스팸 릴레이(U-47), 버전 노출(U-45) |
| 53 | TCP/UDP | DNS | named(BIND) | Zone Transfer 유출(U-50), 버전 취약점(U-49) |
| 69 | UDP | TFTP | tftpd | ⚠️ 인증 없음. 비활성화 대상(U-44) |
| 79 | TCP | Finger | fingerd | ⚠️ 사용자 정보 노출. 비활성화(U-34) |
| 80 | TCP | HTTP | httpd, nginx | 웹 공격 표면(SQLi, XSS). WAF 권장 |
| 110 | TCP | POP3 | dovecot | 평문 인증 위험 → POP3S(995) |
| 111 | TCP/UDP | RPC (portmapper) | rpcbind | ⚠️ 버퍼오버플로우·DoS(U-42). 불필요 시 중지 |
| 135 | TCP | MS RPC | - | ⚠️ Windows RPC. 외부 노출 금지 |
| 137~139 | TCP/UDP | NetBIOS | smbd | ⚠️ 공유 자원 노출(W-20). 외부 차단 |
| 143 | TCP | IMAP | dovecot | 평문 인증 위험 → IMAPS(993) |
| 161/162 | UDP | SNMP | snmpd | ⚠️ Community String 노출(U-59~61). v3 사용 |
| 443 | TCP | HTTPS | httpd, nginx | SSL/TLS. 인증서·프로토콜 버전 관리 |
| 445 | TCP | SMB | smbd | ⚠️ 랜섬웨어 확산 경로. 외부 차단 |
| 512~514 | TCP | r-services (rlogin/rsh/rexec) | - | ⚠️ 인증 없는 원격 실행. 비활성화(U-36) |
| 631 | TCP | CUPS (프린터) | cupsd | 로컬 한정 권장. 불필요 시 중지 |
| 2049 | TCP/UDP | NFS | nfsd | ⚠️ 인가 없는 마운트(U-39, U-40) |
| 3306 | TCP | MySQL | mysqld | DB 서비스. 외부 노출 금지, 로컬/내부망 한정 |
| 1521 | TCP | Oracle | tnslsnr | DB 서비스. 외부 노출 금지 |
| 5432 | TCP | PostgreSQL | postgres | DB 서비스. 외부 노출 금지 |
| 3389 | TCP | RDP | - | ⚠️ Windows 원격데스크톱. 접속 그룹 제한(W-14) |
| 8080 | TCP | HTTP-Alt (Tomcat/WAS) | java | WAS 관리 포트 노출 주의 |

### 포트 분석 시 진단 포인트

- **불필요한 서비스 포트**: telnet(23), finger(79), rsh(514), tftp(69) 등이 열려 있으면 취약 → 중지
- **외부 노출(0.0.0.0) DB 포트**: 3306, 1521, 5432가 외부로 열려 있으면 심각 → 로컬/내부망 바인딩으로 변경
- **RPC/NFS 계열**: 111, 2049는 취약점이 많으므로 미사용 시 반드시 중지
- **평문 프로토콜**: FTP(21), Telnet(23)은 암호화 버전으로 대체 (SFTP, SSH)

### 관련 명령어

```bash
netstat -tlnp          # TCP LISTEN 포트 + PID/프로그램
netstat -ulnp          # UDP 포트
ss -tlnp               # netstat 대체 (최신 배포판)
lsof -i :3306          # 특정 포트 사용 프로세스 확인
cat /etc/services      # 포트-서비스 매핑 표준 정의 (U-22)
```

> **옵션 의미**: `-t` TCP, `-u` UDP, `-l` LISTEN 상태, `-n` 숫자 표기(이름 변환 안 함), `-p` PID/프로그램명 표시

---

## 4. Daemon 분석


**명령어**
```bash
ps -ef | grep "httpd\|mysql\|rpc*"
```

**출력 예시**
```
mysql   2000  1898  ... /usr/libexec/mysqld --datadir=/var/lib/mysql ...
apache  24342 2142  ... /usr/sbin/httpd
rpc     1437  1     ... rpcbind
```

**분석 정리 양식**

| RUSER | Daemon (Command) | 목적 | 경로 | 비고 |
|-------|-----------------|------|------|------|
| root | mysqld_safe | mysql_safe 구동 확인 | datadir=/var/lib/mysql | - |
| mysql | mysqld | mysql 구동 | datadir=/var/lib/mysql | - |

> 어떤 계정으로 어떤 데몬이 구동되는지 확인 → 권한 오용·불필요 서비스 식별.

---

## 5. 계정 분석

**명령어**
```bash
cat /etc/passwd | grep bash
```

**출력 예시**
```
root:x:0:0:root:/root:/bin/bash
adiosl:x:500:500:adiosl:/home/adiosl:/bin/bash
mysql:x:27:27:MySQL Server:/var/lib/mysql:/bin/bash
cubrid:x:501:501::/home/cubrid:/bin/bash
```

**분석 정리 양식**

| Username | Account Info | Home directory | Command/shell | 비고 |
|----------|-------------|----------------|---------------|------|
| root | 관리자 계정 | /root | /bin/bash | 최고관리자 |
| mysql | mysql 구동 계정 | /var/lib/mysql | /bin/bash | 서비스 계정 |

> 로그인 가능한 계정(`/bin/bash`), 서비스 계정, UID 0 계정을 식별.

---

## 6. 분석 총평 작성 항목

환경분석 완료 후 다음 항목을 종합 정리:

- **기본 정보**: OS/DBMS/WEB/WAS 버전 및 EOS(지원 종료) 여부
- **Port 정보**: 불필요하게 열린 포트, 외부 노출 서비스
- **Daemon 정보**: 불필요 서비스, 취약 데몬(rpcbind, telnet 등)
- **계정 정보**: 불필요 계정, UID 0 중복, 서비스 계정의 쉘 부여 여부

> 이 총평을 기반으로 U/W 항목별 상세 진단을 진행.
