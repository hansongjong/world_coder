@echo off
echo [TG-SYSTEM] Stopping all services...

REM 1. TG-CORE 창 찾아서 종료
taskkill /FI "WINDOWTITLE eq TG-CORE*" /T /F >nul 2>&1
if %errorlevel% equ 0 (
    echo    - Core Kernel stopped.
) else (
    echo    - Core Kernel was not running.
)

REM 2. TG-COMMERCE 창 찾아서 종료
taskkill /FI "WINDOWTITLE eq TG-COMMERCE*" /T /F >nul 2>&1
if %errorlevel% equ 0 (
    echo    - Commerce Engine stopped.
) else (
    echo    - Commerce Engine was not running.
)

REM 3. 혹시 모를 잔여 python.exe 정리 (선택 사항 - 주석 처리됨)
REM 주의: 다른 파이썬 프로그램도 꺼질 수 있으므로 기본은 주석 처리
REM taskkill /IM python.exe /F >nul 2>&1

echo.
echo [SUCCESS] System Shutdown Complete.
pause