@echo off
setlocal enabledelayedexpansion

REM ==========================================
REM TG-SYSTEM Parallel Launcher (cmd /k version)
REM ==========================================

REM 1. 환경 설정
set PYTHON_EXE=C:\Users\blue\AppData\Local\Programs\Python\Python313\python.exe
set PROJECT_DIR=%~dp0
cd /d "%PROJECT_DIR%"

echo [LAUNCHER] Root Dir: %PROJECT_DIR%

REM 2. 설정 모드 실행 (Blocking)
echo [LAUNCHER] Running Setup (Wait for completion)...
"%PYTHON_EXE%" boot.py setup

if %errorlevel% neq 0 (
    echo [ERROR] Setup failed.
    pause
    exit /b
)

echo.
echo [LAUNCHER] Spawning Server Windows...

REM 3. Core 서버 실행 (Non-Blocking, New Window)
REM "start" 다음의 첫 번째 따옴표는 창 제목입니다.
REM cmd /k는 명령 실행 후 창을 유지합니다.
start "TG-CORE (Port 8000)" cmd /k ""%PYTHON_EXE%" src/main.py"

REM 약간의 딜레이를 주어 포트 충돌 가능성 최소화
timeout /t 2 >nul

REM 4. Commerce 서버 실행 (Non-Blocking, New Window)
start "TG-COMMERCE (Port 8001)" cmd /k ""%PYTHON_EXE%" src/main_commerce.py"

echo.
echo [SUCCESS] Commands sent. Check the two new windows.
echo ---------------------------------------------------
echo  1. TG-CORE window should be running on Port 8000
echo  2. TG-COMMERCE window should be running on Port 8001
echo ---------------------------------------------------
echo This launcher will close in 5 seconds...
timeout /t 5