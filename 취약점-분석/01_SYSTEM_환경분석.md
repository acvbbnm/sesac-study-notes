# 01. SYSTEM 환경분석

> 진단 전 대상 시스템의 기본 정보를 수집하는 단계. 포트·데몬·계정 분석으로 진단 범위 확정.

---

## 1. 가상환경 구성 (VirtualBox)

진단 실습은 실제 운영 시스템에 영향을 주지 않도록 가상머신(VM)에서 수행한다.

```
1. https://www.virtualbox.org/ 접속 → 다운로드 및 설치
2. 환경 설정 → 호스트 키 조합 단축키 설정
3. 가상이미지 "새로 만들기"로 VM 생성
4. 가상이미지 구동 확인
5. Local PC IP 주소 확인
6. Putty로 가상 머신 SSH 접근
```

**호스트 키(Host Key)**: VM 화면에 갇힌 마우스·키보드를 호스트로 되돌리는 키.
- VirtualBox 기본값: **오른쪽 Ctrl** (창 우측 하단에 현재 호스트 키 표시)
- VMware 기본값: **Ctrl + Alt**

**SSH 접속 (PuTTY)**
```
Host Name: <VM IP>   Port: 22   Connection type: SSH
```
> 비밀번호 입력 시 화면에 아무것도 표시되지 않는 것이 정상(에코 없음).

---

## 2. 기본정보 수집

진단 대상의 플랫폼과 버전을 파악. **버전 정보는 패치 관리(U-64/W-38)·EOS 판단의 기준**이 된다.

| 항목 | 내용 | 확인 명령어 |
|------|------|-------------|
| **OS** | 배포판 & 커널 버전 (예: CentOS 7.9) | `cat /etc/*release`, `uname -a` |
| **DBMS** | DB 종류 & 버전 (예: MySQL 5.7) | `mysql --version`, `sqlplus -v` |
| **WEB Server** | 웹서버 & 버전 (예: Apache 2.4) | `httpd -v`, `nginx -v` |
| **WAS** | 애플리케이션 서버 (예: Tomcat 9) | `catalina.sh version` |

**EOS(End of Service) 개념**  
벤더의 기술 지원·보안 패치가 종료된 상태. EOS 제품은 신규 취약점이 나와도 패치가 제공되지 않으므로 그 자체로 **심각한 취약점**. 기본정보 수집 시 각 플랫폼의 EOS 도래 여부를 반드시 확인한다.

예) CentOS 6 (2020 EOS), CentOS 8 (2021 EOS), Windows Server 2008 (2020 EOS)

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
UID     PID   PPID  C  STIME  TTY  TIME      CMD
root    1898  1     0  Mar16  ?    00:00:00  /bin/sh /usr/bin/mysqld_safe --datadir=/var/lib/mysql ...
mysql   2000  1898  0  Mar16  ?    00:01:58  /usr/libexec/mysqld --datadir=/var/lib/mysql --user=mysql ...
apache  24342 2142  0  Mar21  ?    00:00:00  /usr/sbin/httpd
rpc     1437  1     0  Mar16  ?    00:00:00  rpcbind
```

### ps -ef 필드 설명

| 필드 | 의미 | 진단 관점 |
|------|------|----------|
| **UID** | 프로세스를 실행한 사용자(소유자) | root로 불필요하게 실행되는 서비스 식별 (권한 최소화) |
| **PID** | Process ID — 프로세스 고유 번호 | 프로세스 지정·종료(kill) 시 사용 |
| **PPID** | Parent PID — 부모 프로세스의 PID | 어떤 프로세스가 자식을 띄웠는지 추적. 비정상 부모 = 악성 의심 |
| **C** | CPU 사용률(스케줄링 지표) | 비정상적으로 높으면 이상 프로세스 의심 |
| **STIME** | 프로세스 시작 시각 | 서버 부팅 시각과 다른 임의 실행 프로세스 탐지 |
| **TTY** | 제어 터미널 (`?`=터미널 없음=데몬) | `?`는 백그라운드 데몬, `pts/0`은 사용자 세션 |
| **TIME** | 누적 CPU 사용 시간 | 장시간 점유 프로세스 식별 |
| **CMD** | 실행 명령어(전체 경로+인자) | 실제 실행 파일 경로·옵션 확인 |

### PID / PPID 계층 관계

```
PID 1 (systemd 또는 init)      ← 모든 프로세스의 최상위 부모
 └─ PID 1898  mysqld_safe      (PPID=1,    root로 구동)
     └─ PID 2000  mysqld       (PPID=1898, mysql 계정으로 실제 DB 구동)
