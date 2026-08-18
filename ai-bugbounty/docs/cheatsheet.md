# Cheatsheet — 치트시트 · 프롬프트 · 용어집

## 단계별로 자주 쓰는 명령

| 단계 | 명령 |
|---|---|
| **RECON 정찰** | `nmap -sV target`<br>`ffuf -w list -u URL/FUZZ`<br>`strings bin \| grep -i key` |
| **ANALYZE 분석** | `semgrep --config auto .`<br>`codeql database create db`<br>`/mcp connect ghidra` |
| **VERIFY 검증** | `afl-fuzz -i in -o out ./t`<br>`gdb -ex run --args ./t`<br>`valgrind ./t < poc` |
| **REPORT 제보** | `asan_symbolize < log`<br>최소화된 PoC 스크립트<br>`git diff > patch.txt` |

치트시트 활용법: 반복으로 익힘(외우지 말고 실습에서 자연히), 별칭 등록(긴 명령은 alias·스크립트로 단축), 기록 남기기(성공한 커맨드는 노트에 모아 재사용).

---

## 헌팅 프롬프트 4틀 (ROLE · CONTEXT · CHAIN · VERIFY)

```
[ROLE]    너는 취약점 분석가다. 추측 금지. 출력은 아래 JSON 스키마로만.
[CONTEXT] 대상: @src/parser/ 의 함수들. 진입점: recv_field, parse_packet.
          신뢰 경계: 네트워크 입력. 무관 코드(로깅/UI)는 제외.
[CHAIN]   1) 외부 입력이 닿는 함수를 먼저 추려라
          2) 각 입력의 도달 경로(source→sink)를 잇고 검증 유무를 표시
          3) 근거(파일:라인)와 함께 결론
[VERIFY]  각 후보에 대해: 실제 호출되는가? 공격자가 값을 제어하는가?
          상위에서 이미 검증하지 않는가? 재현 PoC 입력이 나오는가?
          하나라도 '아니오'면 미검증으로 강등. 없으면 '없다'고 답해라.
```

프롬프트에 꼭 넣는 4가지: **범위 · 형식 · 근거 · 실패 허용**.

---

## 자주 나오는 용어 한눈에

### MEMORY 메모리
- **RCE** · 원격 코드 실행
- **PoC** · 개념 증명 (Proof of Concept)
- **RIP** · 명령 포인터 (덮이면 실행 흐름 탈취)
- **canary** · 스택 보호값

### WEB 웹
- **IDOR** · 객체 참조 취약 (식별자 조작으로 타 사용자 자원)
- **SSRF** · 서버 요청 위조
- **CSP** · 콘텐츠 보안 정책
- **payload** · 공격 입력

### PROCESS 분석
- **taint** · 오염 추적 (신뢰 못 할 값의 전파)
- **sink** · 위험 함수 (오염된 값이 도달하면 취약)
- **fuzzing** · 무작위/변이 입력으로 크래시 탐색
- **triage** · 분류·선별

### AI · TOOL 도구
- **MCP** · 도구 연결 규약 (Model Context Protocol)
- **agent** · 자율 실행 AI (계획→실행→관찰 루프)
- **CWE** · 결함 분류 (유형)
- **CVSS** · 심각도 점수

약어에 겁먹지 말 것: 맥락으로 익힌다(실습 중 자연스럽게 손에 붙음) · 출발점 셋(RCE·PoC·CWE부터 확실히 알면 충분) · 리포트 필수어(심각도·재현·영향은 정확히 써야 함).

---

## source → sink 한 장 요약

```
[SOURCE]        [PROPAGATION]           [SINK]
recv/fopen/URL → sprintf/memcpy/concat → db_exec/system/memcpy
외부 입력 진입   값이 가공·전달되는 경로   위험하게 쓰이는 함수

질의: SOURCE의 값이 검증(sanitize) 없이 SINK까지 도달하는가?
→ 도달하면 후보. 도달 못 하면(죽은 코드/상위 검증) 오탐.
```

이 한 장이 SQLi · 명령 인젝션 · 경로 조작 · 버퍼 오버플로를 관통하는 공통 질문이다.
