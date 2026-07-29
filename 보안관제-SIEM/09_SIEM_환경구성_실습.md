# 09. SIEM 환경 구성 실습

> 강의교재 2 — SIEM 환경 구성 (이글루코퍼레이션 이강재, 2026.07)

---

## 1. 가상화 구성도

```
인터넷 (192.168.190.0/24 — VMware NAT)
         │
   [Vyos 라우터]
   eth0: DHCP       (out-net, 외부)
   eth1: 10.0.0.1   (rf-net,  라우터↔방화벽)
   eth2: 10.50.50.1 (att-net, 공격자 망)
         │
   rf-net (10.0.0.0/24)
         │
   [pfsense 방화벽 + IPS(Snort)]
   WAN:  10.0.0.254
   ├── dmz-net   10.0.10.0/24  → [Bee-box 웹서버] 10.0.10.50
   ├── mng-net   10.0.50.0/24  → [Mng-Mint 클라이언트] 10.0.50.100
   └── inner-net 10.0.100.0/24 → [Splunk SIEM] 10.0.100.50

att-net (10.50.50.0/24)
   └── [Att-Mint 공격자 클라이언트] 10.50.50.17
```

---

## 2. VMware Workstation 설치

| 항목 | 내용 |
|------|------|
| 버전 | VMware Workstation 17.6.0 |
| Key | `MC60H-DWHD5-H80U9-6V85M-8280D` |

**NAT 네트워크 IP 설정**
```
Edit > Virtual Network Editor > Type: NAT 선택
> Change Setting > Subnet IP: 192.168.190.0 > Apply > OK
```

---

## 3. VMware ESXi 설치

| 항목 | 내용 |
|------|------|
| 버전 | VMware ESXi 6.7.0 |
| CPU | 8 vCPU |
| Memory | 8 GB |
| HDD | 110 GB (Single file) |

**스토리지 디렉터리 생성**
```
스토리지 > 데이터스토어 > 데이터스토어 브라우저 > 디렉토리 생성 > images
```

**가상스위치 생성 (5개)**
- `att-net` / `rf-net` / `dmz-net` / `mng-net` / `inner-net`

---

## 4. Linux Mint 설치 (Mng-Mint)

| 항목 | 내용 |
|------|------|
| 역할 | 관리 클라이언트 |
| IP | 10.0.50.100/24 |
| Network | mng-net |
| CPU/RAM/HDD | 1 / 1GB / 16GB |

**설치 후 네트워크 설정**
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
ping 10.0.50.1
ping 10.0.0.1
ping 8.8.8.8
```

---

## 5. Vyos 라우터 설치

| 항목 | 내용 |
|------|------|
| 설치 방식 | OVA 파일 |
| CPU/RAM/HDD | 1 / 512MB / 10GB |
| Network 어댑터 | VM-Network / rf-net / att-net |

**기본 네트워크 설정**
```bash
config
set interfaces ethernet eth0 address dhcp           # 외부 (인터넷)
set interfaces ethernet eth0 description 'outside'
set interfaces ethernet eth1 address '10.0.0.1/24'  # 내부 (rf-net)
set interfaces ethernet eth1 description 'inside'
set interfaces ethernet eth2 address '10.50.50.1/24' # 공격자망 (att-net)
set interfaces ethernet eth2 description 'attacker'
commit
save
```

**DNS 설정**
```bash
set system name-server 8.8.8.8
commit
save
ping 8.8.8.8
```

**NAT 설정 (내부 → 외부)**
```bash
set nat source rule 100 outbound-interface 'eth0'
set nat source rule 100 source address '10.0.0.0/8'
set nat source rule 100 translation address masquerade
commit
save
```

**기본 게이트웨이 설정**
```bash
set system gateway-address 192.168.190.2
commit
save
```

**정적 라우팅 설정**
```bash
set protocols static route 10.0.0.0/24  next-hop 10.0.0.1
set protocols static route 10.0.10.0/24 next-hop 10.0.0.1
set protocols static route 10.0.50.0/24 next-hop 10.0.0.1
set protocols static route 10.0.100.0/24 next-hop 10.0.0.1
commit
save
```

---

## 6. pfsense 방화벽 설치

| 항목 | 내용 |
|------|------|
| 설치 방식 | ISO |
| 설치 옵션 | Auto (UFS) |
| CPU/RAM/HDD | 1 / 1GB / 20GB(씬) |
| 인증 | admin / pfsense → 변경: qwer12#$ |

**네트워크 어댑터**
- 어댑터1: rf-net (WAN)
- 어댑터2: dmz-net (OPT1)
- 어댑터3: mng-net (LAN)
- 어댑터4: inner-net (OPT2)

**인터페이스 IP 설정 (콘솔)**
```
WAN  : 10.0.0.254/24  GW: 10.0.0.1
LAN  : 10.0.50.1/24
OPT1 : 10.0.10.1/24   (DMZ-NET)
OPT2 : 10.0.100.1/24  (INNER-NET)
```

**Web UI 초기 설정 (http://10.0.50.1)**
```
Timezone   : Asia/Seoul
admin PW   : qwer12#$
인터페이스 명:
  LAN  → MNG-NET
  OPT1 → DMZ-NET
  OPT2 → INNER-NET
```

**웹서비스 포트포워딩**
```
Firewall > NAT > Port Forward > Add
  Interface          : WAN
  Address Family     : IPv4
  Protocol           : TCP
  Destination        : WAN address
  Destination Port   : HTTP
  Redirect Target IP : 10.0.10.50
  Redirect Target Port: HTTP
