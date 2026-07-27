# Crackme4 — 볼륨 라벨 기반 Keygenme 분석

실습자료 `Crack/Crackme4.exe` (8KB, PE32 GUI, abex 계열). 입력한 시리얼을 **드라이브 볼륨 라벨에서 계산한 정답**과 비교하는 keygenme. 정답이 프로그램 밖(드라이브 이름)에 묶여 있어, 코드/메모리를 안 바꿔도 라벨만 바꾸면 유효 시리얼이 달라진다.

## 식별

| 항목 | 값 |
|---|---|
| ImageBase / EP | `0x400000` / `0x401000` |
| 핵심 import | `GetVolumeInformationA`, `wsprintfA`, `lstrcatA`, `lstrcmpiA`, `GetDlgItemTextA` |
| 성공 문자열 | `Yep, you entered a correct serial!` |
| 실패 문자열 | `The serial you entered is not correct!` |
| 하드코딩 문자열 | `4562-ABEX` (0x4023F3), `L2C-5781` (0x4023FD) |

`GetVolumeInformationA` + `lstrcmpiA` 조합 → "드라이브 정보로 정답을 만들어 문자열 비교"하는 전형적 keygenme.

## 검증 루틴 디스어셈블 (Check 버튼, 0x40106C~)

```asm
; 1) 사용자 입력 읽기
0x40106C  push 0x25 / push 0x402324 / push 0x68 / push [ebp+8]
0x401078  call GetDlgItemTextA        ; 입력 → 0x402324 (최대 0x25바이트)

; 2) 볼륨 정보 얻기
0x40107D  push 0 / push 0 / push 0x4020C8 / push 0x402190
0x40108B  push 0x402194              ; arg4 lpVolumeSerialNumber (시리얼 → 0x402194)
0x401090  push 0x32 / push 0x40225C  ; arg2 lpVolumeNameBuffer (라벨 → 0x40225C)
0x401097  push 0                     ; arg1 lpRootPathName = NULL (실행 드라이브 루트)
0x401099  call GetVolumeInformationA

; 3) 라벨 + "4562-ABEX"
0x40109E  push 0x4023F3 (="4562-ABEX") / push 0x40225C
0x4010A8  call lstrcatA              ; 0x40225C = 볼륨라벨 + "4562-ABEX"

; 4) 앞 4바이트에 +2 (루프 2회)
0x4010AD  mov dl, 2
0x4010AF  add dword ptr [0x40225C], 1
0x4010B6  add dword ptr [0x40225D], 1
0x4010BD  add dword ptr [0x40225E], 1
0x4010C4  add dword ptr [0x40225F], 1
0x4010CB  dec dl
0x4010CD  jne 0x4010AF               ; 첫 4바이트 각각 +2

; 5) "L2C-5781" + 변환결과
0x4010CF  push 0x4023FD (="L2C-5781") / push 0x402000
0x4010D4  call lstrcatA              ; 0x402000 = "L2C-5781"
0x4010DE  push 0x40225C / push 0x402000
0x4010E8  call lstrcatA              ; 0x402000 += 변환된 버퍼

; 6) 비교
0x4010ED  push 0x402324 / push 0x402000
0x4010F7  call lstrcmpiA            ; 대소문자 무시 비교 (계산값 vs 입력)
0x4010FC  cmp eax, 0
0x4010FF  je  0x401117              ; 같으면 → "correct serial!"
```

## 알고리즘 (키젠 로직)

> **정답 = `"L2C-5781"` + ( (볼륨라벨 + `"4562-ABEX"`) 의 앞 4바이트에 각각 +2 )**

- 비교가 `lstrcmpiA`(대소문자 무시)라 케이스는 상관없다.
- `0x402194`에 받은 **볼륨 시리얼 번호는 쓰지 않는다 — 미끼.** 실제로 쓰는 건 볼륨 **라벨**(`0x40225C`).
- `lpRootPathName=NULL`이라 **크랙미가 실행되는 드라이브**의 라벨을 읽는다.
- +2 루프는 버퍼 앞 **4바이트만** 건드린다(라벨이 4자 미만이면 나머지가 `"4562"` 앞쪽으로 넘어간다).

### 키젠 (Python)

```python
def keygen(volume_label=""):
    b = bytearray(volume_label + "4562-ABEX", "latin1")
    for i in range(4):            # 앞 4바이트 +2
        b[i] = (b[i] + 2) & 0xFF
    return "L2C-5781" + b.decode("latin1")
```

### 라벨별 정답 예시

| 볼륨 라벨 | 정답 시리얼 |
|---|---|
| (없음) | `L2C-57816784-ABEX` |
| `TEST` | `L2C-5781VGUV4562-ABEX` |
| `HELLO` | `L2C-5781JGNNO4562-ABEX` |
| `SESAC` | `L2C-5781UGUCC4562-ABEX` |
| `ABCD` | `L2C-5781CDEF4562-ABEX` |

`SESAC` → 앞 4글자 `SESA`만 +2(알파벳 2칸): S→U, E→G, S→U, A→C = `UGUC`, 5번째 `C`는 그대로 → `UGUCC`.

## 푸는 방법 3가지

1. **런타임 읽기 (가장 확실)**: `0x4010F7`(lstrcmpiA)에 F2 BP → 아무 값 입력하고 Check → 덤프에서 `0x402000`을 보면 **내 PC의 정답 문자열**이 그대로 있다. 복사해서 입력.
2. **키젠 계산**: `vol` 명령으로 라벨 확인 → 위 공식/스크립트로 정답 산출.
3. **라벨 바꿔 다른 정답으로**: `label C: SESAC`(관리자) 후 재실행 → 정답이 `L2C-5781UGUCC4562-ABEX`로 바뀜. **코드·메모리 무수정**으로 유효 시리얼이 달라지는 게 이 크랙미의 핵심 포인트.

> 이 공식으로 만들 수 있는 시리얼은 `L2C-5781…4562-ABEX`(라벨 없으면 `…6784-ABEX`) 형태로 제한된다. 완전히 임의의 시리얼을 통과시키려면 라벨이 아니라 조건 분기(`0x4010FF je`)를 패치해야 한다.

## 배운 것

- **키 파일/드라이브 기반 인증**: 정답이 하드코딩이 아니라 환경(볼륨 라벨)에서 파생 → 정적 문자열 검색만으로는 안 나온다. `GetVolumeInformationA` 같은 환경 조회 API가 힌트.
- **미끼 필드**: 받아만 놓고 안 쓰는 값(볼륨 시리얼 0x402194)에 낚이지 말고, 실제로 비교에 흘러드는 버퍼(0x402000)를 추적.
- **비교 지점(lstrcmpiA)에 BP → 계산된 정답 덤프**가 keygenme 공략의 왕도. abex(Crackme2)의 문자열 추적과 같은 삼각형이다.
