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
