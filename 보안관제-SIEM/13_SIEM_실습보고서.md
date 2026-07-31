# 통합보안관제 가상환경 구축 실습보고서

| 항목 | 내용 |
|------|------|
| **교육과정** | AI 보안관제 실무 (새싹 SW 5기) |
| **강사명** | 이강재 / 이글루코퍼레이션 수석부장 |
| **실습일자** | 2026.7.29.(화) ~ 2026.7.31.(목) |
| **실습주제** | 통합보안관제 가상환경 구축 |
| **실습목적** | 통합 보안관제 가상환경 구축을 통해 실제 경보 패킷 수집 및 분석 환경 구성 |
| **활용도구** | VMware Workstation, VMware ESXi 6.7, VyOS, pfSense, Splunk, BeeBox, LinuxMint, MobaXterm |
| **산출물** | 가상환경 (ESXi 위 6개 VM 구동 + Splunk 로그 수집 확인) |

---

## 실습내용

### 1. 가상화 구성도 이해

본 실습의 전체 네트워크 구성은 중첩 가상화(Nested Virtualization) 방식을 사용한다. 물리 PC 위에 VMware Workstation을 설치하고, 그 안에 ESXi 6.7 하이퍼바이저를 구동한 뒤, ESXi 내부에 6개의 게스트 VM을 배치한다.

**네트워크 구성도**

```
[인터넷] ──── [VMware Workstation (물리PC)]
                    │
                [ESXi 6.7.0]
                    │
          ┌─────────┼─────────┐
          │         │         │
     [out-net]  [rf-net]   [att-net]
     VM Network  10.0.0.0/24  10.50.50.0/24
          │         │         │
       [VyOS]   [pfSense]  [att-mint]
     라우터      방화벽     공격자PC
          │         │
          │    ┌────┼────┐
          │    │    │    │
          │ [mng-net] [dmz-net] [inner-net]
          │ 10.0.50.0  10.0.10.0  10.0.100.0
          │    │    │    │
          │ [mng-mint] [bee-box] [Ubuntu]
          │ 관리PC   웹서버   Splunk서버
          │ 10.0.50.17 10.0.10.50 10.0.100.50
```

**가상 스위치 및 네트워크 대역**

| vSwitch | 포트그룹 | 대역 | 용도 |
|---------|----------|------|------|
| vSwitch0 | VM Network (out-net) | DHCP | 외부 인터넷 연결 |
| vSwitch1 | rf-net | 10.0.0.0/24 | pfSense WAN 구간 |
| vSwitch2 | att-net | 10.50.50.0/24 | 공격자 네트워크 |
| vSwitch3 | dmz-net | 10.0.10.0/24 | DMZ (웹서버) |
| vSwitch4 | mng-net | 10.0.50.0/24 | 관리 네트워크 |
| vSwitch5 | inner-net | 10.0.100.0/24 | 내부 네트워크 (Splunk) |

---

### 2. VMware Workstation 설치 및 설정

VMware Workstation에서 ESXi 6.7.0 가상머신을 생성하고 부팅한다.

![VMware Workstation - ESXi VM 목록](images/스크린샷%202026-07-31%20141036.png)

VMware Workstation에서 Virtual Machines 폴더 내 ESXi 6.7 VM이 생성된 모습이다.

![ESXi 부팅 화면](images/스크린샷%202026-07-31%20141246.png)

ESXi 설치 미디어로 부팅하여 하이퍼바이저 설치를 진행한다.

---

### 3. VMware ESXi 설치 및 설정

#### 3-1. ESXi 데이터스토어 확장

ESXi 설치 후 데이터스토어 용량이 부족하여 확장이 필요했다. Web UI에서 확장을 시도하면 "호스트 구성을 변경할 수 없습니다" 오류가 발생한다.

![데이터스토어 확장 오류](images/스크린샷%202026-07-31%20111740.png)

ESXi Web UI에서 데이터스토어 확장 시 오류가 발생한 화면이다.

![디바이스 선택](images/스크린샷%202026-07-31%20111802.png)

![파티션 구성](images/스크린샷%202026-07-31%20111820.png)

![파티션 타입 선택](images/스크린샷%202026-07-31%20111850.png)

![확장 완료 화면](images/스크린샷%202026-07-31%20111914.png)

#### 3-2. SSH를 통한 데이터스토어 확장

