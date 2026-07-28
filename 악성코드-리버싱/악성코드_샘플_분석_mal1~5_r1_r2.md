# 악성코드 샘플 정적 분석 — mal1~5 / r1~r2

> **분석 방법**: 정적 분석 (실행 없음)  
> **도구**: PE 헤더 파싱(pefile), strings, 섹션 엔트로피, import 테이블  
> **환경**: 격리된 Linux 분석 환경

---

## 샘플 개요

| 파일 | 크기 | 아키텍처 | 서브시스템 | 패커 | 유형 |
|---|:-:|:-:|:-:|:-:|---|
| mal1.exe | 11 KB | x86 | Console | 없음 | 배경화면 변경 |
| mal2.exe | 10.5 KB | x86 | Console | 없음 | 브라우저 북마크 하이재킹 |
| mal3.exe | 7.5 KB | x86 | GUI | UPX 3.03 | 키로거 + C2 전송 |
| mal4.exe | 101 KB | x86 | GUI | 없음 | 스크린샷 캡처 |
| mal5.exe | 32 KB | x86 | Console | UPX 3.03 | 랜섬웨어 |
| r1.exex | 31.5 KB | x86 | GUI | 없음 | CryptoShield 랜섬웨어 |
| r2.exex | 993 KB | x64 | Console | 없음 | 키로거 |

> **r1.exex / r2.exex** — `.exex` 확장자로 이름을 바꿔 실행 차단을 우회하려는 흔적

---

## §1 mal1.exe — 배경화면 변경 악성코드 (Wallpaper Changer)

### PE 기본 정보

| 항목 | 값 |
|---|---|
| MD5 | `1172c4410eb5d9780b0c58b2e9336a65` |
| EntryPoint | `0x4014FB` |
| ImageBase | `0x400000` |
| PDB 경로 | `C:\Users\user\source\repos\mal1\Release\mal1.pdb` |

### 섹션 엔트로피

| 섹션 | 엔트로피 | 비고 |
|---|:-:|---|
| .text | 6.09 | 정상 코드 범위 |
| .rdata | 4.23 | 문자열/상수 |
| .data | 1.71 | 낮음 (초기화 데이터) |

### 핵심 Import

```
urlmon.dll      → URLDownloadToFileW       ← 인터넷에서 파일 다운로드
USER32.dll      → SystemParametersInfoW   ← 배경화면 변경 (SPI_SETDESKWALLPAPER)
SHELL32.dll     → SHGetFolderPathW        ← 특수 폴더 경로 획득
ole32.dll       → CLSIDFromString         ← COM 초기화
gdiplus.dll     → GdipCreateBitmapFromFile, GdipSaveImageToFile  ← 이미지 처리
KERNEL32.dll    → DeleteFileW             ← 파일 삭제 (흔적 제거)
```

### 악성 문자열

```
https://elm.umaryland.edu/elm-stories/2023/Hacked.jpg   ← 다운로드 URL
\hacked_image.jpg                                        ← 임시 저장 경로
\hacked_image.bmp                                        ← BMP 변환 후 경로
```

### 동작 흐름

```
1. SHGetFolderPathW → 사용자 홈/TEMP 폴더 경로 획득
2. URLDownloadToFileW → "Hacked.jpg" 다운로드 → \hacked_image.jpg 저장
3. GdipCreateBitmapFromFile → JPG 로드
4. GdipSaveImageToFile → BMP 형식으로 변환 저장 (\hacked_image.bmp)
   (배경화면은 BMP 형식만 직접 지원하는 경우 많음)
5. SystemParametersInfoW(SPI_SETDESKWALLPAPER, ...) → 배경화면 교체
6. DeleteFileW → 원본 JPG 삭제 (흔적 제거)
```

### 분류 및 특징

- **안티디버깅**: `IsDebuggerPresent` 임포트 확인 → 디버거 탐지 로직 포함 가능성
- **PDB 경로**: 개발자 경로(`mal1`) 노출 → 테스트/학습용 샘플로 추정
- **실제 위협도**: 낮음 (파일 파괴 없음, 배경화면만 변경)

---

## §2 mal2.exe — 브라우저 북마크 하이재킹 (Bookmark Hijacker)

### PE 기본 정보

| 항목 | 값 |
|---|---|
| MD5 | `a396a54d6718f584c559b185015daffd` |
| EntryPoint | `0x401788` |
| 섹션 엔트로피 | .text: 6.16 / .data: 4.99 (정상) |