```

**기본 정책 (Deny All)**
```
Firewall > Rules > WAN     → Default Deny 추가
Firewall > Rules > DMZNET  → Default Deny 추가
Firewall > Rules > INNERNET → Default Deny 추가
```

---

## 7. pfsense IPS (Snort) 구축

```
1. System > Update > Update Settings > Save
2. System > Package Manager > Available Package > 'snort' 검색 > Install > Confirm
3. Services > Snort > Interfaces > Add > Interface: WAN(vmx0) > Save
4. Global Settings
   - Enable Snort GPLv2 체크
   - Enable ET Open 체크
   - Update Interval: 1Day
   - Update Start Time: 04:00
   > Save
5. Updates > Update Rules 클릭
6. Services > Snort > Interfaces > Edit > WAN Categories > Select All > Save
7. Services > Snort > Interfaces > 'snort is running' 버튼 클릭
```

**Snort 로그를 syslog로 전송 설정**
```
Services > Snort > Interfaces > Edit > WAN Settings > Alert Settings
- "Snort will send Alerts to the firewall's system log" 체크
- System Log Facility: LOG_USER
→ 스노트 룰 재수행 클릭
```

---

## 8. Bee-box (취약 웹서버) 설치

| 항목 | 내용 |
|------|------|
| 설치 방식 | OVF/VMDK |
| IP | 10.0.10.50/24 |
| 인증 | bee / bug |

**네트워크 설정**
```bash
sudo gedit /etc/network/interfaces
```
```
auto lo
iface lo inet loopback

auto eth1
iface eth1 inet static
  address 10.0.10.50
  netmask 255.255.255.0
  gateway 10.0.10.1
  dns-nameservers 8.8.8.8
```
```bash
sudo reboot
ifconfig
```

---

## 9. Ubuntu (Splunk 서버) 설치

| 항목 | 내용 |
|------|------|
| IP | 10.0.100.50/24 |
| Network | inner-net |
| CPU/RAM/HDD | 1 / 1GB / 50GB(씬) |

**hostname 변경**
```bash
sudo vim /etc/hostname   # kisia01 → splunk
sudo vim /etc/hosts      # 127.0.1.1 splunk
```

**네트워크 설정**
```yaml
# sudo vim /etc/netplan/00-installer-config.yaml
network:
  ethernets:
    ens160:
      addresses: [10.0.100.50/24]
      gateway4: 10.0.100.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```
```bash
# 네트워크 어댑터: VMnetwork → inner-net 변경 후
sudo reboot
```

---

## 10. MobaXterm 설치 및 Splunk 배포

**SSH 세션 설정**
```
Remote host     : 192.168.190.130
Specify username: kisia01
```

**파일 복사**
```
splunk-8.2.0-e053ef3c985f-linux-2.6-amd64.deb
→ 세션 하단에 드래그 앤 드롭 (자동 복사)
```

**Splunk 설치**
```bash
sudo dpkg -i splunk-8.2.0-e053ef3c985f-linux-2.6-amd64.deb
# CP 에러 발생 시:
sudo cp /opt/splunk/swidtag/splunk-Splunk-Enterprise-primary.swidtag \
        /opt/splunk/etc/regid.2001-12.com.splunk-Splunk-Enterprise.swidtag
sudo chown splunk:splunk /opt/splunk/etc/regid.2001-12.com.splunk-Splunk-Enterprise.swidtag

sudo /opt/splunk/bin/splunk enable boot-start   # 자동 시작 설정 (약관: q → y)
# 계정: kisia01 / qwer12#$
sudo /etc/init.d/splunk start
```

**웹 접속**
```
http://10.0.100.50:8000
```

---

## 11. Att-Mint (공격자 클라이언트) 설정

Mng-Mint를 복사하여 공격자 클라이언트로 설정.

```bash
# 네트워크 변경: mng-net → att-net
sudo xed /etc/netplan/1-network-manager-all.yaml
```
```yaml
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    ens160:
      addresses: [10.50.50.17/24]
      gateway4: 10.50.50.1
      nameservers:
        addresses: [8.8.8.8, 8.8.4.4]
```
```bash
sudo netplan apply
ping 10.50.50.1
ping 10.0.0.1
ping 8.8.8.8
```

---

## 12. Splunk 로그 수집 설정

### 방화벽(pfsense) 로그 수집

**Splunk에서 syslog 수신 포트 설정**
```
설정 > 데이터 입력 > UDP > 새로 추가
  포트       : 514
  Source type: syslog
  Index      : 새 인덱스 만들기 → index name: pfsense
```

**pfsense에서 Splunk로 syslog 전송**
```
Status > System Logs > Settings > Remote Logging Options
  Send log messages to remote syslog server: 체크
  Remote log servers: 10.0.100.50
  Remote Syslog Contents: Everything
```

**pfsense 방화벽 룰 로그 활성화**
```
Firewall > Rules > DMZNET > Rule Edit
Extra Options > "Log packets that are handled by this rule" 체크
```

### IPS(Snort) 로그 수집

```
Services > Snort > Interfaces > Edit > WAN Settings > Alert Settings
  Snort will send Alerts to firewall's system log: 체크
  System Log Facility: LOG_USER
→ 스노트 룰 재수행 클릭
```

**Splunk에서 IPS 로그 수집 확인**
```
설정 > 라이선싱 > 라이선스 그룹 변경 > 엔터프라이즈 평가판 라이선스
Services > Snort > Interfaces > Snort Rule Edit
```

### 수집 확인

```
# Bee-box에서 트래픽 발생
ping 8.8.8.8

# Splunk 웹에서 확인
http://10.0.100.50:8000
검색 > index=*    (kisia01 / qwer12#$)
```
