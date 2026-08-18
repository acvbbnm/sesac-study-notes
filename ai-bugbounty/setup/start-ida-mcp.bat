@echo off
chcp 65001 >nul
REM ============================================================
REM  start-ida-mcp.bat
REM  IDA Pro 9.x + ida-pro-mcp 를 켜고 Kali(게스트 VM)에서
REM  붙을 수 있도록 준비하는 스크립트
REM
REM  사용법:  start-ida-mcp.bat  C:\samples\target.exe
REM           start-ida-mcp.bat  C:\samples\target.i64
REM           (인자 없이 실행하면 IDA만 그냥 띄움)
REM
REM  ※ 방화벽 규칙 등록 때문에 "관리자 권한으로 실행" 권장.
REM     한 번 등록되면 그 다음부터는 일반 권한으로 실행해도 됨.
REM ============================================================

setlocal EnableDelayedExpansion

REM ---- 1) 환경 설정 (본인 환경에 맞게 수정) -------------------
set "IDA_DIR=C:\Program Files\IDA Professional 9.3"
set "MCP_PORT=13337"
set "FW_RULE=IDA MCP %MCP_PORT%"
REM -------------------------------------------------------------

if not exist "%IDA_DIR%\ida.exe" (
    echo [!] IDA 를 찾을 수 없습니다: "%IDA_DIR%\ida.exe"
    echo     이 파일 위쪽의 IDA_DIR 값을 실제 설치 경로로 고쳐주세요.
    pause
    exit /b 1
)

REM ---- 2) 방화벽 인바운드 규칙 (없으면 생성) -------------------
netsh advfirewall firewall show rule name="%FW_RULE%" >nul 2>&1
if errorlevel 1 (
    echo [*] 방화벽 규칙 추가 중: %FW_RULE%
    netsh advfirewall firewall add rule name="%FW_RULE%" dir=in action=allow protocol=TCP localport=%MCP_PORT% profile=any >nul 2>&1
    if errorlevel 1 (
        echo [!] 방화벽 규칙 추가 실패 - 관리자 권한으로 다시 실행하세요.
    ) else (
        echo [+] 방화벽 규칙 추가 완료.
    )
) else (
    echo [=] 방화벽 규칙 이미 존재.
)

REM ---- 3) IDA 실행 --------------------------------------------
if "%~1"=="" (
    echo [*] IDA 실행 ^(분석 대상 없음^)
    start "" "%IDA_DIR%\ida.exe"
) else (
    echo [*] IDA 실행: %~1
    start "" "%IDA_DIR%\ida.exe" "%~1"
)

REM ---- 4) MCP 서버가 실제로 LISTEN 하는지 확인 -----------------
echo [*] MCP 서버 기동 대기 중 ^(최대 30초^)...
set /a tries=0
:WAITLOOP
timeout /t 2 /nobreak >nul
netstat -ano | findstr /r /c:"LISTENING" | findstr ":%MCP_PORT% " >nul 2>&1
if not errorlevel 1 goto UP
set /a tries+=1
if !tries! lss 15 goto WAITLOOP

echo.
echo [!] %MCP_PORT% 포트가 열리지 않았습니다.
echo     IDA 안에서 Ctrl+Alt+M ^(Edit ^> Plugins ^> MCP Configuration^) 을 눌러
echo     Host=0.0.0.0 / Port=%MCP_PORT% / Autostart 체크 후 서버를 켜주세요.
goto SHOWIP

:UP
echo [+] MCP 서버 LISTENING 확인:
netstat -ano | findstr /r /c:"LISTENING" | findstr ":%MCP_PORT% "

:SHOWIP
echo.
echo ============================================================
echo  Kali 에서 아래 주소 중 하나로 붙으세요:
echo ============================================================
for /f "tokens=2 delims=:" %%A in ('ipconfig ^| findstr /c:"IPv4"') do (
    set "IP=%%A"
    set "IP=!IP: =!"
    echo    http://!IP!:%MCP_PORT%/mcp
)
echo.
echo  Kali 명령어 예시:
echo    claude mcp add --transport http ida http://^<위_IP^>:%MCP_PORT%/mcp
echo ============================================================
echo.
pause
endlocal