### 핵심 Import

```
KERNEL32.dll  → FindFirstFileA, FindNextFileA, FindClose  ← 파일 탐색
              → Sleep                                      ← 지연 실행
              → IsDebuggerPresent                         ← 안티디버깅
CRT           → fopen, fclose, fputs, system              ← 파일 I/O + 명령 실행
              → getenv                                     ← 환경변수 읽기
              → strstr                                     ← 문자열 검색
```

### 악성 문자열

```
LOCALAPPDATA                                 ← 환경변수로 Chrome 경로 찾기
\Google\Chrome\User Data                     ← Chrome 프로필 루트
%s\Bookmarks                                 ← 북마크 파일 경로 포맷
[+] All Chrome profiles processed            ← 성공 로그
[-] Failed to open %s                        ← 실패 로그
taskkill /F /IM chrome.exe /T > NUL 2>&1    ← Chrome 강제 종료
```

### 삽입되는 악성 북마크 JSON

```json
{
  "name": "Instagram Login",
  "type": "url",
  "url": "https://raw.githubusercontent.com/laisfrigerio/instagram-clone-login-page/..."
}
```
→ 사용자가 북마크 클릭 시 **Instagram 피싱 페이지**로 이동

### 동작 흐름

```
1. getenv("LOCALAPPDATA") → Chrome 경로 구성
2. FindFirstFileA → "User Data\Profile*" 탐색 (다중 프로필 처리)
3. system("taskkill /F /IM chrome.exe /T > NUL 2>&1")
   → Chrome이 켜있으면 Bookmarks 파일 잠김 → 강제 종료
4. fopen(Bookmarks 경로, "w") → 악성 북마크 JSON으로 덮어씀
5. [+] All Chrome profiles processed 출력
```

### 분류 및 특징

- **피싱 전달 수단**: 파일 자체에 피싱 URL 하드코딩
- **다중 프로필 지원**: `Profile 1`, `Profile 2`... 모두 탐색
- `Sleep` 사용 → 재감염 루프 또는 탐지 회피 지연 가능성
- **실제 위협도**: 중간 (크리덴셜 탈취 목적 피싱)

---

## §3 mal3.exe — 키로거 + C2 전송 (UPX 패킹)

### PE 기본 정보

| 항목 | 값 |
|---|---|
| MD5 | `fce3e7d8d02a2a5dc8b1d3a3f40b8f7d` |
| 패커 | UPX 3.03 |
| UPX1 엔트로피 | **7.46** (높음 — 압축 데이터) |
| 서브시스템 | GUI (콘솔 창 숨김) |

### 섹션 구조

| 섹션 | VirtualSize | RawSize | 엔트로피 | 의미 |
|---|:-:|:-:|:-:|---|
| UPX0 | 0x6000 | 0x0 | 0.00 | 언팩 후 코드가 로드될 영역 |
| UPX1 | 0x2000 | 0x1400 | **7.46** | 압축된 실제 코드 |
| .rsrc | 0x1000 | 0x600 | 3.99 | 리소스 |

### 핵심 Import (UPX 스텁 기준)

```
KERNEL32.DLL  → LoadLibraryA, GetProcAddress   ← 동적 API 로딩 (숨기기)
              → VirtualAlloc, VirtualProtect    ← 메모리에 코드 복호화/실행
USER32.dll    → ToAscii                         ← 키코드 → 문자 변환 (키로거)
WININET.dll   → InternetOpenA                   ← HTTP 연결 (C2 통신)
```

### 악성 문자열 (부분 복원)

```
https://eoinm[...].pipedream.net   ← C2 서버 (pipedream.net = serverless webhook)
Mozilla/5.0OA                       ← HTTP User-Agent 위장
5~sHook&                            ← 키보드 훅 관련 (SetWindowsHookEx 추정)
Keybo[ard]                          ← 키보드 후킹 대상
BCDEFGHIJKLMNOPQRSTUVWXYZabcdefg  ← 문자 매핑 테이블 (키로거 출력 변환)
```

### 동작 흐름 (추정)

```
1. UPX 스텁: VirtualAlloc → UPX1 데이터 복호화 → UPX0 영역에 적재
2. 실제 페이로드 실행:
   a. SetWindowsHookEx(WH_KEYBOARD_LL, ...) → 글로벌 키보드 후킹
   b. GetMessage 루프 → 키입력 감지
   c. ToAscii → 키코드를 문자로 변환
   d. InternetOpenA → pipedream.net C2로 HTTP POST 전송
3. GUI 창 없이 백그라운드 동작 (Subsystem=GUI로 콘솔 창 숨김)
```

