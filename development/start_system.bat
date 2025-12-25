@echo off
echo [TG-SYSTEM] Starting Enterprise Environment...

REM 1. Docker 설치 확인
docker --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERROR] Docker is not installed. Please install Docker Desktop first.
    pause
    exit /b
)

REM 2. 기존 컨테이너 정리
echo [*] Cleaning up old containers...
docker-compose down

REM 3. 시스템 빌드 및 실행
echo [*] Building and Starting Services...
docker-compose up -d --build

echo.
echo [SUCCESS] TG-SYSTEM is running!
echo - Gateway: http://localhost/health
echo - Core API: http://localhost/api/core/docs
echo - Commerce API: http://localhost/api/commerce/docs
echo.
pause