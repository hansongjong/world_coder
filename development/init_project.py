import os
import sys
from pathlib import Path

# 프로젝트 루트 디렉토리 설정
BASE_DIR = Path(__file__).resolve().parent

# 생성할 디렉토리 구조 정의 (Clean Architecture 기반)
DIRS = [
    "src",
    "src/core",         # 설정, 로깅, 예외처리 등 공통 모듈
    "src/domain",       # 엔티티, 도메인 로직 (비즈니스 규칙)
    "src/application",  # 유스케이스, 서비스 인터페이스
    "src/infrastructure", # DB, 외부 API 어댑터
    "src/interface",    # API 라우터, CLI 커맨드 등 진입점
    "tests",            # 테스트 코드
    "tests/unit",
    "tests/integration",
    "docs",             # 문서화
    "logs",             # 로그 파일 저장소
    "scripts",          # 유틸리티 스크립트
]

# 생성할 초기 파일 및 기본 내용
FILES = {
    "src/__init__.py": "",
    "src/core/__init__.py": "",
    "src/core/config.py": "\"\"\"\nGlobal Configuration Management\nLoads environment variables and sets up project constants.\n\"\"\"\n\nclass Settings:\n    PROJECT_NAME: str = \"World Coder System\"\n    VERSION: str = \"1.0.0\"\n\nsettings = Settings()\n",
    "src/core/exceptions.py": "\"\"\"\nCustom Exception Classes\n\"\"\"\n\nclass BaseSystemException(Exception):\n    \"\"\"Root exception for the system.\"\"\"\n    pass\n",
    "src/main.py": "\"\"\"\nApplication Entry Point\n\"\"\"\n\ndef main():\n    print(\"System Initialized.\")\n\nif __name__ == \"__main__\":\n    main()\n",
    ".env.example": "# Security Warning: Do not commit actual secrets.\nDEBUG=True\nSECRET_KEY=change_me\nDATABASE_URL=sqlite:///./local.db\n",
    "pytest.ini": "[pytest]\ntestpaths = tests\npython_files = test_*.py\n",
}

def create_structure():
    print(f"[*] Initializing Project Structure in: {BASE_DIR}")
    
    # 1. 디렉토리 생성
    for directory in DIRS:
        dir_path = BASE_DIR / directory
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            print(f"    [CREATED] Directory: {directory}")
        else:
            print(f"    [EXISTS]  Directory: {directory}")
            
    # 2. 파일 생성
    for file_path_str, content in FILES.items():
        file_path = BASE_DIR / file_path_str
        if not file_path.exists():
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(content)
            print(f"    [CREATED] File: {file_path_str}")
        else:
            print(f"    [EXISTS]  File: {file_path_str}")

    print("\n[SUCCESS] Project Scaffolding Complete.")
    print("Please install dependencies via 'pip install -r requirements.txt'")

if __name__ == "__main__":
    create_structure()