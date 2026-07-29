# 11. SIEM 환경구성 진행상황

> 최종 업데이트: 2026-07-29

---

## 현재 진행 상태

| 단계 | 작업 | 상태 |
|------|------|------|
| 1 | VMware Workstation 17.6.0 설치 | ✅ 완료 |
| 2 | VMware ESXi 6.7.0 설치 (Nested VM) | ✅ 완료 |
| 3 | ESXi 가상 스위치 5개 생성 | ✅ 완료 |
| 4 | Vyos 라우터 설치 및 설정 | ✅ 완료 |
| 5 | pfsense 방화벽 설치 및 IP 설정 | ✅ 완료 |
| 6 | Mng-Mint 설치 (OS 설치만 완료) | ⏳ 네트워크 설정 필요 |
| 7 | pfsense 웹 콘솔 접속 및 상세 설정 | ❌ 미진행 |
| 8 | pfsense IPS (Snort) 구축 | ❌ 미진행 |
| 9 | Bee-box 웹서버 설치 | ❌ 미진행 |
| 10 | Ubuntu + Splunk SIEM 설치 | ❌ 미진행 |
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
| 상태 | OS 설치 완료, 네트워크 설정 미완료 |
| 계정 | kim / (설정한 비밀번호) |

---

## 다음 시간 진행 예정

### 1. Mng-Mint 네트워크 설정

```yaml
# sudo xed /etc/netplan/1-network-manager-all.yaml
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
ping 10.0.50.1    # pfsense 연결 확인
ping 10.0.0.1     # Vyos 라우터 확인
ping 8.8.8.8      # 인터넷 확인
```

### 2. pfsense 웹 콘솔 접속

Mng-Mint 브라우저에서: `http://10.0.50.1`
- 계정: admin / pfsense → 비밀번호 변경: qwer12#$
- Timezone: Asia/Seoul
- 인터페이스 이름 변경: LAN→MNG-NET, OPT1→DMZ-NET, OPT2→INNER-NET

### 3. pfsense 방화벽 룰 및 포트포워딩 설정

### 4. Snort IPS 설치

### 5. Bee-box 웹서버 설치

### 6. Ubuntu + Splunk 설치

### 7. Att-Mint 설정

### 8. 로그 수집 연동 테스트

---

## 안전한 종료/시작 순서

### 종료 순서 (역순)
```
1. Mng-Mint → sudo poweroff
2. pfsense → 콘솔 메뉴 6 (Halt system) → y
3. Vyos → poweroff
4. ESXi → F2 → Shut Down
5. VMware Workstation 닫기
```

### 시작 순서
```
1. VMware Workstation → ESXi VM 시작
2. ESXi 웹 콘솔 접속 (http://192.168.190.128)
3. Vyos 시작
4. pfsense 시작
5. Mng-Mint 시작
```
