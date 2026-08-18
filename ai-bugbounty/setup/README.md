# setup — 실습 환경 세팅

강의 "AI로 코드 읽기(MCP)" 파트를 실제로 따라 하기 위한 세팅 파일 모음입니다. 가상환경의 **Kali(Claude Code 클라이언트)** 에서 **Windows 호스트의 IDA Pro(MCP 서버)** 에 붙는 구성을 다룹니다.

```
[Windows 호스트]                       [Kali 게스트 VM]
 IDA Pro 9.x                            Claude Code
   └ ida-pro-mcp 플러그인                   │
       HTTP 0.0.0.0:13337/mcp  ◄────────────┘
                             가상 네트워크(NAT/Host-only)
```

## 파일

| 파일 | 용도 |
|---|---|
| [`IDA-MCP-Kali-연동.md`](IDA-MCP-Kali-연동.md) | 설치 → 0.0.0.0 바인딩 → 방화벽 → Kali `claude mcp add` → 트러블슈팅 전체 절차 |
| [`start-ida-mcp.bat`](start-ida-mcp.bat) | Windows에서 방화벽 규칙 확인/생성 + IDA 실행 + 13337 LISTEN 대기 + 접속 IP 출력 |
| [`ida_mcp_diag.py`](ida_mcp_diag.py) | 플러그인이 `Edit > Plugins`에 안 뜰 때 IDA 안에서 `File > Script file...`로 실행해 원인 진단 |

## 자주 막히는 3가지 (요약)

1. **플러그인이 안 뜸** → 대개 IDA의 Python이 3.11 미만. `idapyswitch.exe`로 3.12/3.13을 선택하고 IDA 재시작. (ida-pro-mcp는 `from typing import NotRequired`를 써서 3.10에서 import가 실패함)
2. **Kali에서 연결 안 됨** → 플러그인 기본 바인딩이 `127.0.0.1`. `Ctrl+Alt+M`에서 Host를 `0.0.0.0`으로. (또는 `DEFAULT_HOST`를 편집)
3. **curl 타임아웃** → Windows 방화벽 TCP 13337 인바운드 미허용. `netsh advfirewall firewall add rule ... localport=13337 profile=any`

자세한 내용은 [`IDA-MCP-Kali-연동.md`](IDA-MCP-Kali-연동.md) 참고.

## 참고

- [mrexodia/ida-pro-mcp](https://github.com/mrexodia/ida-pro-mcp)
- [Claude Code MCP 문서](https://code.claude.com/docs/en/mcp)
