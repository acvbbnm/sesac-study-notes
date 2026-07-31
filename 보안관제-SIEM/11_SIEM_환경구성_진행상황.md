# 11. SIEM 환경구성 진행상황

> 최종 업데이트: 2026-07-31

---

## 현재 진행 상태

| 단계 | 작업 | 상태 |
|------|------|------|
| 1 | VMware Workstation 17.6.0 설치 | ✅ 완료 |
| 2 | VMware ESXi 6.7.0 설치 (Nested VM) | ✅ 완료 |
| 3 | ESXi 가상 스위치 5개 생성 | ✅ 완료 |
| 4 | Vyos 라우터 설치 및 설정 | ✅ 완료 |
| 5 | pfsense 방화벽 설치 및 IP 설정 | ✅ 완료 |
| 6 | Mng-Mint 네트워크 설정 | ✅ 완료 (10.0.50.100/24) |
| 7 | pfsense 웹 콘솔 접속 | ✅ 완료 (HTTP 포트80, Mng-Mint에서 접속 확인) |
| 8 | Bee-box 웹서버 설치 | ✅ 완료 (OVF 등록, IP 설정 완료) |
| 9 | Ubuntu + Splunk SIEM 설치 | ✅ 완료 (inner-net 전환 완료, 10.0.100.50/24) |
| 10 | pfsense 방화벽 룰 설정 | ✅ 완료 (WAN NAT룰, DMZNET/INNERNET deny all) |
| 11 | Mng-Mint → Ubuntu SSH 연결 | ✅ 완료 (pfSense 경유 mng-net↔inner-net 통신) |
| 12 | pfsense IPS (Snort) 구축 | ✅ 완료 (GPLv2+ET Open, WAN 인터페이스, 룰 적용) |
| 13 | Att-Mint 공격자 클라이언트 설정 | ✅ 완료 (mng-mint 복제, att-net, 10.50.50.17/24) |
| 14 | Splunk 로그 수집 설정 (방화벽/IPS) | ✅ 완료 (UDP 514, index=pfsense, 483 events 확인) |

---

## 완료된 설정 상세

### ESXi 호스트 정보

| 항목 | 값 |
|------|-----|
| 버전 | VMware ESXi 6.7.0 (Build 14320388) |
| CPU | 4 x 12th Gen Intel Core i7-12700 |
| RAM | 7.9 GiB |
| 관리 URL | http://192.168.190.128 |
| 계정 | root / (설정한 비밀번호) |

### 가상 스위치 (vSwitch) 생성 완료

| vSwitch 이름 | 용도 |
|-------------|------|
| att-net | 공격자 네트워크 |
| rf-net | 라우터 ↔ 방화벽 |
| dmz-net | DMZ (웹서버) |
| mng-net | 관리 네트워크 |
| inner-net | 내부 (SIEM) |

### Vyos 라우터 설정 완료

| 인터페이스 | IP | 네트워크 | 용도 |
|----------|-----|---------|------|
| eth0 | DHCP (192.168.190.x) | VM Network (out-net) | 인터넷 |
| eth1 | 10.0.0.1/24 | rf-net | 방화벽 연결 |
| eth2 | 10.50.50.1/24 | att-net | 공격자 네트워크 |

**설정 항목:**
- NAT Masquerade: 10.0.0.0/8 → eth0 (인터넷 접속용)
- DNS: 8.8.8.8
- 기본 게이트웨이: 192.168.190.2
- 정적 라우팅: 10.0.10.0/24, 10.0.50.0/24, 10.0.100.0/24 → next-hop 10.0.0.254
- 인터넷 연결: ✅ 확인 (ping 8.8.8.8 성공)

### pfsense 방화벽 설정 완료

**인터페이스 ↔ MAC 주소 매핑 (중요!)**

ESXi 어댑터 순서와 pfSense vmx 번호가 MAC 주소 순서에 따라 다르게 배정됨:

| ESXi 어댑터 | 네트워크 | MAC 주소 | pfSense 인터페이스 |
|-----------|---------|---------|-----------------|
| 어댑터 1 | rf-net | 00:0c:29:1e:3b:e3 | vmx1 |
| 어댑터 2 | dmz-net | 00:0c:29:1e:3b:ed | vmx2 |
| 어댑터 3 | mng-net | 00:0c:29:1e:3b:f7 | vmx3 |
| 어댑터 4 | inner-net | 00:0c:29:1e:3b:01 | vmx0 |

**인터페이스 할당 (MAC 기반 재매핑 완료):**

| pfSense 역할 | vmx 인터페이스 | IP 주소 | 실제 네트워크 |
|-------------|-------------|---------|-----------|
| WAN | vmx1 (:3b:e3) | 10.0.0.254/24 (GW: 10.0.0.1) | rf-net |
| LAN | vmx3 (:3b:f7) | 10.0.50.1/24 | mng-net |
| OPT1 | vmx2 (:3b:ed) | 10.0.10.1/24 | dmz-net |
| OPT2 | vmx0 (:3b:01) | 10.0.100.1/24 | inner-net |

**연결 확인:**
- pfsense → Vyos (10.0.0.1) ping: ✅ 성공

### Mng-Mint (관리 클라이언트)

| 항목 | 값 |
|------|-----|
| OS | Linux Mint |
| 네트워크 | mng-net |
| IP | 10.0.50.17/24 (GW: 10.0.50.1) |
| 상태 | ✅ 네트워크 설정 완료 |
| 계정 | kim / (설정한 비밀번호) |
| ping 확인 | pfsense(10.0.50.1) ✅ 성공 |