Web UI 오류로 인해 SSH를 통해 직접 파티션을 조작한다. `partedUtil`과 `vmkfstools`를 사용하여 데이터스토어를 확장한다.

![SSH 파티션 명령어 실행](images/스크린샷%202026-07-31%20112340.png)

SSH로 접속하여 `partedUtil` 명령으로 파티션 정보를 확인하고 확장을 시도한다.

![파티션 확장 에러 및 수정](images/스크린샷%202026-07-31%20112420.png)

파티션 종료 섹터 값 충돌(314572799) 오류가 발생하여, GPT 백업 영역(34섹터)을 고려한 314572766으로 수정하여 해결했다.

#### 3-3. ESXi 가상 시스템 구성

![ESXi VM 목록 - 초기 생성](images/스크린샷%202026-07-31%20142123.png)

vyos와 mng-mint VM이 생성되어 등록된 초기 모습이다.

![ESXi VM 전체 목록](images/스크린샷%202026-07-31%20112820.png)

최종적으로 6개 VM(vyos, mng-mint, pfsense, bee-box, ubuntu, att-mint)이 모두 생성된 모습이다.

---

### 4. LinuxMint 설치 및 구성

#### 4-1. mng-mint (관리 PC) 설치

mng-mint는 관리 네트워크(mng-net, 10.0.50.0/24)에 위치하며, pfSense WebGUI 접속 및 Splunk 웹 UI 접속에 사용하는 관리용 PC이다.

- IP: 10.0.50.17/24
- Gateway: 10.0.50.1 (pfSense LAN)
- 네트워크: mng-net

#### 4-2. att-mint (공격자 PC) 복제

att-mint는 mng-mint VM을 복제하여 생성한다. 교안에 따라 데이터스토어 브라우저에서 mng-mint 폴더를 att-mint로 복사한 뒤, "기존 가상 시스템 등록"으로 등록한다.

![교안 - LinuxMint 복제 절차](images/스크린샷%202026-07-31%20153158.png)

교안의 LinuxMint 복사 적용 절차이다. 데이터스토어 브라우저에서 Mng-Mint 폴더를 복사하고, 기존 가상 시스템 등록으로 VM을 추가한다.

![데이터스토어 - mng-mint 폴더 복사](images/스크린샷%202026-07-31%20152826.png)

데이터스토어 브라우저에서 mng-mint 폴더를 선택하여 복사를 진행한다.

![att-mint 폴더 - 잘못된 복사 (vmdk만 존재)](images/스크린샷%202026-07-31%20152946.png)

첫 번째 시도에서 att-mint 폴더에 vmdk 파일만 복사되고 vmx 파일이 없어 VM 등록이 불가능했다.

![VM 등록 - VMX 파일 없음](images/스크린샷%202026-07-31%20153057.png)

"기존 가상 시스템 등록" 화면에서 att-mint 디렉토리를 선택했으나 VMX 파일이 없어 "표시할 항목 없음"으로 표시된다.

![att-mint 내 중첩 폴더 구조](images/스크린샷%202026-07-31%20153246.png)

att-mint 폴더 안에 mng-mint 하위 폴더가 중첩 생성된 구조를 확인했다. mng-mint VM을 종료한 후 다시 복사하여 해결했다.

![VM 등록 - mng-mint.vmx 발견](images/스크린샷%202026-07-31%20153118.png)

올바르게 복사된 후 mng-mint.vmx 파일이 발견되어 등록이 가능해졌다.

#### 4-3. att-mint 네트워크 설정

복제 후 VM 이름을 att-mint로 변경하고, 네트워크를 att-net으로 변경한 뒤 netplan 설정을 수정한다.

```yaml
network:
  version: 2
  renderer: NetworkManager
  ethernets:
    ens160:
      addresses: [10.50.50.17/24]
      gateway4: 10.50.50.1
      nameservers:
        addresses: [8.8.8.8,8.8.4.4]
```

![netplan YAML 에러 - expected sequence](images/스크린샷%202026-07-31%20113344.png)

netplan apply 시 YAML 포맷 오류(addresses 필드)가 발생했다. 대괄호(`[]`) 형식으로 수정하여 해결했다.

![netplan 에러 - unknown key 'version'](images/스크린샷%202026-07-31%20153741.png)

`1-network-manager-all.yaml` 파일에서 `version` 키 인식 오류가 발생했다. YAML 들여쓰기(2칸)를 정확히 맞춰 해결했다.

---

### 5. VyOS 라우터 설치 및 구성

