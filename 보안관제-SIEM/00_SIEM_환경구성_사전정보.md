# 00. SIEM 환경구성 사전정보

> SIEM 실습 환경을 구축하기 전에 알아야 할 네트워크 구성, 각 장비의 역할, IP 체계, 소프트웨어 정보를 정리한 문서.

---

## 1. 가상화 구성도 개요

```
                        out-net                          att-net
  Internet ────── (192.168.190.0/24) ──── Router ──── (10.50.50.0/24) ──── Att-Mint
               (192.168.190.x)          (Vyos)                            (10.50.50.17)
                                    dhcp │ (10.50.50.1)
                                         │
                                   (10.0.0.1)
                                         │
                                       [IPS]
                                         │
                                    rf-net (10.0.0.0/24)
                                         │
                                   (10.0.0.254)
                                         │
            SIEM ──── inner-net ──── Firewall ──── dmz-net ──── Web Service
         (10.0.100.50) (10.0.100.0/24) (pfsense) (10.0.10.0/24)  (Bee-box)
                                   (10.0.100.1) │ (10.0.10.1)   (10.0.10.50)
                                         │
                                   (10.0.50.1)
                                         │
                                    mng-net (10.0.50.0/24)
                                         │
                                      Mng-Mint
                                    (10.0.50.100)
```

### 구성 목적

이 환경은 **실제 기업 보안관제 인프라를 축소 모델링**한 것이다. 공격자(Att-Mint)가 외부에서 웹 서버(Bee-box)를 공격하면, 그 트래픽이 라우터 → IPS → 방화벽을 거치면서 각 보안장비에 로그가 남고, 이 로그를 SIEM(Splunk)이 수집·분석하는 전체 흐름을 체험하는 것이 목적이다.

### 실제 기업 환경과의 대응

| 실습 구성 | 실제 기업 환경 대응 |
|----------|-------------------|
| Vyos 라우터 | ISP 연결 라우터, 경계 라우터 |
| pfsense 방화벽 + Snort IPS | 전용 방화벽(Palo Alto, Fortinet 등) + 전용 IPS(SNIPER 등) |
| Bee-box 웹 서버 | 기업 웹 서비스 서버 (DMZ 구간) |
| Splunk SIEM | 통합보안관제시스템 (SPiDER TM, QRadar 등) |
| Mng-Mint | 관제 요원 워크스테이션 |
| Att-Mint | 외부 공격자 / 모의해킹 테스터 |

---

## 2. 네트워크 구간(Zone) 설계

이 실습 환경은 5개의 가상 네트워크(vSwitch)로 구성된다. 각 네트워크는 실제 기업 환경의 보안 구간(Zone)을 모사한다.

| 가상 네트워크 | 서브넷 | 역할 | 실제 기업 대응 | 보안 수준 |
|-------------|--------|------|-------------|----------|
| **out-net** | 192.168.190.0/24 | 인터넷 구간 (VMware NAT) | 인터넷 / ISP 연결 | Untrust |
| **rf-net** | 10.0.0.0/24 | 라우터 ↔ 방화벽 구간 | 경계 네트워크 (Perimeter) | - |
| **att-net** | 10.50.50.0/24 | 공격자 네트워크 | 외부 위협 (인터넷 측) | Untrust |
| **dmz-net** | 10.0.10.0/24 | DMZ (웹서버 등 대외 서비스) | DMZ 구간 | Semi-Trust |
| **mng-net** | 10.0.50.0/24 | 관리 네트워크 (관제 접속용) | 관리 VLAN / OOB 관리망 | Trust |
| **inner-net** | 10.0.100.0/24 | 내부 네트워크 (SIEM 서버) | 서버팜 / 내부 업무망 | Trust |

### Zone 간 통신 정책 원칙