### 분류 및 특징

- **C2**: pipedream.net — 정상 서비스를 C2로 악용 (Living off the Land)
- **UPX 패킹** → 정적 분석 방해, 시그니처 우회
- `LoadLibraryA` + `GetProcAddress` → 임포트 테이블에 API 숨김 (동적 로딩)
- **실제 위협도**: 높음 (실시간 키입력 탈취 + 외부 전송)

---

## §4 mal4.exe — 스크린샷 캡처 악성코드 (Screenshot Stealer)

### PE 기본 정보

| 항목 | 값 |
|---|---|
| MD5 | `47b3ff271fa088eaa3d8fbb5cb40c43b` |
| .rsrc 크기 | 94 KB (전체 101 KB 중 대부분) |
| .rsrc 엔트로피 | 4.03 (낮음 — 그림/텍스트 리소스 가능) |

### 핵심 Import

```
USER32.dll   → GetDC, GetSystemMetrics, ReleaseDC         ← 화면 DC 획득
GDI32.dll    → CreateCompatibleDC, CreateCompatibleBitmap ← 오프스크린 DC 생성
             → BitBlt                                      ← 화면 복사 (핵심 API)
             → GetDIBits                                   ← 픽셀 데이터 추출
KERNEL32.dll → GetLocalTime                                ← 타임스탬프 생성
             → CreateDirectoryA, GlobalAlloc/Lock/Unlock   ← 저장 경로/메모리
CRT          → fopen, fwrite, fclose                       ← BMP 파일 저장
```

### 악성 문자열

```
C:\temp                               ← 저장 디렉터리 (하드코딩)
C:\temp\%04d%02d%02d_%02d%02d%02d.bmp  ← 파일명 형식: 날짜시간.bmp
                                         예) C:\temp\20260728_143022.bmp
```

### 동작 흐름

```
1. CreateDirectoryA("C:\temp") → 저장 폴더 생성
2. GetDC(NULL) → 전체 화면 DC 획득
3. GetSystemMetrics(SM_CXSCREEN/SM_CYSCREEN) → 화면 해상도
4. CreateCompatibleDC + CreateCompatibleBitmap → 오프스크린 버퍼
5. BitBlt → 화면 내용을 버퍼에 복사 (스크린샷)
6. GetDIBits → 픽셀 배열 추출
7. GetLocalTime → 현재 날짜/시간 획득
8. fopen("C:\temp\날짜시간.bmp", "wb") + fwrite → BMP 파일 저장
9. 루프 → 주기적으로 반복 캡처
```

### 분류 및 특징

- **저장 위치 하드코딩**: `C:\temp` — 단순 구현, 탐지 쉬움
- C2 통신 import 없음 → **로컬 저장 전용** (별도 exfil 도구와 조합 사용 추정)
- **실제 위협도**: 중간 (스파이웨어, 기업 정보 탈취에 활용 가능)

---

## §5 mal5.exe — 랜섬웨어 (UPX 패킹)

### PE 기본 정보

| 항목 | 값 |
|---|---|
| MD5 | `fb047055b1c1ee5ca751e69a89835b62` |
| 패커 | UPX 3.03 |
| UPX1 엔트로피 | **7.81** (매우 높음) |
| 서브시스템 | Console |

### 핵심 Import (스텁)

```
KERNEL32.DLL  → VirtualAlloc, VirtualProtect, VirtualFree ← 언팩 + 코드 실행
              → LoadLibraryA, GetProcAddress               ← 동적 API 로딩
ADVAPI32.dll  → CryptEncrypt                               ← 파일 암호화 ★
USER32.dll    → SystemParametersInfoA                      ← 배경화면 변경 (랜섬 노트)
CRT           → fopen, strcat_s                            ← 파일 열기 + 경로 조합
```

### 악성 문자열 (부분 복원, 난독화)

```
CryptAcquireCo[ntext]   ← 암호화 컨텍스트 초기화 (난독화됨)
yKey D[erive]           ← CryptDeriveKey (키 파생, 난독화)
CryptEncrypt            ← 파일 암호화 실행
SystemParametersInfoA   ← 배경화면 변경 (랜섬 메시지 이미지)
```

