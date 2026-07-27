# 안티 디버깅 기법 (Anti-Debugging)

교안 p128~141. 악성코드가 **분석가의 디버거를 탐지·방해**하는 기법 모음. 실습자료 Part 2 `Anti-Debugging/` 폴더의 번호별 바이너리가 각 기법에 대응한다. 아래 내용은 교안 원문과 실제 디스어셈블(특히 `9.Answer.exe`의 정답 코드)로 검증했다.

## 실습 바이너리 ↔ 기법 매핑

파일 번호는 교안 목차 번호와 일치한다(단 #4는 단독 파일 없음).

| 파일 | 교안# | 기법 | 검증 |
|---|---|---|---|
| `1.IDP.exe` | 1 | IsDebuggerPresent | API 호출 |
| `2.PEB.exe` | 2 | PEB.BeingDebugged 직접 읽기 | ✅ `fs:[0x30]→[eax+2]` |
| `3.NGF.exe` | 3 | NtGlobalFlag | ✅ `fs:[0x30]→[eax+0x68]`, `cmp 0x70` |
| (파일 없음) | 4 | CheckRemoteDebuggerPresent | 교안 |
| `5.FW.exe` | 5 | FindWindow | `FindWindowA` import |
| `6.RD.exe` | 6 | **Time Check (RDTSC)** — "RD"=RDtsc | ✅ `rdtsc … rdtsc; sub` |
| `7.DC.exe` | 7 | Dumb Code | 교안 |
| `8.FO.exe` | 8 | Fake Opcode | 교안 |
| `9.Exercise.exe` / `9.Answer.exe` | — | 종합 실습(빈 스텁 채우기) / 정답 | ✅ 9.Answer 디스어셈블 |

- `(fixed)` 접미사(`1.IDP(fixed)`, `5.FW(fixed)`)는 안티디버깅을 우회(패치)한 정답본. 원본과 diff하면 고친 바이트가 바로 보인다.
- `PEview.exe`는 PE 뷰어, `odbg110/`은 OllyDbg — 도구(샘플 아님).

## 기법별 원리와 우회

### 1) IsDebuggerPresent (1.IDP)

`kernel32!IsDebuggerPresent()`는 내부적으로 PEB의 `BeingDebugged` 바이트를 반환한다. `9.Answer.exe`의 해당 스텁:

```asm
0x40C000  call dword ptr [0x425144]  ; IsDebuggerPresent (IAT)
0x40C006  call 0x40B900              ; 결과(eax)로 판정 보고
0x40C00B  ret
```

**우회**: 반환값 분기를 뒤집거나 EAX를 0으로. 또는 PEB의 BeingDebugged를 0으로 패치(→ 2번과 동일 지점).

### 2) PEB.BeingDebugged 직접 읽기 (2.PEB)

API를 우회하려는 분석가를 다시 우회. `fs:[0x30]`으로 PEB 주소를 얻어 오프셋 `+2`(BeingDebugged)를 직접 읽는다. `9.Answer.exe` 정답:

```asm
0x40BD00  mov eax, dword ptr fs:[0x30]   ; PEB
0x40BD06  mov edx, dword ptr [eax+2]     ; PEB.BeingDebugged
0x40BD09  xor eax, eax
0x40BD0B  mov al, dl                     ; al = BeingDebugged (디버깅 중이면 1)
0x40BD0D  call 0x40B900                  ; 판정 보고
0x40BD12  ret
```

**우회**: 런타임에 PEB `+2` 바이트를 0으로 수정. `2.PEB.exe` 단독본도 같은 `fs:[0x30]→[eax+2]` 패턴이다.

### 3) NtGlobalFlag (3.NGF)

디버거로 프로세스를 띄우면 힙 관련 플래그가 세팅된다. PEB 오프셋 `+0x68`(x86)의 `NtGlobalFlag`가 `0x70`이면 디버깅 중. `9.Answer.exe` 정답:

```asm
0x40BF00  mov eax, dword ptr fs:[0x30]
0x40BF06  mov eax, dword ptr [eax+0x68]  ; NtGlobalFlag
0x40BF09  cmp eax, 0x70                  ; 0x70 = 디버깅 중
0x40BF0C  je  0x40BF15
0x40BF0E  mov eax, 0                     ; 정상
0x40BF13  jmp 0x40BF1A
0x40BF15  mov eax, 1                     ; 탐지됨
0x40BF1A  call 0x40B900
0x40BF1F  ret
```

`0x70`의 정체(교안 p134) — 디버깅 시 켜지는 힙 검사 플래그 3개의 합:

| 플래그 | 값 |
|---|---|
| FLG_HEAP_ENABLE_TAIL_CHECK | 0x10 |
| FLG_HEAP_ENABLE_FREE_CHECK | 0x20 |
| FLG_HEAP_VALIDATE_PARAMETERS | 0x40 |
| **합계** | **0x70** |

**우회**: PEB `+0x68`을 0으로 패치.

### 4) CheckRemoteDebuggerPresent (단독 파일 없음)

교안 p135. `kernel32!CheckRemoteDebuggerPresent()`는 내부적으로 `ZwQueryInformationProcess()`를 `ProcessDebugPort`로 호출한다. **DebugPort 값이 0이 아니면** 디버거가 붙어 있는 것. 다른 프로세스가 자신을 디버깅 중인지 커널에 질의하는 방식이라 PEB 패치로는 못 막고, API 반환값/`DebugPort` 결과 분기를 패치해야 한다.

### 5) FindWindow (5.FW)

디버거 **창 클래스명**을 찾아 탐지. `user32!FindWindowA("OLLYDBG", 0)` 등이 NULL이 아니면 디버거 실행 중.

```asm
push 0
push "OLLYDBG"        ; 또는 "WinDbgFrameClass" 등
call FindWindowA
test eax, eax
jnz  detected
```

**우회**: 분기 패치, 또는 디버거 창 클래스명 변경.

### 6) Time Check — RDTSC (6.RD)

교안 p137. 코드 두 지점 A→B의 실행 시간을 잰다. 디버거로 싱글스텝하면 사람이 개입하는 만큼 시간차가 비정상적으로 커지는 걸 이용. 이 코스는 `rdtsc`(타임스탬프 카운터 읽기)로 구현한다. `9.Answer.exe`에서 이 rdtsc가 종합 체크의 **바깥 프레임**을 이룬다:

```asm
0x40BB00  rdtsc                     ; 시작 시각 (EDX:EAX)
0x40BB02  push edx                  ; 시작값 저장
0x40BB03  call 0x40BD00             ; PEB 체크
0x40BB08  ...  call 0x40BF00        ; NtGlobalFlag 체크
0x40BB12  ...  call 0x40C000        ; IsDebuggerPresent 체크
0x40BB21  rdtsc                     ; 끝 시각
0x40BB23  sub  edx, dword ptr [esp] ; 시간차 = 끝 - 시작
```

시간차가 임계값보다 크면(=중간에서 싱글스텝/브레이크로 지연됨) 디버깅으로 판단.

**우회**: 두 rdtsc 사이를 `F9`로 한 번에 통과(싱글스텝 금지), 또는 시간차 비교 분기를 패치, 또는 두 번째 rdtsc 결과를 첫 값과 같게 조작.

### 7) Dumb Code (7.DC)

교안 p138. 의미 없는 **쓰레기 코드**를 끼워 넣어 분석 흐름과 가독성을 흐트러뜨리는 기법. 실행에는 영향이 없지만 분석가가 진짜 로직을 찾기 어렵게 만든다.

**우회**: 실제 데이터 흐름에 영향을 주는 명령만 추려서 읽기. 무의미 연산은 무시.

### 8) Fake Opcode (8.FO)

교안 p139. 정상 명령어 스트림 중간에 **가짜 바이트**를 넣어 선형 디스어셈블러(linear sweep)를 오정렬시킨다. 디스어셈블러는 엉뚱하게 해석하지만, 실제 실행은 `jmp`로 그 가짜 바이트를 건너뛰어 정상 동작. IDA/x32dbg의 자동 분석이 깨지도록 유도한다.

**우회**: 실제 실행 경로를 따라 수동으로 코드 재정렬, 가짜 바이트를 NOP/데이터로 표시(x32dbg에서 해당 영역 우클릭 → Analyze 재실행).

## 9. Exercise / Answer — 종합 실습

`9.Exercise.exe`는 위 기법들을 **빈 스텁으로 남겨둔 채워 넣기 과제**다. 각 체크 함수가 `ret`만 있고, 학생이 안티디버그 로직을 구현해야 한다.

### 구조 (교안 p141 + 검증)

| 주소 | 역할 | Exercise(빈칸) | Answer(정답) |
|---|---|---|---|
| `0x40BB00` | Time Check(rdtsc) 드라이버 | rdtsc + 하위 체크 call | rdtsc 2회로 시간차 측정 |
| `0x40BD00` | PEB 체크 | `ret` | `fs:[30]→[+2]` |
| `0x40BF00` | NtGlobalFlag 체크 | `ret` | `[+0x68] cmp 0x70` |
| `0x40C000` | IsDebuggerPresent 체크 | `ret` | `call [IAT]` |
| `0x40B900` | 판정 보고 | eax 플래그 평가 | (공통) |

### 판정 로직 (0x40B900)

```asm
0x40B900  cmp eax, 0
0x40B903  je  0x40B914          ; eax==0 → 정상
0x40B905  push 0x420024         ; "디버깅 당함"
0x40B90A  call 0x4010C0         ; printf
...
0x40B914  push 0x42001C         ; "정상"
0x40B919  call 0x4010C0
```

각 체크 함수는 탐지 시 `eax=1`로 설정하고 `0x40B900`을 호출한다. 하나라도 1이면 `"디버깅 당함"`, 전부 0이면 `"정상"`이 출력된다.

## 직접 구현 실습 (9.Exercise 빈 스텁 채우기)

`9.Exercise.exe`의 각 체크는 `ret`만 있는 빈 함수다. x32dbg에서 각 주소로 `Ctrl+G` 이동 → 스페이스바로 어셈블해 **탐지 로직을 직접 작성**한다. 규칙은 하나: **디버거를 탐지하면 `eax=1`, 아니면 `eax=0`으로 만들고 `call 0x40B900`(판정 보고)** 을 부른 뒤 `ret`.

### 준비

1. `9.Exercise.exe`를 x32dbg로 로드(디버거로 열어야 탐지가 의미 있음).
2. 아래 각 스텁 주소로 `Ctrl+G` 이동 후 작성. 어셈블 창 "Fill with NOP's" 켜두기(빈 공간이 넉넉해 안전).

### ① PEB.BeingDebugged 체크 — 0x40BD00

PEB의 `+2` 바이트가 곧 "디버깅 여부"다. 그대로 eax에 담아 보고하면 된다.

```asm
0x40BD00  mov eax, dword ptr fs:[0x30]   ; PEB 주소
0x40BD06  mov edx, dword ptr [eax+2]     ; BeingDebugged (0/1)
0x40BD09  xor eax, eax
0x40BD0B  mov al, dl                     ; eax = 탐지 플래그
0x40BD0D  call 0x40B900                  ; 판정 보고
0x40BD12  ret
```

왜: BeingDebugged는 디버거가 붙으면 1이 되는 바이트라, 별도 비교 없이 그 값이 곧 탐지 결과다.

### ② NtGlobalFlag 체크 — 0x40BF00

PEB `+0x68`이 `0x70`이면 디버깅 중. 같으면 eax=1, 아니면 0.

```asm
0x40BF00  mov eax, dword ptr fs:[0x30]
0x40BF06  mov eax, dword ptr [eax+0x68]  ; NtGlobalFlag
0x40BF09  cmp eax, 0x70                  ; 힙 체크 플래그 합(0x10+0x20+0x40)
0x40BF0C  je  0x40BF15
0x40BF0E  mov eax, 0                     ; 정상
0x40BF13  jmp 0x40BF1A
0x40BF15  mov eax, 1                     ; 탐지
0x40BF1A  call 0x40B900
0x40BF1F  ret
```

왜: BeingDebugged와 달리 값이 0/1이 아니라 플래그 비트라, `0x70`과 비교해서 0/1로 정규화한 뒤 보고한다.

### ③ IsDebuggerPresent 체크 — 0x40C000

API가 알아서 PEB를 읽어 0/1을 반환하므로 그대로 보고.

```asm
0x40C000  call dword ptr [<IsDebuggerPresent IAT>]   ; 반환값 eax = 0/1
0x40C006  call 0x40B900
0x40C00B  ret
```

`<IsDebuggerPresent IAT>` 슬롯은 x32dbg가 `<&IsDebuggerPresent>`로 자동 라벨링해준다(9.Answer 기준 `0x425144`). Symbols 탭이나 어셈블 창에서 `call dword ptr [<&IsDebuggerPresent>]`로 그대로 입력해도 된다.

### ④ Time Check(RDTSC) 완성 — 0x40BB00

드라이버는 이미 시작 `rdtsc`와 세 체크 호출이 있다. **끝 지점에 두 번째 rdtsc를 찍고 시간차를 구하는 부분**을 완성한다.

```asm
0x40BB00  rdtsc                     ; 시작 시각 (이미 있음)
0x40BB02  push edx
          ... call 0x40BD00 / 0x40BF00 / 0x40C000 (세 체크) ...
0x40BB21  rdtsc                     ; 끝 시각 (직접 추가)
0x40BB23  sub edx, dword ptr [esp]  ; 시간차 = 끝 - 시작
          ; 시간차가 임계값보다 크면 eax=1 로 보고하도록 분기 추가
```

왜: 싱글스텝/브레이크로 지연되면 두 rdtsc 차이가 폭발한다. 그 차이를 임계값과 비교해 탐지로 판단한다.

### ⑤ 검증

- 작성 후 `F9`로 실행 → **디버거가 붙어 있으니** 각 체크가 1을 보고 → `"디버깅 당함"` 출력이 정상(=탐지 로직이 동작).
- 반대로 디버거 없이 그냥 실행하면 `"정상"`이 떠야 한다.
- 한 스텁씩 작성하며 테스트하면 어느 체크가 동작/미동작인지 바로 확인된다.

> 이 과정이 곧 "안티디버깅을 **만드는**" 실습이다. 반대로 이걸 **우회**하는 연습은 아래 워크플로우로 이어진다(내가 짠 탐지를 스스로 무력화해보기).

## 공통 우회 워크플로우 (x32dbg)

1. **BP on API**: `IsDebuggerPresent`, `FindWindowA`에 BP(Symbols 탭/Intermodular calls). 호출 직후 반환값 분기를 확인.
2. **분기 뒤집기**: `test eax,eax` 다음 `jnz detected`에서 플래그(Z)를 수동 토글하거나 명령어 패치.
3. **PEB 직접 수정**: API를 안 쓰는 2·3번은 PEB의 `+2`(BeingDebugged), `+0x68`(NtGlobalFlag)을 메모리에서 0으로.
4. **RDTSC 우회**: 두 rdtsc 구간을 싱글스텝하지 말고 `F9`로 통과, 시간차 분기 패치.
5. **(fixed) 대조**: 정답본과 원본을 바이트 diff해 패치 위치를 역으로 학습.
6. **플러그인**: ScyllaHide 같은 안티-안티디버그 플러그인이 위 항목을 자동 처리(교안은 수동 실습 권장).

## 정리

안티디버깅은 "탐지 → 분석가가 우회 → 더 낮은 레이어에서 재탐지"의 반복이다. `IsDebuggerPresent`(API) → PEB 직접 읽기 → NtGlobalFlag → rdtsc 타이밍 순으로 **점점 저수준으로 내려간다.** 결국 대부분의 탐지가 PEB의 몇 개 필드(BeingDebugged, NtGlobalFlag)와 타이밍으로 수렴하므로, PEB 구조와 rdtsc 원리를 알면 우회할 수 있다.
