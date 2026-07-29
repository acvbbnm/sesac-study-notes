# 보안관제 & SIEM 실무 정리

> 강의교재 1~3 (2026.07) 기반 정리  
> SeSAC AI 보안전문가 양성과정 SW 5기

---

## 목차

1. [보안관제 & SOC](#1-보안관제--soc)
2. [네트워크의 이해](#2-네트워크의-이해)
3. [방화벽의 이해](#3-방화벽의-이해)
4. [IDS / IPS 이해](#4-ids--ips-이해)
5. [웹방화벽(WAF) 이해](#5-웹방화벽waf-이해)
6. [이벤트 대응 및 분석](#6-이벤트-대응-및-분석)
7. [통합보안관제시스템 (ESM → SIEM)](#7-통합보안관제시스템-esm--siem)
8. [SIEM 운영](#8-siem-운영)
9. [SIEM 환경 구성 실습](#9-siem-환경-구성-실습)
10. [네트워크 구성도 샘플](#10-네트워크-구성도-샘플)

---

## 1. 보안관제 & SOC

### 보안관제란

보안관제(MSS, Managed Security Service)는 이기종 보안장비에서 탐지되는 보안 이벤트를 수집·분석하고 사이버 침해에 대해 **탐지 → 차단 → 대응**하는 업무다.

### 보안관제 종류

| 종류 | 장점 | 단점 |
|------|------|------|
| 자체관제 | 환경 파악 용이, 빠른 대응 | 전문성 부족, 인력 수급 문제 |
| 파견관제 | 원활한 의사소통, 사이트 특화 | 인력 관리 부담, 단가 높음 |
| 파견+원격 | 두 방식 장점 융합 | 서비스 품질 편차 |
| 원격관제 | 저비용, 인력 관리 불필요 | 침해 시 즉각 조치 어려움 |

### 보안관제 구성요소 (3P)

- **People** : 역할별 숙련 인력
- **Process** : 절차·위기대응 매뉴얼·유관부서 역할 정의
- **System** : 모니터링 툴, 침해사고대응관리시스템

### SOC (Security Operation Center)

중앙 집중화된 환경에서 사람·프로세스·기술을 활용하여 사이버위협을 식별·예방·탐지·대응·복구하는 조직.

업무 사이클: `식별(Identify) → 예방(Protect) → 탐지(Detect) → 대응(Respond) → 복구(Recovery)`

---

## 2. 네트워크의 이해

### OSI 7계층과 보안장비

| 계층 | 이름 | 보안장비 |
|------|------|---------|
| 7 | Application | IPS, WAF |
| 4 | Transport | IDS, 방화벽(TCP/UDP 차단) |
| 3 | Network | 방화벽(IP 차단) |

### 네트워크 구성 방식

**In-line 모드**: 모든 트래픽이 장비 통과. 탐지+차단 가능. Fail-Over 필수.

**Sniffing 모드**: 미러링으로 트래픽 복사 분석. 탐지만 가능, 차단 불가. IDS에서 사용.

**Out of Path 모드**: 회선 바깥에 탐지+차단 장비 분리. DDoS 대응, ISP급 망에서 활용.

**HA 구성**
- Active-Active: Load Balancing + Fail-Over
- Active-Standby: 평소 Active, 장애 시 Standby 전환

### Zone 개념

| Zone | 설명 |
|------|------|
| 인터넷 구간 | 개인정보처리시스템과 인터넷 직접 연결 |
| DMZ | 외부와 내부 사이 중간 영역. 외부에서 접근 가능하나 내부망 보호 |
| 내부망 | 물리적 망분리·접근통제로 외부 직접 접근 차단 |

---

## 3. 방화벽의 이해

### 정의

네트워크 출입로를 단일화하여 ACL(접근제어 목록)으로 패킷을 허용/차단하는 시스템.

### 보안정책 4종

| 정책 | 설명 |
|------|------|
| Paranoid | All Block |
| Prudent | Any Open, 나머지 Drop |
| Cautious | Any Block, 나머지 Allow |
| Promiscuous | All Open |

### NAT 종류

| 종류 | 방향 | 설명 |
|------|------|------|
| PAT (N:1) | 내→외 | 다수 사설IP → 공인IP 하나 (일반 인터넷 접속) |
| DIP (N:N) | 내→외 | 특정 사설IP 대역 → 특정 공인IP (IP 인증 필요 서비스) |
| VIP (1:N) | 외→내 | 공인IP 하나를 포트로 내부 서버 분산 |
| MIP (1:1) | 외→내 | 공인IP 1개 ↔ 내부 서버 1개 |

### 방화벽 운영 모드

| 모드 | 특징 |
|------|------|
| Transparent (L2) | Bridge 구성. Manage IP만 할당 |
| NAT Mode (L3) | 사설IP → 공인IP 변환. Routing Table 필요 |
| Route Mode (L3) | 하단도 공인IP 사용. NAT 불필요 |

### 방화벽 로그 필드

```
machine_name | fw_rule_id | nat_rule_id | src_ip | src_port
dst_ip | dst_port | protocol | ingress_if | tx_packets | rx_packets | duration
```

---

## 4. IDS / IPS 이해

### IDS vs IPS

| 항목 | IDS | IPS |
|------|-----|-----|
| 목적 | 침입 탐지 | 침입 방지 |
| 구성 방식 | Out of Path (Sniffing) | In-line |
| 대응 | 사후 분석, 관리자 알림 | 실시간 차단 |
| 단점 | 차단 불가 | 오탐 시 정상 트래픽 차단 위험 |

### IDS 탐지 방식

| 방식 | 원리 | 장점 | 단점 |
|------|------|------|------|
| 지식기반(오용탐지) | Signature 패턴 매칭 | 오탐률 낮음 | 신규 공격 탐지 불가 |
| 행위기반(비정상탐지) | 급격한 변화 탐지 | 알려지지 않은 공격 탐지 | 오탐률 높음 |

### IPS 로그 예시

```
[Victim=125.209.210.92],[Protocol=tcp/80],[Risk=High],[Handling=Alarm],[SrcPort=57231],[HackType=00004]
```

---

## 5. 웹방화벽(WAF) 이해

HTTP/HTTPS 트래픽 감시로 웹 어플리케이션 공격을 서버 도달 전에 차단.

**구성**: `라우터 → 방화벽 → 웹방화벽 → 웹서버`

**주요 기능**
- 탐지 로그: 탐지 룰·출발지·국가·URL·시각 제공
- RawData: Decoding 후 정탐/오탐 판단
- 감사 로그: 로그인·설정 변경·네트워크 인터페이스 이력
- 정책 설정: 웹서버 추가, SSL 인증서 등록, Inline/Proxy 모드

---

## 6. 이벤트 대응 및 분석

### 이벤트 대응 프로세스

```
① 보안장비 로그 수집 (SIEM 연동)
② 이벤트 탐지 (연관성 분석 룰 경보 → 메일 발송)
③ 1차 분석 (정탐/오탐 판단, 유효성 테스트)
④ 공격자 IP 차단 + 탐지 보고서 작성
   (공격자IP / 대상IP / Port / 이벤트명 / 상세데이터 / 공격설명 / 조치방안)
⑤ 담당자 통보 (메일 / SMS / 유선)
⑥ 침해사고 조치 지원 (CERT, 피해서버 2차 분석)
```

### 주요 공격 유형 & 대응

**SQL Injection**  
웹 파라미터에 SQL 삽입 → DB 데이터 유출·변조, 인증 우회.

**Webshell**  
파일 업로드 취약점 → 웹서버에 쉘 업로드 → 서버 명령 실행.  
대응: 허용 확장자만 업로드, Directory Listing 제거.

**Command Injection**  
시스템 명령어 호출 함수의 인자값 조작 → OS 명령 실행. (대표: Bash ShellShock)  
대응: 파이프라인(`|`), `open()` 등으로 사용자 입력 전달 금지.

**XSS (Cross Site Scripting)**  
악성 스크립트 게시판 삽입 → 사용자 쿠키 탈취.  
대응: 특수문자 필터링(`<`,`>`,`&`), 세션 인증 전환, HTML White List.

### 정탐/오탐 확인

- **SIEM (F/W)**: Brute Force, IP Scanning 등 연관성 분석으로 확인
- **IPS/IDS RawData**: Base64 Decoding 후 패턴 분석  
- **WAF**: 상세보기에서 자동 Decoding된 탐지 데이터 확인

---

## 7. 통합보안관제시스템 (ESM → SIEM)

### 보안관제 세대 진화

| 세대 | 시스템 | 특징 |
|------|--------|------|
| 1세대 | 단위 보안장비 | 개별 장비 독립 운영 |
| 2세대 | ESM | 로그/이벤트 통합 저장, 경보 모니터링 |
| 3세대 | SIEM | 빅데이터 기반, Threat Intelligence 연동, 실시간+과거 분석 |

---

## 8. SIEM 운영

### SIEM 구성요소

| 구성 | 역할 |
|------|------|
| Manager | 알람 처리(Email/SMS/SNMP), DB 백업/삭제 스케줄링 |
| Console | 사용자 관리, 연관성 분석 설정, 경보 설정 화면 |
| Agent | 장비 로그 수집·정규화·축약 후 Manager 전송 |

### 이벤트 검색

```
SIEM → 보안관제 탭 → 통합 로그 검색
→ 로그유형 선택 (FW / IPS / WebFW)
→ Query: 시간 / 출발지IP / 목적지IP / Port / Method
```

### 경보 종류

| 종류 | 설명 |
|------|------|
| 번들룰 | 핑 체크, 프로세스 체크, 미수집 체크 (가용성 모니터링) |
| 단일경보 | 특정 Object 조건 충족 시 경보. 제외 IP로 오탐 감소 |
| 상관분석 | 단일경보 조합으로 다단계 탐지 (이기종 장비 연계) |

**상관분석 예시**
```
Step 1: 방화벽 포트 스캔 탐지 (정보수집 단계)
Step 2: IPS/WAF 시그니처 탐지 (침투 시도 단계)
```

---

## 9. SIEM 환경 구성 실습

### 가상화 구성도

```
인터넷 (192.168.190.0/24)
        │
   Vyos 라우터
   eth0: DHCP (외부)
   eth1: 10.0.0.1  (rf-net)
   eth2: 10.50.50.1 (att-net)
        │
   rf-net (10.0.0.0/24)
        │
   pfsense 방화벽/IPS
   WAN:  10.0.0.254
   ├── dmz-net   10.0.10.0/24  → Bee-box (10.0.10.50)
   ├── mng-net   10.0.50.0/24  → Mng-Mint (10.0.50.100)
   └── inner-net 10.0.100.0/24 → Splunk SIEM (10.0.100.50)

att-net (10.50.50.0/24) → Att-Mint 공격자 (10.50.50.17)
```

### 구성 요소 요약

| 구성요소 | 버전 | 역할 | 인증정보 |
|---------|------|------|---------|
| VMware Workstation | 17.6.0 | 호스트 하이퍼바이저 | Key: MC60H-DWHD5-H80U9-6V85M-8280D |
| VMware ESXi | 6.7.0 | 가상화 플랫폼 | - |
| Vyos | - | 라우터 | - |
| pfsense | - | 방화벽 + IPS(Snort) | admin / pfsense → qwer12#$ |
| Bee-box | - | 취약 웹서버 (공격 대상) | bee / bug |
| Splunk | 8.2.0 | SIEM (포트 8000) | kisia01 / qwer12#$ |
| MobaXterm | - | SSH 클라이언트 | - |

### Vyos 핵심 설정

```bash
# 인터페이스
set interfaces ethernet eth0 address dhcp
set interfaces ethernet eth1 address '10.0.0.1/24'
set interfaces ethernet eth2 address '10.50.50.1/24'

# NAT (사설 → 공인)
set nat source rule 100 outbound-interface 'eth0'
set nat source rule 100 source address '10.0.0.0/8'
set nat source rule 100 translation address masquerade

# 정적 라우팅
set protocols static route 10.0.10.0/24 next-hop 10.0.0.1
set protocols static route 10.0.50.0/24 next-hop 10.0.0.1
set protocols static route 10.0.100.0/24 next-hop 10.0.0.1
set system gateway-address 192.168.190.2
set system name-server 8.8.8.8
commit && save
```

### pfsense IPS (Snort) 구축

```
1. System > Package Manager > snort 설치
2. Services > Snort > Interfaces > WAN 추가
3. Global Settings > ET Open 룰 활성화, 업데이트 1일
4. Updates > Update Rules
5. WAN Categories > Select All > Save
6. snort running 버튼 클릭
```

### Splunk 로그 수집 설정

```bash
# Splunk 설치 및 시작
sudo dpkg -i splunk-8.2.0-...-linux-2.6-amd64.deb
sudo /opt/splunk/bin/splunk enable boot-start
sudo /etc/init.d/splunk start
# 웹 접속: http://10.0.100.50:8000

# 방화벽 syslog 수신 (Splunk)
설정 > 데이터 입력 > UDP > 포트 514
source type: syslog, index: pfsense

# pfsense → Splunk syslog 전송
Status > System Logs > Settings
Remote log servers: 10.0.100.50
Remote Syslog Contents: Everything

# pfsense 방화벽 로그 활성화
Firewall > Rules > 해당 룰 Edit
Extra Options > "Log packets that are handled by this rule" 체크

# IPS(Snort) 로그를 syslog로 전송
Services > Snort > Interfaces > Edit > Alert Settings
"Snort will send Alerts to the firewall's system log" 체크
System Log Facility: LOG_USER
```

### Mng-Mint 네트워크 설정

```yaml
# /etc/netplan/1-network-manager-all.yaml
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    ens160:
      addresses: [10.0.50.100/24]
      gateway4: 10.0.50.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```

```bash
sudo netplan apply
```

---

## 10. 네트워크 구성도 샘플

```
         L3 Router
              │
             L4
              │
        BB Switch (L2)
     ┌────────┼────────┐
   was#1   was#2,#3  was#4
```

3계층 구성: 라우터(L3) → 로드밸런서(L4) → 백본스위치(L2) → WAS 서버 팜