VyOS는 외부 네트워크(out-net)와 내부 네트워크(rf-net, att-net)를 연결하는 라우터 역할을 수행한다.

![VyOS 인터페이스 설정](images/스크린샷%202026-07-31%20142351.png)

VyOS 콘솔에서 `configure` 모드로 진입하여 각 인터페이스를 설정하는 모습이다.

**VyOS 인터페이스 구성**

| 인터페이스 | IP | 설명 |
|-----------|-----|------|
| eth0 | DHCP | outside (VM Network → 인터넷) |
| eth1 | 10.0.0.1/24 | inside (rf-net → pfSense WAN) |
| eth2 | 10.50.50.1/24 | attacker (att-net → 공격자) |

---

### 6. pfSense 설치 및 설정

#### 6-1. pfSense VM 하드웨어 구성

pfSense VM에는 4개의 네트워크 어댑터를 할당하여 각 네트워크 존을 연결한다.

![pfSense VM 설정 - 4개 NIC](images/스크린샷%202026-07-31%20142738.png)

pfSense VM 설정 편집 화면이다. 네트워크 어댑터가 rf-net, dmz-net, mng-net, inner-net 4개로 구성되어 있다.

#### 6-2. pfSense 인터페이스 할당

pfSense는 MAC 주소 알파벳 순으로 vmx 인터페이스를 할당한다. 따라서 ESXi 어댑터 순서와 pfSense 내부 인터페이스 순서가 다르다.

![pfSense MAC 주소 및 vmx 매핑](images/스크린샷%202026-07-31%20143358.png)

pfSense 콘솔에서 확인한 MAC 주소별 vmx 인터페이스 매핑이다.

| vmx 인터페이스 | MAC 주소 | 매핑 네트워크 |
|--------------|----------|-------------|
| vmx0 | 00:0c:29:1e:3b:01 | inner-net |
| vmx1 | 00:0c:29:1e:3b:e3 | rf-net |
| vmx2 | 00:0c:29:1e:3b:ed | dmz-net |
| vmx3 | 00:0c:29:1e:3b:f7 | mng-net |

인터페이스 할당 결과:

| pfSense 인터페이스 | vmx | 네트워크 |
|-------------------|-----|----------|
| WAN | vmx1 | rf-net |
| LAN | vmx3 | mng-net |
| OPT1 | vmx2 | dmz-net |
| OPT2 | vmx0 | inner-net |

![pfSense 인터페이스 할당 완료](images/스크린샷%202026-07-31%20144020.png)

pfSense 콘솔에서 인터페이스 할당이 완료된 모습이다. WAN→vmx1, LAN→vmx3, OPT1→vmx2, OPT2→vmx0으로 할당되었다.

#### 6-3. pfSense IP 주소 설정

각 인터페이스에 IP 주소를 설정한다.

| 인터페이스 | IP | 용도 |
|----------|-----|------|
| WAN (vmx1) | 10.0.0.254/24 | 외부 연결 (rf-net) |
| LAN (vmx3) | 10.0.50.1/24 | 관리 네트워크 (mng-net) |
| OPT1 (vmx2) | 10.0.10.1/24 | DMZ (dmz-net) |
| OPT2 (vmx0) | 10.0.100.1/24 | 내부 네트워크 (inner-net) |

![pfSense 인터페이스 설정 진행](images/스크린샷%202026-07-31%20112450.png)

![pfSense VLAN 설정 질의](images/스크린샷%202026-07-31%20112507.png)

![pfSense 인터페이스 할당 진행](images/스크린샷%202026-07-31%20112521.png)

![pfSense IP 설정 완료](images/스크린샷%202026-07-31%20112720.png)

---

### 7. BeeBox 설치 및 설정

BeeBox(bWAPP)는 DMZ 네트워크에 위치하는 취약한 웹 애플리케이션 서버이다. 외부(공격자)로부터의 공격 대상이 되며, pfSense 방화벽과 Snort IPS의 탐지 대상이 된다.

- IP: 10.0.10.50/24
- Gateway: 10.0.10.1 (pfSense OPT1/DMZNET)
- 네트워크: dmz-net

![bee-box ifconfig - IP 확인](images/스크린샷%202026-07-31%20145501.png)

bee-box에서 `ifconfig` 명령으로 IP 주소(10.0.10.50)가 정상 설정된 것을 확인한다.

#### 트러블슈팅: bee-box 외부 통신 불가