```
┌──────────────────────────────────────────────────────────┐
│                     방화벽 정책 요약                       │
├────────────────────┬─────────────────────────────────────┤
│ 외부 → DMZ         │ 허용 (HTTP 80/443만)                 │
│ 외부 → 내부/관리    │ 차단 (Any Deny)                     │
│ DMZ → 내부         │ 최소 허용 (DB 포트 등 필요 시만)      │
│ 내부 → DMZ         │ 허용 (관리 목적)                     │
│ 내부 → 외부        │ 정책에 따라 허용                     │
│ 관리 → 전 구간     │ 허용 (관리/모니터링 목적)              │
└────────────────────┴─────────────────────────────────────┘
```

### 왜 이렇게 나누는가?

네트워크를 Zone별로 분리하는 이유는 **침해 확산 방지(Lateral Movement 차단)** 때문이다.

- 공격자가 DMZ의 웹서버를 장악해도, 방화벽 정책에 의해 내부 DB 서버나 SIEM에 직접 접근할 수 없다
- 관리망을 별도로 분리하면, 공격자가 서비스망을 통해 관제 시스템에 접근하는 것을 차단할 수 있다
- 각 Zone별로 방화벽 로그가 남으므로, 비정상 통신을 SIEM에서 탐지할 수 있다

---

## 3. IP 주소 할당표

### 장비별 IP 할당

| 장비 | 역할 | 인터페이스 | IP 주소 | 서브넷 | 게이트웨이 | 소속 네트워크 |
|------|------|-----------|---------|--------|-----------|-------------|
| **Vyos 라우터** | 경계 라우터 | eth0 | DHCP (192.168.190.x) | /24 | VMware NAT | out-net |
| | | eth1 | 10.0.0.1 | /24 | - | rf-net |
| | | eth2 | 10.50.50.1 | /24 | - | att-net |
| **pfsense 방화벽** | 방화벽 + IPS | WAN | 10.0.0.254 | /24 | 10.0.0.1 | rf-net |
| | | DMZ-NET (OPT1) | 10.0.10.1 | /24 | - | dmz-net |
| | | MNG-NET (LAN) | 10.0.50.1 | /24 | - | mng-net |
| | | INNER-NET (OPT2) | 10.0.100.1 | /24 | - | inner-net |
| **Bee-box** | 취약 웹서버 | eth1 | 10.0.10.50 | /24 | 10.0.10.1 | dmz-net |
| **Splunk (SIEM)** | 로그 수집/분석 | ens160 | 10.0.100.50 | /24 | 10.0.100.1 | inner-net |
| **Mng-Mint** | 관리 클라이언트 | ens160 | 10.0.50.100 | /24 | 10.0.50.1 | mng-net |
| **Att-Mint** | 공격자 클라이언트 | ens160 | 10.50.50.17 | /24 | 10.50.50.1 | att-net |

### 주요 서비스 포트

| 서비스 | 포트 | 프로토콜 | 용도 |
|--------|------|---------|------|
| HTTP | 80/TCP | HTTP | Bee-box 웹 서비스 접근 |
| HTTPS | 443/TCP | HTTPS | SSL 웹 서비스 |
| SSH | 22/TCP | SSH | Linux 서버 원격 관리 |
| Syslog | 514/UDP | Syslog | 방화벽/IPS → SIEM 로그 전송 |
| Splunk Web | 8000/TCP | HTTP | Splunk 관리 콘솔 접속 |
| Splunk Mgmt | 8089/TCP | HTTPS | Splunk 관리 API |
| pfsense Web | 80/TCP | HTTP | pfsense 관리 콘솔 (mng-net에서 접속) |
| ICMP | - | ICMP | 네트워크 연결 확인 (ping) |
| SNMP | 161/UDP | SNMP | 장비 상태 모니터링 |
| DNS | 53/UDP,TCP | DNS | 도메인 네임 해석 |

---

## 4. 장비별 상세 정보

### 4-1. Vyos 라우터

| 항목 | 내용 |
|------|------|
| **소프트웨어** | VyOS (Debian 기반 네트워크 OS) |
| **설치 방식** | OVA 파일 임포트 |
| **리소스** | CPU 1 / RAM 512MB / HDD 10GB |
| **어댑터** | 3개 (out-net, rf-net, att-net) |
| **기본 계정** | vyos / vyos |

