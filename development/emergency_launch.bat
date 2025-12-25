@echo off
title TG-SYSTEM EMERGENCY LAUNCHER

echo [1/2] Attempting to open Web POS (Fallback)...
REM HTML 파일을 브라우저로 바로 엽니다 (서버가 켜져 있어야 함)
start http://localhost:8001/

echo.
echo [2/2] Attempting to run Flutter App (Plan A)...
echo If this fails, please use the Web Browser window opened above.
echo.

cd tg_pos_app
call flutter run -d chrome

pause