```

- **PPID로 부모를 추적**하면 프로세스가 정상 경로로 뜬 것인지 확인 가능
- 예: `mysqld`(PID 2000)의 PPID가 1898(mysqld_safe)이므로 정상. 만약 웹서버(httpd)의 자식으로 셸(/bin/sh)이 떠 있다면 **웹쉘·명령 인젝션** 의심
- PID 1의 부모(PPID 0)는 커널. init/systemd가 고아 프로세스를 입양

### 분석 정리 양식

| RUSER (UID) | PID | PPID | Daemon (CMD) | 목적 | 비고 |
|------|-----|------|------|------|------|
| root | 1898 | 1 | mysqld_safe | mysql 안전 구동 래퍼 | root 실행 |
| mysql | 2000 | 1898 | mysqld | 실제 DB 구동 | mysql 계정(권한 분리) |
| apache | 24342 | 2142 | httpd | 웹 서비스 | apache 계정 |
| rpc | 1437 | 1 | rpcbind | RPC 포트매퍼 | ⚠️ 불필요 시 중지(U-42) |

> 어떤 **계정(UID)** 으로 어떤 데몬이 구동되는지, **PPID로 부모-자식 관계**가 정상인지 확인 → 권한 오용·불필요 서비스·비정상 프로세스 식별.

### 관련 명령어

```bash
ps -ef                     # 전체 프로세스 (UID/PID/PPID/CMD)
ps -ef | grep <서비스명>    # 특정 서비스 프로세스 필터
ps aux                     # BSD 스타일 (CPU/MEM 사용률 포함)
pstree -p                  # 프로세스 부모-자식 트리 시각화
ps -ef --forest            # 계층(트리) 형태로 출력
kill -9 <PID>              # 프로세스 강제 종료
```

> **`ps -ef` 옵션**: `-e` 모든 프로세스, `-f` 상세 포맷(UID·PPID·STIME 등 전체 필드)

---

## 5. 계정 분석


**명령어**
```bash
cat /etc/passwd | grep bash     # 로그인 셸(bash)이 부여된 계정만 필터
cat /etc/passwd                 # 전체 계정
cat /etc/shadow                 # 암호화된 비밀번호 (root만 열람)
```

**출력 예시 (/etc/passwd)**
```
root:x:0:0:root:/root:/bin/bash
adiosl:x:500:500:adiosl:/home/adiosl:/bin/bash
mysql:x:27:27:MySQL Server:/var/lib/mysql:/bin/bash
cubrid:x:501:501::/home/cubrid:/bin/bash
```

### /etc/passwd 필드 구조 (`:` 구분 7개 필드)

```
  root : x : 0 : 0 : root : /root : /bin/bash
   ①    ②   ③   ④    ⑤      ⑥        ⑦
```

| # | 필드 | 예시 | 의미 / 진단 관점 |
|:-:|------|------|------|
| ① | Username | root | 계정 이름 |
| ② | Password | x | 비밀번호 표시. `x`=shadow 파일에 암호화 저장(정상). 실제 해시가 여기 있으면 취약(U-04) |
| ③ | **UID** | 0 | 사용자 ID. **0 = 최고관리자(root)**. root 외 UID 0 존재 시 취약(U-05) |
| ④ | GID | 0 | 기본 그룹 ID. 존재하지 않는 GID 금지(U-09) |
| ⑤ | Comment | root | 계정 설명(GECOS) |
| ⑥ | Home Directory | /root | 홈 디렉터리 경로. 권한 점검 대상(U-31) |
| ⑦ | Login Shell | /bin/bash | 로그인 셸. 서비스 계정에 셸 부여 시 취약(U-11) |

### UID 체계 (리눅스 기준)

| UID 범위 | 분류 | 설명 |
|---------|------|------|
| **0** | 최고관리자 | root 전용. 중복 금지(U-05) |
| 1 ~ 999 | 시스템/서비스 계정 | 데몬 실행용 (mysql, apache 등). 로그인 불필요 → 셸 제한 |
| **1000 이상** | 일반 사용자 계정 | 실제 로그인 사용자 (CentOS 7+/Ubuntu는 1000부터, 구버전은 500부터) |

> 예시의 `mysql`(UID 27)은 시스템 계정인데 `/bin/bash` 셸이 부여됨 → **U-11 취약** 후보  
> 예시의 `adiosl`(UID 500), `cubrid`(UID 501)는 일반 사용자 계정

### 로그인 셸의 의미

| 셸 | 로그인 | 용도 |
|------|:---:|------|
| `/bin/bash`, `/bin/sh` | 가능 | 로그인 가능 계정 |
| `/sbin/nologin` | 불가 | 로그인 차단(서비스 계정 권장) |
| `/bin/false` | 불가 | 로그인 즉시 종료 |

### 분석 정리 양식

| Username | UID | Home directory | Login Shell | 비고 |
|----------|:---:|----------------|-------------|------|
| root | 0 | /root | /bin/bash | 최고관리자 |
| mysql | 27 | /var/lib/mysql | /bin/bash | 서비스 계정 ⚠️ 셸 제한 필요(U-11) |
| adiosl | 500 | /home/adiosl | /bin/bash | 일반 사용자 |

> 로그인 가능 계정(`/bin/bash`), 서비스 계정의 셸 부여, **UID 0 중복**, 불필요 계정을 식별.

### 관련 명령어

```bash
awk -F: '$3==0 {print $1}' /etc/passwd   # UID 0 계정 전체 출력 (root 외 존재 시 취약)
awk -F: '$3>=1000 {print $1}' /etc/passwd # 일반 사용자 계정 목록
cat /etc/group                            # 그룹 정보 (wheel 그룹 등)
lastlog                                   # 계정별 최종 로그인 기록 (미사용 계정 식별)
```

---

## 6. 분석 총평 작성 항목

환경분석 완료 후 다음 항목을 종합 정리:

- **기본 정보**: OS/DBMS/WEB/WAS 버전 및 EOS(지원 종료) 여부
- **Port 정보**: 불필요하게 열린 포트, 외부(0.0.0.0) 노출 서비스
- **Daemon 정보**: 불필요 서비스, 취약 데몬(rpcbind, telnet 등), 비정상 부모 프로세스
- **계정 정보**: 불필요 계정, UID 0 중복, 서비스 계정의 셸 부여 여부

> 이 총평을 기반으로 U/W 항목별 상세 진단을 진행.
