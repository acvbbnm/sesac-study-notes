# 11. SIEM 환경구성 진행상황

> 최종 업데이트: 2026-07-30

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
| 7 | pfsense 웹 콘솔 접속 및 상세 설정 | ⚠️ 접속 불가 (HTTPS 타임아웃, 추후 재시도) |
| 8 | Bee-box 웹서버 설치 | ✅ 완료 (OVF 등록, IP 설정 완료) |
| 9 | Ubuntu + Splunk SIEM 설치 | ✅ 완료 (Splunk 8.2.0 설치, 네트워크 inner-net 전환 필요) |
| 10 | pfsense IPS (Snort) 구축 | ❌ 미진행 |
| 11 | Att-Mint 공격자 클라이언트 설정 | ❌ 미진행 |
| 12 | Splunk 로그 수집 설정 (방화벽/IPS) | ❌ 미진행 |

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
| 어댑터 1 | rf-net | 00:0c:29:58:94:a9 | vmx1 |
| 어댑터 2 | dmz-net | 00:0c:29:58:94:b3 | vmx2 |
| 어댑터 3 | mng-net | 00:0c:29:58:94:bd | vmx3 |
| 어댑터 4 | inner-net | 00:0c:29:58:94:c7 | vmx0 |

**인터페이스 할당 (MAC 기반 재매핑 완료):**

| pfSense 역할 | vmx 인터페이스 | IP 주소 | 실제 네트워크 |
|-------------|-------------|---------|-----------|
| WAN | vmx1 (:a9) | 10.0.0.254/24 (GW: 10.0.0.1) | rf-net |
| LAN | vmx3 (:bd) | 10.0.50.1/24 | mng-net |
| OPT1 | vmx2 (:b3) | 10.0.10.1/24 | dmz-net |
| OPT2 | vmx0 (:c7) | 10.0.100.1/24 | inner-net |

**연결 확인:**
- pfsense → Vyos (10.0.0.1) ping: ✅ 성공

### Mng-Mint (관리 클라이언트)

| 항목 | 값 |
|------|-----|
| OS | Linux Mint |
| 네트워크 | mng-net |
| IP | 10.0.50.100/24 (GW: 10.0.50.1) |
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
| 네트워크 | inner-net (현재 VM Network → inner-net 전환 필요) |
| IP | 10.0.100.50/24 (GW: 10.0.100.1) - netplan 설정 완료 |
| hostname | splunk |
| Splunk | 8.2.0 설치 완료, 자동 시작 설정 완료 |
| Splunk 계정 | kisia01 / qwer12#$ |
| Splunk 웹 | http://10.0.100.50:8000 |
| SSH 계정 | user / (설정한 비밀번호) |
| MobaXterm | Windows에서 SSH 접속용으로 설치 완료 |

**TODO:** ESXi에서 네트워크를 inner-net으로 변경 + netplan 고정 IP 재적용

---

## 다음 시간 진행 예정

### 1. Ubuntu 네트워크 inner-net 전환
- ESXi에서 ubuntu VM 네트워크 → inner-net 변경
- netplan 고정 IP 적용 (10.0.100.50/24)

### 2. pfsense 웹 콘솔 접속 재시도
- Mng-Mint에서 https://10.0.50.1 접속
- webConfigurator 재시작 (콘솔 11번) 후 시도
- 계정: admin / pfsense → 비밀번호 변경: qwer12#$

### 3. Att-Mint 공격자 클라이언트 설정
- IP: 10.50.50.17/24, GW: 10.50.50.1
- 네트워크: att-net

### 4. pfsense 방화벽 룰 및 포트포워딩 설정

### 5. Snort IPS 설치

### 6. Splunk 로그 수집 연동 테스트

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
- 데이터스토어: 92.5GB (ISO 삭제로 공간 확보 필요)
- VM 동시 실행 시 메모리 부족 주의 (커널 패닉 발생 이력 있음)
- 필요 없는 VM은 꺼두고 작업할 것