bee-box에서 `ping 8.8.8.8` 시 "Destination Host Unreachable" 오류가 발생했다.

![bee-box ping 실패](images/스크린샷%202026-07-31%20154900.png)

![bee-box ping 재시도 실패](images/스크린샷%202026-07-31%20155034.png)

![bee-box 라우팅 테이블 확인](images/스크린샷%202026-07-31%20155112.png)

`route -n`으로 라우팅 테이블을 확인하면 기본 게이트웨이(10.0.10.1)는 올바르게 설정되어 있으나, 게이트웨이 자체에 ping이 실패한다.

**원인 및 해결:**
1. pfSense DMZNET 방화벽 규칙의 프로토콜이 TCP만 허용 → **Any**로 변경
2. bee-box VM의 ESXi 네트워크 어댑터가 dmz-net으로 설정되지 않음 → **dmz-net으로 변경**

---

### 8. Ubuntu 설치 및 설정

Ubuntu 20.04 LTS는 Splunk Enterprise 서버로 사용된다. inner-net에 위치하여 pfSense로부터 syslog를 수신한다.

![Ubuntu 부팅 - 네트워크 대기](images/스크린샷%202026-07-31%20151030.png)

Ubuntu 부팅 시 "Wait for Network to be Configured" 메시지가 표시된다. inner-net 네트워크 설정이 적용되기를 기다리는 중이다.

**Ubuntu 네트워크 설정 (netplan)**

![교안 - Splunk 네트워크 설정](images/스크린샷%202026-07-31%20150904.png)

교안에 따른 Ubuntu(Splunk) 서버의 netplan 설정이다.

```yaml
network:
  ethernets:
    ens160:
      addresses: [10.0.100.50/24]
      gateway4: 10.0.100.1
      nameservers:
        addresses: [8.8.8.8,8.8.4.4]
```

- IP: 10.0.100.50/24
- Gateway: 10.0.100.1 (pfSense OPT2/INNERNET)
- 네트워크: inner-net

![Ubuntu SSH 접속 - IP 확인](images/스크린샷%202026-07-31%20154234.png)

Ubuntu 콘솔에서 SSH 로그인 후 IP 주소(10.0.100.50)를 확인하고 Splunk가 정상 구동 중인 것을 확인한다.

---

### 9. MobaXterm 설치 및 적용

MobaXterm은 mng-mint에서 Ubuntu(Splunk) 서버로 SSH 접속하여 관리하기 위한 터미널 클라이언트이다.

![MobaXterm SSH 접속](images/스크린샷%202026-07-31%20150154.png)

MobaXterm으로 Ubuntu 서버(192.168.190.137 → 이후 inner-net으로 전환하여 10.0.100.50)에 SSH 접속한 화면이다. 좌측에는 교안의 Splunk 설치 절차가 표시되어 있다.

---

### 10. Splunk 설치 및 설정

#### 10-1. Splunk Enterprise 설치

MobaXterm을 통해 Ubuntu 서버에 SSH 접속 후 Splunk Enterprise 8.2.0을 설치한다.

![dpkg 명령어 오타 에러](images/스크린샷%202026-07-31%20150249.png)

`sudo dpkg-isplunk...` (공백 누락) 오타로 "command not found" 에러가 발생했다. `dpkg -i`로 수정하여 해결했다.

![Splunk 설치 및 CP 에러 처리](images/스크린샷%202026-07-31%20150531.png)

`sudo dpkg -i splunk-8.2.0-...` 명령으로 설치를 진행한다. 설치 후 CP 에러 발생 시 SWID 관련 명령어로 예외 처리하고, `splunk enable boot-start`로 자동 시작을 설정한다.

#### 10-2. Splunk 경로 오타 트러블슈팅

![Splunk 경로 오타 - /oppt/splunk](images/스크린샷%202026-07-31%20154129.png)

mng-mint(user@user-virtual-machine)에서 Splunk를 실행하려 했으나, 이 VM에는 Splunk이 설치되어 있지 않다. Ubuntu(Splunk 서버)에서 실행해야 한다.

![Splunk 경로 오타 수정 및 실행 성공](images/스크린샷%202026-07-31%20154234.png)

Ubuntu(user@splunk)에서 `/oppt/splunk/bin/splunk` (경로 오타)를 `/opt/splunk/bin/splunk start`로 수정하여 성공적으로 실행했다. "The splunk daemon (splunkd) is already running" 메시지로 정상 구동을 확인했다.

