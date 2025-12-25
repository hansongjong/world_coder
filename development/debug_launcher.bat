@echo off
setlocal

set PYTHON_EXE=C:\Users\blue\AppData\Local\Programs\Python\Python313\python.exe
set POS_DIR=%~dp0tg_pos_app

title TG-SYSTEM DEBUG CONSOLE

echo ========================================================
echo  TG-SYSTEM DIAGNOSTIC LAUNCHER
echo ========================================================

echo.
echo [1/3] Checking Backend Servers...
tasklist /FI "IMAGENAME eq python.exe" | findstr "python.exe" >nul
if %errorlevel% neq 0 (
    echo [WARN] Servers are NOT running. Starting them now...
    start "TG-CORE" "%PYTHON_EXE%" src/main.py
    start "TG-COMMERCE" "%PYTHON_EXE%" src/main_commerce.py
    timeout /t 3 >nul
) else (
    echo [OK] Python processes are running.
)

echo.
echo [2/3] Checking Project Files...
if not exist "%POS_DIR%\lib\screens\login_screen.dart" (
    echo [ERROR] Critical source file missing: login_screen.dart
    echo Attempting auto-repair...
    "%PYTHON_EXE%" fix_code_final.py
) else (
    echo [OK] Source files exist.
)

echo.
echo [3/3] Launching Flutter App (Verbose Mode)...
echo --------------------------------------------------------
echo  If this step fails, it usually means:
echo  1. Visual Studio C++ Tools are missing.
echo  2. Flutter SDK is not in PATH.
echo  3. A previous build process is stuck.
echo --------------------------------------------------------
echo.

cd "%POS_DIR%"
echo Running: flutter run -d windows -v
flutter run -d windows -v

echo.
echo [FINISHED] The app process has ended.
pause