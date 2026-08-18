# Bug Bounty with AI agent — 정리 노트

> "토큰 주면 0-day 찾아오는 AI"
> Find the Gap · 강사 김종혁 (Offensive Security Researcher) · 2026.08.07

AI 에이전트를 실제 버그바운티 헌팅에 붙이는 2일 16시간 과정의 정리본입니다. 개념은 요약 위주로, 도구 연결·실습 절차는 따라 할 수 있게 정리했습니다. 우리가 직접 세팅한 **Windows IDA ↔ Kali MCP 연동 가이드**도 [`setup/`](setup/)에 포함돼 있습니다.

---

## 이 과정의 핵심 한 줄

> **AI는 "찾기"를 대신하는 게 아니라 "코드 읽는 시간"을 줄여 준다. 그래서 그만큼 "검증하고 재현하는 시간"이 늘어난다.**
> 취약 여부·심각도의 최종 판단과 제보 책임은 언제나 사람에게 있다. AI는 후보를 좁히는 증폭기일 뿐, 재현된 것만 취약점이라고 부른다.

## 커리큘럼 한눈에

| 구간 | 주제 | 핵심 |
|---|---|---|
| **Day 1 AM** | 기초와 원리 | 버그바운티 제도·생태계, Scope·트리아지, 수작업 헌팅 4단계 |
| **Day 1 PM** | 취약점 기초 | 메모리 손상 4계열, 웹·로직 취약점, CWE·CVE·CVSS |
| **Day 2 AM** | 에이전트 실전 | MCP 도구 연결, 하네스·루프·그래프, 프롬프트 설계, 크래시 트리아지 |
| **Day 2 PM** | 실습과 운영 | nProtect 대상 실습, 무인 탐색 자동화, 리포트 작성·제출 |

시간 배분: **이론 40% · 실습 50% · 공유 10%**

---

## 목차 (섹션별 정리)

1. [취약점 기초 — Vulnerability Basics](docs/01-vulnerability-basics.md)
   메모리 손상 4계열, 웹·로직 취약점, CWE·CVE·CVSS
2. [Old Bug Bounty — AI 없이 하던 방식](docs/02-old-bug-bounty.md)
   수작업 헌팅 4단계, Scope·법적 경계, 플랫폼, 트리아지
3. [New Bug Bounty — AI를 붙이면](docs/03-new-bug-bounty.md)
   AI가 코드를 읽는 법, MCP, 챗봇 vs 에이전트, 컨텍스트·환각, 벤치마크
4. [Hands-on Hunting — 도구 체인 실전](docs/04-hands-on-hunting.md)
   RAPTOR 워크플로, 정적·동적·퍼징 도구, 하네스·루프·그래프 엔지니어링
5. [Reporting & Ops — 제보와 운영](docs/05-reporting-and-ops.md)
   통과하는 리포트, 무인 자동화, 토큰 예산, AI의 한계, 실제 제보 사례
6. [Cheatsheet — 치트시트·프롬프트·용어집](docs/cheatsheet.md)
   단계별 명령, 헌팅 프롬프트 4틀, 자주 나오는 용어

## 실습 환경 (setup)

- [IDA-MCP-Kali-연동.md](setup/IDA-MCP-Kali-연동.md) — Windows IDA Pro ↔ Kali(게스트 VM) MCP 연동 실전 가이드
- [start-ida-mcp.bat](setup/start-ida-mcp.bat) — IDA 실행 + 방화벽 + 접속 IP 안내 배치 스크립트
- [ida_mcp_diag.py](setup/ida_mcp_diag.py) — 플러그인이 안 뜰 때 원인 진단 스크립트

### 실습 환경 준비 체크리스트

| 구분 | 항목 |
|---|---|
| 계정·권한 | Claude/OpenAI API 키, HackerOne 계정, GitHub 계정, 실습용 격리 VM |
| 분석 도구 | Ghidra 11.x, IDA Free/Pro, Burp Suite Community, x64dbg·gdb+pwndbg |
| 에이전트 환경 | Claude Code CLI, Codex CLI(선택), MCP 서버 3종, Docker Desktop |
| 스캔·퍼징 | Semgrep CLI, CodeQL CLI, AFL++ 컨테이너, **Python 3.11 이상** |

> 시작 전 3가지: ① MCP 서버가 로컬 포트를 쓰므로 방화벽 예외 확인 ② 컨테이너·코퍼스 때문에 디스크 최소 40GB ③ 실습은 반드시 VM/컨테이너 안에서만.

---

## 더 배우기

- 문서: 각 도구 공식 docs·튜토리얼
- 리포트: HackerOne Hacktivity, GitHub Advisory
- 훈련: CTF, pwn.college, 워게임
- 레포: ExploitGym·CyberGym 공개 하네스

습관: 매주 공개 라이트업 한 편 정독 · 읽은 취약점은 직접 재현 · 배운 것은 노트/글로 기록.

---

*본 정리본은 강의 슬라이드(FTG "Bug Bounty with AI agent" ver.1, 107p)를 학습용으로 재구성한 것입니다. 슬라이드 내 수치·벤치마크(예: CyberGym/ExploitGym 점수, 보상 금액대)는 강의 시점 예시이며, 실제 값은 원 출처에서 확인하세요.*
