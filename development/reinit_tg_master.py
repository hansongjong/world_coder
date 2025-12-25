import os
import sys
from pathlib import Path

# 프로젝트 루트
BASE_DIR = Path(__file__).resolve().parent

# TG_MASTER에 최적화된 폴더 구조
DIRS = [
    "src",
    "src/core",          # 설정(API_ID/HASH), 로깅
    "src/domain",        # Telegram 계정, 작업(Task) 모델
    "src/usecase",       # 메시지 전송, 그룹 추출 등 비즈니스 로직
    "src/infrastructure",# Telethon 클라이언트 래퍼, DB 연결
    "src/interface",     # CLI 또는 GUI 엔트리 포인트
    "sessions",          # .session 파일 저장소 (보안 주의)
    "data",              # 타겟 유저 목록, 추출 데이터 등
    "logs",              # 실행 로그
    "tests"
]

FILES = {
    "src/__init__.py": "",
    "sessions/.gitkeep": "",
    "data/.gitkeep": "",
    "src/core/config.py": "",  # 내용은 아래에서 별도 작성
    ".env": "# Telegram API Info (my.telegram.org)\nAPI_ID=123456\nAPI_HASH=your_api_hash_here\nADMIN_PHONE=+821000000000\n",
    "requirements.txt": "telethon>=1.30.0\npydantic>=2.0.0\npython-dotenv>=1.0.0\nloguru>=0.7.0\nsqlalchemy>=2.0.0\npytest-asyncio>=0.21.0\n",
    "README.md": "# TG_MASTER\n\nTelegram Automation & Marketing Tool developed by CODER-X.\nBased on TG_MASTER_DESIGN specs.\n"
}

def reinit_structure():
    print(f"[*] Re-initializing TG_MASTER Project in: {BASE_DIR}")
    
    for directory in DIRS:
        dir_path = BASE_DIR / directory
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"    [OK] Directory: {directory}")

    for file_path_str, content in FILES.items():
        file_path = BASE_DIR / file_path_str
        # 기존 파일이 있어도 덮어쓰기 (잘못된 내용 수정)
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"    [RESET] File: {file_path_str}")

    print("\n[SUCCESS] TG_MASTER Structure Ready.")

if __name__ == "__main__":
    reinit_structure()