**역할과 동작 원리**

Vyos는 오픈소스 라우터 OS로, 이 실습에서는 **인터넷과 내부 네트워크를 연결하는 경계 라우터** 역할을 한다.

- **라우팅**: 서로 다른 서브넷(out-net, rf-net, att-net) 간 패킷을 전달
- **NAT**: 내부 사설 IP(10.x.x.x) → 외부 공인 IP(192.168.190.x)로 변환하여 인터넷 접속 가능하게 함
- **정적 라우팅**: 방화벽 하위 네트워크(dmz-net, mng-net, inner-net)에 대한 경로를 수동 설정

**알아야 할 개념: NAT Masquerade**

```
내부 PC (10.0.10.50) ──→ Vyos 라우터 ──→ 인터넷
                    Source IP: 10.0.10.50       Source IP: 192.168.190.x
                    (사설 IP)                    (공인 IP로 변환됨)
```

Masquerade는 PAT(Port Address Translation)의 일종으로, 나가는 인터페이스(eth0)의 IP를 자동으로 사용한다. DHCP로 IP가 바뀌어도 자동 적용되므로 실습 환경에서 편리하다.

**핵심 설정 명령어 구조**

```bash
configure                    # 설정 모드 진입
set interfaces ethernet ...  # 인터페이스 설정
set nat source rule ...      # NAT 설정
set protocols static route ..# 정적 라우팅
commit                       # 설정 적용 (메모리)
save                         # 설정 저장 (디스크)
```

> **주의**: `commit`은 현재 세션에만 적용되고, `save`를 해야 재부팅 후에도 유지된다.

---

### 4-2. pfsense 방화벽

| 항목 | 내용 |
|------|------|
| **소프트웨어** | pfSense (FreeBSD 기반 오픈소스 방화벽) |
| **설치 방식** | ISO 설치 (Auto UFS) |
| **리소스** | CPU 1 / RAM 1GB / HDD 20GB (씬 프로비저닝) |
| **어댑터** | 4개 (rf-net, dmz-net, mng-net, inner-net) |
| **기본 계정** | admin / pfsense → 변경: qwer12#$ |
| **관리 접속** | http://10.0.50.1 (Mng-Mint에서 접속) |

**역할과 동작 원리**

pfSense는 이 실습에서 **핵심 보안 장비**로, 모든 Zone 간 트래픽을 제어하는 관문이다.

```
역할 1: 접근 제어 (ACL)
  → 어떤 IP/포트의 트래픽을 허용/차단할지 정책으로 결정

역할 2: NAT / 포트포워딩
  → 외부에서 Bee-box 웹 서버에 접근할 수 있도록 포트포워딩 설정

역할 3: IPS (Snort 패키지)
  → 방화벽에 Snort를 설치하여 침입탐지/차단 기능 추가

역할 4: 로그 생성
  → 모든 허용/차단 이벤트를 Syslog로 SIEM에 전송
```

**인터페이스 구성 이해**

pfSense에서 각 인터페이스는 하나의 보안 Zone을 대표한다:

| pfSense 인터페이스 | 물리 매핑 | 보안 Zone | Trust Level |
|-------------------|----------|----------|-------------|
| WAN (vmx0) | rf-net | 외부 (Untrust) | 낮음 |
| LAN → MNG-NET (vmx2) | mng-net | 관리 (Trust) | 높음 |
| OPT1 → DMZ-NET (vmx1) | dmz-net | DMZ (Semi-Trust) | 중간 |
| OPT2 → INNER-NET (vmx3) | inner-net | 내부 (Trust) | 높음 |

**방화벽 정책 기본 원칙**

pfSense는 기본적으로 **WAN 인바운드 트래픽을 모두 차단**한다 (Default Deny). 따라서:

