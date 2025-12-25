@echo off
setlocal

set PYTHON_EXE=C:\Users\blue\AppData\Local\Programs\Python\Python313\python.exe
set POS_DIR=%~dp0tg_pos_app

echo [POS-BUILDER] Checking Project...

REM 1. 프로젝트 없으면 생성
if not exist "%POS_DIR%" (
    call flutter create "%POS_DIR%" --platforms=windows
)

REM 2. 소스 코드 강제 주입
echo [POS-BUILDER] Injecting Source Code...
"%PYTHON_EXE%" scripts/build_pos_project.py

REM 3. [중요] 빌드 캐시 강제 삭제 (Deep Clean)
echo [POS-BUILDER] Removing build cache...
if exist "%POS_DIR%\build" (
    rmdir /s /q "%POS_DIR%\build"
    echo    - Build folder removed.
)
if exist "%POS_DIR%\.dart_tool" (
    rmdir /s /q "%POS_DIR%\.dart_tool"
    echo    - Dart tool cache removed.
)

REM 4. 의존성 재설치
cd "%POS_DIR%"
echo [POS-BUILDER] Fetching dependencies...
call flutter pub get

REM 5. 실행
echo.
echo [POS-BUILDER] Launching App (Clean Build)...
echo This will take longer than usual...
call flutter run -d windows

if %errorlevel% neq 0 (
    echo [ERROR] Build Failed.
    pause
)