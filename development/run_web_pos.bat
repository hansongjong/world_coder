@echo off
setlocal

set POS_DIR=%~dp0tg_pos_app

echo [POS-WEB] Switching to Web Mode...

REM 1. 웹 지원 활성화
call flutter config --enable-web >nul 2>&1

REM 2. 프로젝트 폴더가 없으면 생성
if not exist "%POS_DIR%" (
    call flutter create "%POS_DIR%" --platforms=web
) else (
    REM web 폴더가 없으면 생성
    if not exist "%POS_DIR%\web" (
        cd "%POS_DIR%"
        call flutter create . --platforms=web
        cd ..
    )
)

REM 3. 웹 실행 (크롬)
echo.
echo [POS-WEB] Launching in Chrome...
echo This does NOT require Visual Studio C++.
echo.

cd "%POS_DIR%"
call flutter run -d chrome

if %errorlevel% neq 0 (
    echo [ERROR] Web launch failed.
    pause
)