# 08. RPC 서비스 vs xinetd 데몬 (개념 정리)

> 서비스 관리 진단(U-34~U-42 등)에서 자주 등장하는 두 개념. 역할·계층이 달라 혼동하기 쉬워 정리. (교안 보충)

---

## 1. 한 줄 요약

- **xinetd**: 여러 네트워크 서비스를 대신 대기하다 요청이 오면 실행해주는 **중개 데몬(슈퍼 데몬)**
- **RPC**: 원격의 프로그램 함수를 로컬처럼 호출하는 **통신 방식(프로토콜)**. 포트는 rpcbind가 안내

### 교안 정의 (요약)

1. **RPC(Remote Procedure Call) 서비스**  
   내부 네트워크에서 운영 중인 서버에 특정 RPC 서비스를 **원격으로 호출하여 실행**하는 서비스

2. **xinetd(인터넷 슈퍼) 데몬**  
   외부 네트워크에서 운영 중인 서버에 **"r"이 포함된 데몬**(rlogin, rsh, rexec 등)이 보관되어 있을 경우 이를 **강제로 호출해 실행**하는 서비스

> 즉, RPC는 **내부망**에서 원격 서비스를 호출하는 방식이고, xinetd는 **외부망**에서 접근 가능한 `r` 계열 서비스 등을 대신 실행하는 슈퍼 데몬이라는 관점에서 대비된다.

---

## 2. xinetd (Extended Internet Daemon) — 슈퍼 데몬

telnet·ftp·tftp·finger 같은 작은 서비스들을 각각 상시 띄워두지 않고, **xinetd 하나가 대표로 포트를 지키다가 요청이 들어올 때만 해당 서비스를 실행**한다. (과거 `inetd`의 개선판 — 접근제어·로깅 등 보안 기능 강화)

| 항목 | 내용 |
|------|------|
| **정체** | 서비스 실행을 중개하는 데몬 |
| **동작** | 포트 대기(listen) → 요청 수신 → 해당 서비스 프로세스 실행 |
| **목적** | 자주 안 쓰는 서비스를 온디맨드로 실행 → 리소스 절약 + 접근제어 중앙 관리 |
| **설정 파일** | `/etc/xinetd.conf`, `/etc/xinetd.d/<서비스명>` |
| **관리 서비스** | telnet, ftp, tftp, finger, rsh, rlogin 등 |

**설정 예시 (`/etc/xinetd.d/telnet`)**
```
service telnet
{
    disable     = yes        # yes = 서비스 비활성화 (진단 시 이 값 확인)
    socket_type = stream
    protocol    = tcp
    wait        = no
    user        = root
    server      = /usr/sbin/in.telnetd
    only_from   = 192.168.0.0/24   # 접근 허용 IP (접근제어)
}
```

> 진단 시 `disable = yes` 여부로 서비스 활성화 상태를 판단. telnet·finger 등 취약 서비스는 `disable = yes` 이어야 양호.

---

## 3. RPC (Remote Procedure Call) — 원격 함수 호출 방식

네트워크 너머의 프로그램 함수를 **로컬 함수처럼 호출**하는 통신 규약. NFS·NIS 등이 이 방식으로 동작한다. RPC 서비스는 **고정 포트가 없고 랜덤 포트**를 사용하기 때문에, **rpcbind(portmapper, 111번 포트)** 가 "어떤 서비스가 몇 번 포트에 있는지" 안내하는 중개자 역할을 한다.

| 항목 | 내용 |
|------|------|
| **정체** | 원격 프로시저(함수) 호출 통신 방식 |
| **핵심 데몬** | rpcbind (portmapper) — 111번 포트 |
| **포트** | 서비스마다 랜덤 포트 → rpcbind가 매핑·안내 |
| **관리 서비스** | NFS, NIS/NIS+, rpc.statd, automountd 등 |
| **위험성** | 버퍼오버플로우·DoS·원격 실행 취약점 이력 다수 |

**RPC 통신 흐름**
```
클라이언트 → rpcbind(111)에 "NFS 서비스 어디 있어?" 질의
rpcbind    → "2049 (또는 랜덤 포트)에 있음" 응답
클라이언트 → 해당 포트로 실제 RPC 호출
```

**등록된 RPC 서비스 확인**
```bash
rpcinfo -p            # rpcbind에 등록된 RPC 서비스·포트 목록
netstat -tlnp | grep rpc
```

---

## 4. 핵심 차이 비교

| 구분 | xinetd | RPC |
|------|--------|-----|
| **정체** | 서비스 실행 중개 데몬(슈퍼 데몬) | 원격 함수 호출 통신 방식 |
| **역할** | 요청 오면 해당 서비스를 대신 실행 | 원격 프로그램의 함수를 호출 |
| **포트** | 각 서비스의 **고정 포트**를 대표 관리 | rpcbind(111)가 **랜덤 포트**를 매핑·안내 |
| **대상 서비스** | telnet, ftp, tftp, finger | NFS, NIS, rpc.statd, automountd |
| **설정/관리** | `/etc/xinetd.d/` 파일 | rpcbind가 동적 관리 |
| **관련 진단 항목** | U-34(finger), U-44(tftp/talk), U-52(telnet), U-20(inetd.conf 권한) | U-39/40(NFS), U-41(automountd), U-42(RPC) |

---

## 5. 진단 관점 정리

두 계열 모두 **취약점이 많아 불필요 시 비활성화** 권고 대상이다.

**xinetd 계열 조치**
```bash
# 서비스 비활성화 (예: telnet)
vi /etc/xinetd.d/telnet     # disable = yes
systemctl restart xinetd

# 또는 chkconfig
chkconfig telnet off
```

**RPC 계열 조치**
```bash
# 사용 중인 RPC 서비스 확인
rpcinfo -p

# NFS·rpcbind 미사용 시 중지 (U-39, U-42)
systemctl stop rpcbind rpc-statd nfs-server
systemctl disable rpcbind rpc-statd nfs-server
```

> **관계 정리**: xinetd는 "여러 서비스를 대신 띄워주는 문지기 데몬", RPC는 "원격 함수를 호출하는 통신 규약(포트는 rpcbind가 안내)". 둘은 계층이 다르지만, 둘 다 **불필요한 서비스가 열려 있으면 공격 표면이 되므로** 진단에서 함께 점검·차단한다.  
> (→ [06. 환경분석 실전 예시](./06_환경분석_실전예시_CentOS6.9.md)에서 rpcbind·rpc.statd가 외부 노출된 사례 참고)
