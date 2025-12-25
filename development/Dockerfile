# Base Image: 가볍고 보안성이 높은 Python Slim 버전 사용
FROM python:3.10-slim

# 환경 변수 설정
# PYTHONDONTWRITEBYTECODE: .pyc 파일 생성 방지
# PYTHONUNBUFFERED: 로그를 즉시 콘솔로 출력
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONPATH=/app

# 작업 디렉토리 설정
WORKDIR /app

# 시스템 의존성 설치 (필요시 gcc 등 컴파일러 포함)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# 의존성 패키지 설치
# 캐시 효율성을 위해 requirements.txt만 먼저 복사
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 소스 코드 복사
COPY src/ src/
COPY .env .

# 실행 권한 설정 (선택사항)
RUN useradd -m appuser && chown -R appuser /app
USER appuser

# 기본 실행 명령 (Docker Compose에서 덮어쓸 예정)
CMD ["python", "src/main.py"]