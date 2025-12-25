@echo off
setlocal

REM 1. 경로 설정 (따옴표로 감싸서 공백 오류 방지)
set "PYTHON_EXE=C:\Users\blue\AppData\Local\Programs\Python\Python313\python.exe"
set "BASE_DIR=%~dp0"
set "POS_DIR=%BASE_DIR%tg_pos_app"

echo [SAFE-MODE] Starting Diagnostics...
echo Work Dir: %BASE_DIR%

REM 2. Python 실행 확인
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python executable not found at: %PYTHON_EXE%
    echo Please check the path.
    goto :error
)

REM 3. Flutter 프로젝트 확인
if not exist "%POS_DIR%" (
    echo [ERROR] POS Directory not found: %POS_DIR%
    goto :error
)

REM 4. 서버 확인 및 실행
echo [CHECK] Core Servers...
tasklist /FI "IMAGENAME eq python.exe" | findstr "python.exe" >nul
if %errorlevel% neq 0 (
    echo [WARN] Servers down. Starting...
    start /min "CORE" "%PYTHON_EXE%" src/main.py
    start /min "COMMERCE" "%PYTHON_EXE%" src/main_commerce.py
    timeout /t 5 >nul
) else (
    echo [OK] Servers are running.
)

REM 5. 앱 실행 시도
echo [EXEC] Flutter Run...
cd /d "%POS_DIR%"
call flutter run -d windows -v

if %errorlevel% neq 0 (
    echo [CRITICAL] Flutter run failed with exit code %errorlevel%.
    goto :error
)

goto :end

:error
color 4f
echo.
echo =================================================
echo  FATAL ERROR OCCURRED
echo =================================================
echo  The window will remain open for inspection.
echo.
cmd /k
exit /b

:end
echo [SUCCESS] App closed normally.
pause