### Bee-box (취약 웹서버)

| 항목 | 값 |
|------|-----|
| OS | Ubuntu (32비트) - bWAPP 사전 설치 |
| 네트워크 | dmz-net |
| IP | 10.0.10.50/24 (GW: 10.0.10.1) |
| 설치 방식 | OVF → 기존 가상 시스템 등록 (vmx 직접 등록) |
| 계정 | bee / bug |
| 상태 | ✅ 설치 완료, 네트워크 설정 완료 |
| 키보드 | USA 레이아웃으로 변경 완료 |

### Ubuntu + Splunk (SIEM 서버)

| 항목 | 값 |
|------|-----|
| OS | Ubuntu Server 20.04 LTS |
| 네트워크 | inner-net ✅ (전환 완료) |
| IP | 10.0.100.50/24 (GW: 10.0.100.1) |
| hostname | splunk |
| Splunk | 8.2.0 설치 완료, 자동 시작 설정 완료 |
| Splunk 계정 | kisia01 / qwer12#$ |
| Splunk 웹 | http://10.0.100.50:8000 |
| SSH 계정 | user / (설정한 비밀번호) |
| SSH 접속 | Mng-Mint에서 `ssh user@10.0.100.50` ✅ 확인 |
| MobaXterm | Windows에서 설치 완료 (inner-net 전환 후 직접접속 불가, Mng-Mint SSH 사용) |

### pfsense 웹 콘솔 접속 정보

| 항목 | 값 |
|------|-----|
| 접속 URL | http://10.0.50.1 (HTTP, 포트 80) |
| 접속 방법 | Mng-Mint 브라우저에서 접속 |
| 계정 | admin / pfsense (→ qwer12#$ 변경 예정) |
| 버전 | 2.7.2-RELEASE (FreeBSD 14.0-CURRENT) |
| 웹서버 | nginx (포트 80에서 동작) |
| 참고 | HTTPS(443)는 비활성, HTTP(80)만 사용 가능 |

### pfsense 방화벽 룰 현황

| 인터페이스 | 룰 | 설명 |
|----------|-----|------|
| WAN | ✅ Allow TCP * → 10.0.10.50:80 | NAT (외부→Bee-box 웹서버) |
| WAN | ❌ Deny all TCP | 나머지 차단 |
| MNGNET | (anti-lockout 기본룰) | 관리 접속 허용 |
| DMZNET | ❌ Deny all TCP | 전체 차단 |
| INNERNET | ❌ Deny all TCP | 전체 차단 |

---

### Snort IPS (pfsense)

| 항목 | 값 |
|------|-----|
| 패키지 | Snort (pfSense Package Manager에서 설치) |
| 모니터링 인터페이스 | WAN (vmx1) |
| 룰셋 | Snort GPLv2 + ET Open |
| 업데이트 주기 | 1Day, 04:00 |
| 카테고리 | Select All 적용 |
| 상태 | ✅ Running |

---

## 완료된 추가 설정

### Att-Mint (공격자 클라이언트)

| 항목 | 값 |
|------|-----|
| OS | Linux Mint (mng-mint 복제) |
| 네트워크 | att-net |
| IP | 10.50.50.17/24 (GW: 10.50.50.1) |
| 생성 방법 | 데이터스토어 브라우저에서 mng-mint 폴더 복사 → 기존 VM 등록 |
| 상태 | ✅ 설치 완료, 네트워크 설정 완료 |

### Splunk 로그 수집 설정

| 항목 | 값 |
|------|-----|
| Splunk 데이터 입력 | UDP 514 (syslog) |
| Source type | syslog |
| Index | pfsense (신규 생성) |
| pfSense Remote Logging | 10.0.100.50, Everything 체크 |
| 수집 확인 | ✅ index=pfsense 검색 → 483 events 확인 |

---

## 다음 진행 예정

### 공격 탐지 및 대응 실습 (siem-project 레포)
- Phase 1: att-mint에서 Bee-box 공격 수행
- Phase 2: Splunk 로그 분석 + 방화벽 정책 대응
- Phase 3: SOC 관제 시뮬레이션

---

## 안전한 종료/시작 순서

### 종료 순서 (역순)
```
1. Ubuntu(Splunk) → sudo poweroff
2. Bee-box → sudo poweroff
3. Mng-Mint → sudo poweroff
4. pfsense → 콘솔 메뉴 6 (Halt system) → y
5. Vyos → poweroff
6. ESXi → F2 → Shut Down
7. VMware Workstation 닫기
```

### 시작 순서
```
1. VMware Workstation → ESXi VM 시작
2. ESXi 웹 콘솔 접속 (http://192.168.190.128)
3. Vyos 시작
4. pfsense 시작
5. Mng-Mint 시작
6. Bee-box 시작
7. Ubuntu(Splunk) 시작
```

### ESXi 리소스 주의사항
- ESXi RAM: 7.9GB (VMware Workstation에서 150GB 디스크로 확장 완료)
- 데이터스토어: 150GB (디스크 확장 완료, ISO 삭제로 공간 확보 완료)
- VM 동시 실행 시 메모리 부족 주의 (커널 패닉 발생 이력 있음)
- 필요 없는 VM은 꺼두고 작업할 것