#### 10-3. Splunk Web UI 접속

![Splunk 홈 화면](images/스크린샷%202026-07-31%20150832.png)

mng-mint의 Firefox에서 `http://10.0.100.50:8000`(또는 초기 `192.168.190.137:8000`)으로 접속하여 Splunk Enterprise 8.2.0 홈 화면을 확인한다.

![Splunk 홈 화면 (inner-net 전환 후)](images/스크린샷%202026-07-31%20114106.png)

inner-net으로 네트워크 전환 후 `10.0.100.50:8000`으로 접속한 Splunk 홈 화면이다.

---

### 11. pfSense 설정 (방화벽 규칙)

pfSense WebGUI(`https://10.0.50.1`)에 mng-mint에서 접속하여 방화벽 규칙을 설정한다.

#### 11-1. NAT 포트 포워딩

![NAT Port Forward 설정](images/스크린샷%202026-07-31%20151843.png)

WAN 인터페이스에 NAT 포트 포워딩 규칙을 추가한다. 외부에서 HTTP(80) 포트로 들어오는 트래픽을 DMZ의 bee-box(10.0.10.50)로 전달한다.

#### 11-2. WAN 방화벽 규칙

![WAN 방화벽 규칙](images/스크린샷%202026-07-31%20152008.png)

WAN 탭에서 HTTP 트래픽을 bee-box(10.0.10.50:80)로 허용하는 NAT 규칙이 생성된 것을 확인한다.

#### 11-3. DMZNET 방화벽 규칙

![DMZNET 방화벽 규칙](images/스크린샷%202026-07-31%20114529.png)

DMZNET 탭에서 DMZ 네트워크의 트래픽 허용 규칙을 설정한다. 프로토콜은 **Any**로 설정하여 ICMP(ping)를 포함한 모든 프로토콜을 허용한다.

---

### 12. pfSense를 활용한 IPS 구축 (Snort)

pfSense에 Snort IPS 패키지를 설치하여 침입 탐지/방지 시스템을 구축한다.

#### 12-1. Snort 설치 및 Global Settings

![교안 - Snort 설정 절차](images/스크린샷%202026-07-31%20152315.png)

교안에 따른 Snort 설정 순서:
1. Services > Snort > Interfaces > Add > WAN(vmx1) 선택 > Save
2. Global Settings > Enable Snort GPLv2, Enable ET Open 선택 > Update Interval: 1Day > Save
3. Updates > Update Rules 클릭
4. Interfaces > Edit > WAN Categories > Select All > Save
5. Snort 시작 (snort is running 버튼 클릭)

#### 12-2. Snort 인터페이스 추가

![Snort Interfaces - 초기 (비어있음)](images/스크린샷%202026-07-31%20152531.png)

Snort 패키지 설치 직후 인터페이스가 비어있는 상태이다.

![Snort Interfaces - WAN 추가 완료](images/스크린샷%202026-07-31%20152722.png)

WAN(vmx1) 인터페이스가 추가된 모습이다. Pattern Match: AC-BNFA, Blocking Mode: DISABLED로 설정되었다.

![Snort WAN 인터페이스 최종 상태](images/스크린샷%202026-07-31%20154741.png)

Snort가 WAN(vmx1) 인터페이스에서 정상적으로 설정 완료된 최종 모습이다.

---

### 13. pfSense 로그 수집 설정

pfSense의 방화벽 로그와 Snort IPS 로그를 Splunk 서버로 전송하도록 syslog를 설정한다.

#### 13-1. 교안 참조

![교안 - pfSense 로그 수집 설정](images/스크린샷%202026-07-31%20153830.png)

교안에 따른 로그 수집 설정 절차:
- 방화벽 로그를 Splunk에 저장: Settings > Data Inputs > UDP > 514 포트
- 방화벽 규칙에 로그 활성화: Firewall > Rules > DMZNET > Rule Edit > Log packets 체크
- syslog 원격 전송: Status > System Logs > Settings > Remote Logging Options

#### 13-2. pfSense Remote Logging 설정

![pfSense Remote Logging 설정](images/스크린샷%202026-07-31%20155327.png)

pfSense의 Status > System Logs > Settings에서 Remote Logging Options를 설정한다:
- **Enable Remote Logging**: 체크 (Send log messages to remote syslog server)
- **Source Address**: Default (any)
- **IP Protocol**: IPv4
- **Remote log servers**: `10.0.100.50` (Ubuntu/Splunk 서버 IP)
- **Remote Syslog Contents**: **Everything** 체크