1. 외부에서 Bee-box 웹 서버에 접근하려면 → **포트포워딩** + **WAN 방화벽 룰** 필요
2. 각 Zone 간 통신이 필요하면 → 해당 인터페이스에 **명시적 허용 룰** 추가 필요
3. LAN(MNG-NET)은 기본적으로 모든 아웃바운드가 허용됨 (관리 편의)

**포트포워딩 동작 흐름**

```
① 공격자 (10.50.50.17) → Vyos → pfsense WAN (10.0.0.254:80)
② pfsense가 목적지를 변환: 10.0.0.254:80 → 10.0.10.50:80
③ 패킷이 DMZ의 Bee-box (10.0.10.50:80)에 도달
④ 응답 패킷은 역순으로 NAT 되어 공격자에게 전달
```

---

### 4-3. Snort IPS (pfsense 내장)

| 항목 | 내용 |
|------|------|
| **소프트웨어** | Snort 3.x (pfSense 패키지) |
| **설치 방식** | pfSense Package Manager에서 설치 |
| **적용 인터페이스** | WAN (vmx0) |
| **룰셋** | Snort GPLv2 + Emerging Threats Open |
| **룰 업데이트** | 1일 1회 (04:00) |

**Snort의 동작 원리**

Snort는 네트워크 트래픽을 실시간으로 검사하여 알려진 공격 패턴(Signature)과 매칭되는 트래픽을 탐지/차단한다.

```
패킷 수신 → 프로토콜 디코딩 → 전처리기(Preprocessor) → 탐지 엔진(Signature 매칭) → 경보/차단
```

**룰셋 종류**

| 룰셋 | 설명 | 라이선스 |
|------|------|---------|
| **Snort GPLv2** | Snort 커뮤니티 룰. 기본 공격 패턴 포함 | 무료 |
| **Emerging Threats Open** | 커뮤니티 기반 최신 위협 룰 | 무료 |
| **Snort Subscriber (VRT)** | Cisco Talos가 관리하는 프리미엄 룰 | 유료 (30일 지연 무료) |
| **ET Pro** | Proofpoint가 관리하는 프리미엄 위협 룰 | 유료 |

**로그 전송 설정**

Snort에서 탐지된 경보(Alert)를 SIEM으로 보내려면 **Syslog 전송**을 활성화해야 한다:

```
Snort Alert → pfSense System Log (LOG_USER) → Syslog (UDP 514) → Splunk SIEM
```

---

### 4-4. Bee-box (취약 웹 서버)

| 항목 | 내용 |
|------|------|
| **소프트웨어** | bWAPP (buggy Web Application) on Ubuntu |
| **설치 방식** | OVF/VMDK 임포트 |
| **리소스** | 기본 설정 유지 |
| **기본 계정** | bee / bug |
| **웹 접속** | http://10.0.10.50/bWAPP/ |

**bWAPP이란?**

bWAPP(buggy Web Application)은 **의도적으로 취약하게 만든 웹 애플리케이션**이다. OWASP Top 10을 포함한 100개 이상의 웹 취약점을 실습할 수 있도록 설계되었다.

**실습 가능한 주요 취약점**

| 카테고리 | 취약점 예시 | OWASP 분류 |
|---------|-----------|-----------|
| Injection | SQL Injection (GET/POST), Blind SQLi, OS Command Injection | A03:2021 |
| XSS | Reflected XSS, Stored XSS, DOM-based XSS | A03:2021 |
| 인증 우회 | Broken Authentication, Session Management | A07:2021 |
| 파일 업로드 | Unrestricted File Upload (웹셸) | A01:2021 |
| 디렉토리 트래버설 | Directory Traversal, File Inclusion (LFI/RFI) | A01:2021 |
| CSRF | Cross-Site Request Forgery | A01:2021 |
| SSRF | Server-Side Request Forgery | A10:2021 |

**왜 DMZ에 배치하는가?**

실제 기업에서도 웹 서버는 DMZ에 위치한다. 외부에서 접근이 필요하지만, 내부망(DB 서버 등)과는 방화벽으로 분리하여 웹 서버가 침해되더라도 내부로의 확산을 차단한다.