### 동작 흐름 (추정)

```
1. UPX 스텁 → 언팩 후 실제 코드 실행
2. CryptAcquireContext → 암호화 프로바이더 초기화
3. CryptDeriveKey → 암호화 키 생성
4. fopen + 파일 탐색 → 대상 파일 순회
5. CryptEncrypt → 파일 내용 암호화 (확장자 변경 추정)
6. SystemParametersInfoA(SPI_SETDESKWALLPAPER) → 배경화면을 랜섬 메시지 이미지로 변경
```

### 분류 및 특징

- **Windows CryptoAPI 사용** (`ADVAPI32.dll`) → 비교적 단순한 대칭 암호화
- 문자열 난독화 (`CryptAcquireCo[bxt]` 등) → 정적 분석 방해
- UPX + 동적 API 로딩 → 이중 분석 방어
- **실제 위협도**: 높음 (파일 암호화 + 피해자에게 메시지)

---

## §6 r1.exex — CryptoShield 1.0 랜섬웨어

### PE 기본 정보

| 항목 | 값 |
|---|---|
| MD5 | `35a11b95c0349b1eccf4f1e1902d9a94` |
| 아키텍처 | x86 (PE32) |
| 서브시스템 | GUI |
| 컴파일 시각 | `0x5890976F` (2017년경) |

### 핵심 Import

```
ADVAPI32.dll  → CryptGenKey, CryptDeriveKey      ← RSA-2048 키 쌍 생성
              → CryptEncrypt, CryptExportKey      ← 파일 암호화, 공개키 내보내기
              → GetUserNameW                       ← 피해자 식별
              → RegSetValueExW, RegFlushKey       ← 레지스트리 지속성 등록
WININET.dll   → InternetConnectA, HttpOpenRequestA, HttpSendRequestA ← C2 통신
WS2_32.dll    → socket, connect, gethostbyname   ← 직접 소켓 C2 통신
SHELL32.dll   → ShellExecuteW                    ← 랜섬 노트 실행
```

### 랜섬 노트 (내장 HTML)

```
All of your files were encrypted by a strong encryption with RSA-2048 using CryptoShield 1.0.

Contact us by email:
  restoring_sup@india.com          ← 주 이메일
  restoring_sup@computer4u.com     ← 예비 이메일 1
  restoring_reserve@india.com      ← 예비 이메일 2

Decrypting of your files is only possible with the help of the private key and
decrypt program, which is on our secret server.

-----BEGIN PRIVATE KEY-----  (표시용 가짜 키)
-----END PRIVATE KEY-----
```

### C2 통신

```
HTTP POST → /test_site_scripts/moduls/traffic/get_info.php
Content-Type: application/x-www-form-urlencoded
→ 피해자 PC 정보, 사용자명, 고유 ID 전송
```

### 동작 흐름

```
1. GetUserNameW → 피해자 식별자 생성
2. CryptGenKey(RSA-2048) → 공개키/개인키 쌍 생성
3. CryptExportKey → 공개키를 C2로 전송 (개인키는 서버만 보유)
4. 파일 시스템 순회 → CryptEncrypt로 파일 암호화
5. ShellExecuteW → 랜섬 노트 HTML 브라우저로 열기
6. RegSetValueExW → 재부팅 후에도 실행되도록 레지스트리 등록
7. HttpSendRequestA → C2에 감염 보고
```

### 분류 및 특징

- **실제 알려진 악성코드**: CryptoShield 1.0 (2017년 활성)
- **RSA-2048 비대칭 암호화** → 개인키 없이 복호화 불가
- **3개 이메일** 등록 → 하나가 폐쇄돼도 대응 가능하게 설계
- **C2 + 소켓** 이중 통신 경로
- **실제 위협도**: 매우 높음 (실제 피해 발생한 랜섬웨어 패밀리)

---

## §7 r2.exex — 키로거 (x64, 오픈소스 기반)

### PE 기본 정보

| 항목 | 값 |
|---|---|
| MD5 | `61651bb3669b41a414ad141d614a06fc` |
| 아키텍처 | **x64 (PE32+)** |
| 서브시스템 | Console |
| 컴파일러 | MinGW (GCC for Windows) |
| 소스 경로 | `C:\Users\Rishabh\Desktop\project\keylogger.c` |

### 핵심 Import