#### 13-3. pfSense System Logs 확인

![pfSense System Logs](images/스크린샷%202026-07-31%20114622.png)

pfSense의 System Logs에서 방화벽 로그가 정상적으로 기록되고 있는 것을 확인한다.

---

### 14. 패킷 수집 및 분석

#### 14-1. Splunk 데이터 입력 설정 (UDP 514)

![Splunk UDP 514 데이터 입력](images/스크린샷%202026-07-31%20114238.png)

Splunk에서 Settings > Data Inputs > UDP > 새로 추가하여 포트 514에서 syslog 데이터를 수신하도록 설정한다.

#### 14-2. Splunk 인덱스 생성 (pfsense)

![Splunk Input Settings - pfsense 인덱스](images/스크린샷%202026-07-31%20114423.png)

Source type을 `syslog`로, Index를 새로 생성한 `pfsense`로 설정한다.

#### 14-3. Splunk 로그 수집 확인

pfSense에서 syslog를 Splunk로 전송한 후, Splunk에서 `index=pfsense` 검색으로 로그 수집을 확인한다.

![Splunk 검색 - 483 events 수집 확인](images/스크린샷%202026-07-31%20155909.png)

`index=pfsense` 검색 결과 **483개 이벤트**가 수집된 것을 확인했다. 타임라인 그래프에서 이벤트 분포를 볼 수 있으며, pfSense 방화벽 로그가 Splunk에 정상적으로 수집되고 있음을 확인했다.

#### 트러블슈팅: Splunk 로그 미수신

초기에 pfSense에서 Splunk(10.0.100.50)로 ping이 실패하여 syslog가 전달되지 않았다. pfSense 콘솔에서 옵션 7 (Ping host)로 `10.0.100.50`을 확인한 결과, pfSense INNERNET 인터페이스를 통한 통신이 정상 복구된 후 로그가 수집되기 시작했다.

![pfSense → Splunk 통신 확인 안내](images/스크린샷%202026-07-31%20155452.png)

---

## 실습 결과 요약

| 구성요소 | 상태 | 비고 |
|---------|------|------|
| ESXi 6.7.0 | 정상 구동 | 데이터스토어 SSH 확장 완료 |
| VyOS 라우터 | 정상 구동 | eth0(DHCP), eth1(10.0.0.1), eth2(10.50.50.1) |
| pfSense 방화벽 | 정상 구동 | WAN/LAN/OPT1/OPT2 4개 인터페이스 |
| mng-mint (관리PC) | 정상 구동 | 10.0.50.17, pfSense/Splunk 접속용 |
| att-mint (공격자PC) | 정상 구동 | 10.50.50.17, mng-mint 복제 |
| bee-box (웹서버) | 정상 구동 | 10.0.10.50, DMZ 네트워크 |
| Ubuntu/Splunk | 정상 구동 | 10.0.100.50, Splunk 8.2.0 |
| Snort IPS | 정상 구동 | WAN(vmx1) 인터페이스, GPLv2+ET Open |
| Syslog 수집 | 정상 수집 | UDP 514, index=pfsense, 483 events 확인 |

## 트러블슈팅 정리

| 문제 | 원인 | 해결 |
|------|------|------|
| ESXi 데이터스토어 확장 실패 | Web UI 오류 | SSH로 partedUtil/vmkfstools 직접 실행 |
| dpkg 명령어 오류 | `dpkg-i` 공백 누락 | `dpkg -i`로 수정 |
| Splunk 경로 오류 | `/oppt/splunk` 오타 | `/opt/splunk`로 수정 |
| mng-mint에서 splunk start | Splunk 미설치 VM에서 실행 | Ubuntu(Splunk 서버)에서 실행 |
| att-mint 복제 실패 | mng-mint 가동 중 복사, vmx 누락 | mng-mint 종료 후 재복사 |
| netplan YAML 에러 | 들여쓰기/형식 오류 | 2칸 들여쓰기, 대괄호 형식 적용 |
| bee-box ping 실패 | DMZNET TCP만 허용 + 어댑터 미설정 | 프로토콜 Any + dmz-net 어댑터 변경 |
| Splunk 로그 미수신 | pfSense→Splunk 통신 불가 | pfSense 재시작 후 통신 복구, 483 events 확인 |