---

### 4-5. Splunk (SIEM)

| 항목 | 내용 |
|------|------|
| **소프트웨어** | Splunk Enterprise 8.2.0 |
| **설치 방식** | Ubuntu에 DEB 패키지 설치 |
| **리소스** | CPU 1 / RAM 1GB / HDD 50GB (씬) |
| **기본 계정** | kisia01 / qwer12#$ |
| **웹 접속** | http://10.0.100.50:8000 |
| **라이선스** | 엔터프라이즈 평가판 (60일) |

**Splunk이란?**

Splunk은 **머신 데이터(로그, 이벤트, 메트릭)를 수집·인덱싱·검색·시각화**하는 빅데이터 분석 플랫폼이다. 보안 분야에서는 SIEM으로 널리 사용된다.

**Splunk 핵심 개념**

| 개념 | 설명 |
|------|------|
| **Index** | 로그 데이터를 저장하는 저장소. 장비/용도별로 분리 (예: `pfsense`, `snort`) |
| **Source Type** | 로그의 형식을 정의 (예: `syslog`, `csv`, `json`). 파싱 규칙 결정 |
| **SPL (Search Processing Language)** | Splunk 전용 검색 언어. SQL과 유사한 파이프라인 구조 |
| **App** | 대시보드, 검색, 리포트를 묶은 패키지 (예: Splunk for Security) |
| **Forwarder** | 원격 장비에서 로그를 수집하여 Splunk 서버로 전달하는 경량 에이전트 |

**기본 SPL 검색 예시**

```spl
# 전체 로그 검색
index=*

# pfsense 방화벽 로그 검색
index=pfsense

# 특정 IP에서 발생한 이벤트
index=pfsense src_ip=10.50.50.17

# 최근 1시간 내 차단된 이벤트
index=pfsense action=blocked earliest=-1h

# 목적지 포트 80번 이벤트 통계
index=pfsense dst_port=80 | stats count by src_ip

# 시간대별 이벤트 추이
index=pfsense | timechart count by action
```

**로그 수집 구조**

```
┌─────────────────────────────┐
│        Splunk SIEM          │
│      (10.0.100.50)          │
│                             │
│  ┌─────────┐ ┌───────────┐ │
│  │ Index:   │ │ Index:    │ │
│  │ pfsense  │ │ snort     │ │
│  └────┬─────┘ └─────┬────┘ │
│       │              │      │
└───────┼──────────────┼──────┘
        │              │
   UDP 514        UDP 514
   (Syslog)       (Syslog)
        │              │
   ┌────┴────┐    ┌────┴────┐
   │ pfsense │    │  Snort  │
   │ 방화벽   │    │  IPS    │
   │ 로그     │    │  Alert  │
   └─────────┘    └─────────┘
```

**왜 inner-net(내부망)에 배치하는가?**

SIEM은 모든 보안 로그를 수집·저장하는 핵심 시스템이다. 공격자가 SIEM에 접근하면 로그를 삭제하거나 탐지 룰을 무력화할 수 있으므로, **가장 보호 수준이 높은 내부망에 배치**한다.

---

### 4-6. Mng-Mint (관리 클라이언트)

| 항목 | 내용 |
|------|------|
| **소프트웨어** | Linux Mint |
| **설치 방식** | ISO 설치 |
| **리소스** | CPU 1 / RAM 1GB / HDD 16GB |
| **기본 계정** | 설치 시 설정 |
| **네트워크** | mng-net (10.0.50.100) |

**역할**

관제 요원이 사용하는 워크스테이션이다. 이 PC에서:

- pfSense 웹 콘솔(http://10.0.50.1)에 접속하여 방화벽/IPS 관리
- Splunk 웹 콘솔(http://10.0.100.50:8000)에 접속하여 로그 분석
- SSH로 각 서버에 원격 접속하여 관리

**왜 별도 관리망(mng-net)에 배치하는가?**

관리 트래픽과 서비스 트래픽을 분리하면:
- 서비스 장애가 관리 접속에 영향을 주지 않음
- 공격자가 서비스망을 통해 관리 콘솔에 접근하는 경로가 차단됨
- 관리 접속 로그를 별도로 모니터링하여 비인가 접근 탐지 가능

---

### 4-7. Att-Mint (공격자 클라이언트)

| 항목 | 내용 |
|------|------|
| **소프트웨어** | Linux Mint (Mng-Mint 복제) |
| **리소스** | CPU 1 / RAM 1GB / HDD 16GB |
| **네트워크** | att-net (10.50.50.17) |

**역할**

외부 공격자를 시뮬레이션하는 클라이언트이다. 이 PC에서:

- Bee-box 웹 서버에 대한 SQL Injection, XSS 등 웹 공격 수행
- 네트워크 스캔 (Nmap 등)
- DDoS 공격 시뮬레이션
- 공격 트래픽이 보안장비에서 탐지되는지 확인

**공격 시 트래픽 경로**

```
Att-Mint (10.50.50.17)
    │
    ▼
Vyos 라우터 (10.50.50.1 → 10.0.0.1)
    │
    ▼ ← IPS(Snort)가 여기서 트래픽 검사 → Alert 발생 → SIEM 전송
    │
pfsense 방화벽 (10.0.0.254)
    │ ← 방화벽 로그 발생 → SIEM 전송
    │ ← 포트포워딩: WAN:80 → 10.0.10.50:80
    ▼
Bee-box 웹 서버 (10.0.10.50)
    │
    ▼
웹 애플리케이션에서 공격 처리 (취약점 동작)
```

---

## 5. 가상화 플랫폼 사전 지식

### 5-1. VMware 구성

| 항목 | 내용 |
|------|------|
| **호스트** | VMware Workstation 17.6.0 (Windows PC에 설치) |
| **게스트 하이퍼바이저** | VMware ESXi 6.7.0 (Workstation 위에 Nested VM으로 구동) |
| **리소스** | ESXi에 CPU 8 / RAM 8GB / HDD 110GB 할당 |

### Nested Virtualization (중첩 가상화) 구조

```
┌─────────────────────────────────────────┐
│ Windows PC (물리 머신)                    │
│                                          │
│  ┌─────────────────────────────────────┐ │
│  │ VMware Workstation                  │ │
│  │                                     │ │
│  │  ┌─────────────────────────────┐    │ │
│  │  │ VMware ESXi 6.7.0          │    │ │
│  │  │                             │    │ │
│  │  │  ┌────┐ ┌────┐ ┌────┐     │    │ │
│  │  │  │Vyos│ │pfS │ │Bee │ ... │    │ │
│  │  │  │    │ │ense│ │box │     │    │ │
│  │  │  └────┘ └────┘ └────┘     │    │ │
│  │  └─────────────────────────────┘    │ │
│  └─────────────────────────────────────┘ │
└─────────────────────────────────────────┘
```

**왜 ESXi를 중간에 넣는가?**

- 실제 기업 환경에서 보안 장비들은 ESXi/vSphere 위에서 운영되는 경우가 많다
- ESXi의 가상 스위치(vSwitch) 기능을 활용하여 네트워크 Zone 분리를 실습할 수 있다
- 기업 인프라 운영 경험을 쌓을 수 있다

### 5-2. 가상 스위치 (vSwitch) 생성 목록

ESXi 내부에서 아래 5개의 가상 스위치를 생성하여 네트워크를 분리한다:

| vSwitch 이름 | 연결 대상 | 설명 |
|-------------|----------|------|
| att-net | Vyos eth2, Att-Mint | 공격자 네트워크 |
| rf-net | Vyos eth1, pfsense WAN | 라우터-방화벽 연결 |
| dmz-net | pfsense OPT1, Bee-box | DMZ 구간 |
| mng-net | pfsense LAN, Mng-Mint | 관리 네트워크 |
| inner-net | pfsense OPT2, Splunk | 내부 네트워크 |

---

## 6. 트래픽 흐름과 로그 수집 시나리오

### 시나리오: 공격자가 SQL Injection 공격 시

```
1단계: 공격 시도
━━━━━━━━━━━━━━
Att-Mint → HTTP GET "http://10.0.0.254/bWAPP/sqli_1.php?title=' OR 1=1--"

2단계: 라우터 통과
━━━━━━━━━━━━━━━━
Vyos 라우터: 10.50.50.17 → 10.0.0.254 로 패킷 라우팅
(라우터에서는 별도 보안 로그 없음)

3단계: IPS(Snort) 탐지
━━━━━━━━━━━━━━━━━━━━
Snort가 HTTP 페이로드에서 "' OR 1=1--" 패턴 매칭
→ Alert 발생: [1:1000001:1] SQL Injection Attempt
→ Syslog로 Splunk에 전송

4단계: 방화벽 통과
━━━━━━━━━━━━━━━━
pfsense가 WAN → DMZ 포트포워딩 룰에 따라 트래픽 전달
→ 방화벽 로그 생성 (src: 10.50.50.17, dst: 10.0.10.50, port: 80, action: pass)
→ Syslog로 Splunk에 전송

5단계: 웹 서버 도달
━━━━━━━━━━━━━━━━
Bee-box (10.0.10.50)의 bWAPP 애플리케이션이 취약한 SQL 쿼리 실행
→ DB에서 데이터 유출

6단계: SIEM 분석
━━━━━━━━━━━━━━
Splunk에서 관제 요원이 확인:
- Snort Alert: SQL Injection 탐지 이벤트
- 방화벽 로그: 공격자 IP의 접근 기록
- 상관분석: 동일 IP에서 다수의 웹 공격 시도 탐지

7단계: 대응
━━━━━━━━━
관제 요원이 pfsense 방화벽에서 공격자 IP (10.50.50.17) 차단 룰 추가
→ 이후 공격 트래픽은 방화벽에서 Drop
```

---

## 7. 사전 확인 체크리스트

### 호스트 PC 요구사항

| 항목 | 최소 사양 | 권장 사양 |
|------|----------|----------|
| CPU | 4코어 (VT-x/AMD-V 지원 필수) | 8코어 이상 |
| RAM | 12GB | 16GB 이상 |
| 디스크 | 150GB 여유 공간 | SSD 200GB 이상 |
| OS | Windows 10/11 Pro 64bit | Windows 11 Pro |
| 네트워크 | 인터넷 연결 필요 | 유선 LAN 권장 |

> **VT-x/AMD-V 활성화 확인**: BIOS에서 Intel VT-x 또는 AMD-V가 활성화되어 있어야 ESXi 내부에서 VM을 구동할 수 있다.

### 필요 파일 목록

| 파일 | 용도 | 크기(대략) |
|------|------|----------|
| VMware-workstation-17.6.0.exe | 호스트 하이퍼바이저 | ~600MB |
| VMware-VMvisor-Installer-6.7.0.iso | ESXi 설치 | ~350MB |
| vyos-*.ova | Vyos 라우터 | ~300MB |
| pfSense-CE-*.iso | 방화벽 설치 | ~800MB |
| bee-box-v1.6.ova / .vmdk | 취약 웹서버 | ~1.5GB |
| linuxmint-*.iso | 클라이언트 (Mng, Att) | ~2.5GB |
| splunk-8.2.0-*.deb | SIEM 서버 | ~500MB |
| ubuntu-*-server.iso | Splunk 서버 OS | ~1GB |

### 네트워크 연결 검증 순서

환경 구성 완료 후 아래 순서로 ping 테스트를 수행하여 연결 상태를 확인한다:

```
1. Vyos에서 인터넷 확인
   vyos$ ping 8.8.8.8              ✓ 인터넷 연결

2. pfsense에서 라우터 확인
   pfsense → Diagnostics > Ping
   대상: 10.0.0.1                   ✓ rf-net 연결

3. Mng-Mint에서 게이트웨이 확인
   $ ping 10.0.50.1                ✓ mng-net → pfsense
   $ ping 10.0.0.1                 ✓ pfsense → Vyos 라우터
   $ ping 8.8.8.8                  ✓ 인터넷 연결

4. Bee-box에서 게이트웨이 확인
   $ ping 10.0.10.1                ✓ dmz-net → pfsense

5. Splunk에서 게이트웨이 확인
   $ ping 10.0.100.1               ✓ inner-net → pfsense

6. Att-Mint에서 웹 서버 접근 확인
   $ curl http://10.0.0.254        ✓ 포트포워딩 → Bee-box

7. Splunk 로그 수집 확인
   Splunk Web → index=pfsense     ✓ Syslog 수집 정상
```

---

## 8. 자주 발생하는 문제와 해결

| 증상 | 원인 | 해결 방법 |
|------|------|----------|
| ESXi 내부 VM이 부팅 안 됨 | VT-x 중첩 가상화 미활성 | Workstation VM 설정 → Processors → "Virtualize Intel VT-x/EPT" 체크 |
| Mng-Mint에서 인터넷 안 됨 | Vyos NAT 설정 누락 | Vyos에서 `set nat source rule 100` 확인 |
| pfsense 웹 콘솔 접속 불가 | LAN 인터페이스 IP 미설정 | pfsense 콘솔에서 Option 2 → LAN IP 설정 |
| Bee-box에 외부 접근 불가 | 포트포워딩 미설정 | pfsense → Firewall → NAT → Port Forward 추가 |
| Splunk에 로그 안 들어옴 | Syslog 포트 미오픈 / 방화벽 차단 | Splunk UDP 514 설정 확인, pfsense → INNER-NET 룰 확인 |
| Snort Alert가 SIEM에 안 보임 | Snort Syslog 전송 미설정 | Snort → Alert Settings → "Send to system log" 체크 |
| ping은 되는데 웹 접속 불가 | 방화벽에서 HTTP만 차단 | pfsense 해당 인터페이스 룰에서 TCP 80 허용 추가 |
| Vyos 설정이 재부팅 후 초기화 | `save` 명령 미실행 | `commit` 후 반드시 `save` 실행 |

---

## 9. 핵심 용어 정리

| 용어 | 설명 |
|------|------|
| **vSwitch** | 가상 스위치. 하이퍼바이저 내부에서 VM 간 네트워크를 연결하는 소프트웨어 스위치 |
| **NAT** | Network Address Translation. 사설 IP ↔ 공인 IP 주소 변환 |
| **포트포워딩** | 외부에서 특정 포트로 들어온 트래픽을 내부의 다른 IP:포트로 전달하는 기술 |
| **Syslog** | 시스템 로그를 네트워크를 통해 전송하는 표준 프로토콜 (UDP 514) |
| **DMZ** | DeMilitarized Zone. 외부와 내부 사이의 완충 구간으로, 대외 서비스 서버를 배치 |
| **ACL** | Access Control List. 트래픽 허용/차단 규칙 목록 |
| **Signature** | 알려진 공격 패턴을 정의한 규칙. IPS/IDS가 이를 기반으로 탐지 |
| **Index** | Splunk에서 로그 데이터를 저장하는 논리적 저장소 |
| **SPL** | Search Processing Language. Splunk의 검색/분석 쿼리 언어 |
| **Nested Virtualization** | VM 안에서 또 다른 VM을 실행하는 중첩 가상화 기술 |
| **Thin Provisioning** | 디스크 공간을 실제 사용량만큼만 할당하는 방식 (vs Thick: 전체 사전 할당) |
| **OVA/OVF** | Open Virtual Appliance/Format. 가상 머신을 배포하기 위한 표준 패키지 형식 |
| **Masquerade** | NAT의 일종으로, 나가는 인터페이스의 IP를 자동으로 출발지 IP로 사용 |