```
USER32.dll    → GetAsyncKeyState   ← 키 상태 폴링 방식 키로거 ★
              → GetKeyState         ← 보조 키 상태 (Shift, Caps 등)
              → FindWindowA         ← 활성 창 제목 확인
              → ShowWindow          ← 콘솔 창 숨기기
KERNEL32.dll  → AllocConsole        ← 콘솔 창 생성/관리
```

### 악성 문자열

```
Keylogs.txt          ← 키입력 저장 파일명
isKeyListed          ← 함수명 (특정 키 필터링 여부 확인)
vKey, cur_key        ← 내부 변수명 (가상 키코드)
keylogger.c          ← 소스 파일명 노출
```

### 동작 흐름

```
1. ShowWindow(SW_HIDE) → 콘솔 창 숨김
2. 무한 루프:
   a. GetAsyncKeyState(vKey) 0x00~0xFF 순회 → 눌린 키 감지
   b. GetKeyState(VK_SHIFT) → 대소문자 판별
   c. FindWindowA(NULL, NULL) → 현재 활성 창 제목 기록
   d. fopen("Keylogs.txt", "a") → 키입력 추가 저장
```

### 분류 및 특징

- **폴링 방식** (`GetAsyncKeyState`) — 훅 방식보다 단순하지만 탐지 우회 가능
- **소스 경로 노출** → 오픈소스/학습용 기반 (GitHub keylogger 프로젝트 추정)
- **정적 링크** → 별도 DLL 없이 독립 실행 (993 KB 중 대부분이 MinGW 라이브러리)
- C2 없음 → **로컬 저장 전용** (`Keylogs.txt`)
- **실제 위협도**: 중간 (지속 실행 시 모든 키입력 수집)

---

## §8 종합 비교

### 악성 행위 분류표

| 파일 | 정보 탈취 | 파일 파괴 | 지속성 | C2 통신 | 패킹 | 안티디버깅 |
|---|:-:|:-:|:-:|:-:|:-:|:-:|
| mal1.exe | ✗ | ✗ | ✗ | ✗ (다운로드만) | ✗ | ✓ (IDP) |
| mal2.exe | ✓ (북마크) | ✗ | ✗ | ✗ | ✗ | ✓ (IDP) |
| mal3.exe | ✓ (키입력) | ✗ | ? | ✓ (C2 POST) | ✓ UPX | ? |
| mal4.exe | ✓ (화면) | ✗ | ? | ✗ | ✗ | ✓ (IDP) |
| mal5.exe | ✗ | ✓ (암호화) | ? | ? | ✓ UPX | ? |
| r1.exex | ✓ (시스템정보) | ✓ (암호화) | ✓ (레지) | ✓ (HTTP+소켓) | ✗ | ? |
| r2.exex | ✓ (키입력) | ✗ | ✗ | ✗ | ✗ | ✗ |

*IDP = IsDebuggerPresent*

### 위협 수준

```
매우 높음: r1.exex (CryptoShield 랜섬웨어, 실제 피해 사례 존재)
높음:      mal3.exe (키로거 + C2), mal5.exe (랜섬웨어)
중간:      mal2.exe (피싱 유도), mal4.exe (스크린샷), r2.exex (키로거)
낮음:      mal1.exe (배경화면 변경)
```

### 공통 패턴

1. **IsDebuggerPresent** — mal1·2·4 모두 임포트 → 분석 환경 탐지
2. **UPX 패킹** — mal3·5는 패킹으로 정적 분석 방해 + 엔트로피 7.4~7.8
3. **동적 API 로딩** — mal3·5: `LoadLibraryA + GetProcAddress` → 임포트 테이블 은닉
4. **C2 없는 로컬 저장** — mal4·r2: 별도 exfil 도구와 조합 사용 의도

---

## §9 정적 분석 한계 및 권장 추가 분석

| 샘플 | 한계 | 권장 |
|---|---|---|
| mal3·mal5 | UPX로 실제 코드 미확인 | `upx -d` 언팩 후 재분석 또는 동적 분석 |
| mal5 | CryptEncrypt 대상 파일 확장자 불명 | 샌드박스(Cuckoo) 실행 → 파일 변경 모니터링 |
| r1 | 암호화 알고리즘 세부 불명 | IDA로 Crypt* 함수 역어셈블 |
| r2 | Keylogs.txt 저장 경로 불명 | 동적 분석으로 실제 저장 위치 확인 |

> **안전 주의**: 실제 실행 시 반드시 **스냅샷 복원 가능한 가상머신 격리 환경** 사용
