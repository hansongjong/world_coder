import os
import sys
import subprocess
from pathlib import Path

# 경로 설정
ROOT_DIR = Path(__file__).resolve().parent
POS_DIR = ROOT_DIR / "tg_pos_app"
REPAIR_SCRIPT = ROOT_DIR / "scripts" / "repair_pos_project.py"

def run_command(cmd, cwd=None):
    """명령어 실행 래퍼"""
    print(f"\n[EXEC] {cmd}")
    try:
        # shell=True는 윈도우에서 명령어 인식을 위해 필요
        subprocess.check_call(cmd, shell=True, cwd=cwd)
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {e}")
        sys.exit(1)

def main():
    print("=== TG-POS AUTO FIX & RUN SYSTEM ===")
    
    # 1. 소스 코드 복구 (Repair Script 실행)
    print("\n[*] Step 1: Repairing Source Code...")
    run_command(f'"{sys.executable}" "{REPAIR_SCRIPT}"')
    
    # 2. 빌드 캐시 청소 (Flutter Clean)
    print("\n[*] Step 2: Cleaning Build Cache...")
    if (POS_DIR / "pubspec.yaml").exists():
        run_command("flutter clean", cwd=POS_DIR)
        run_command("flutter pub get", cwd=POS_DIR)
    else:
        print("[!] Flutter project not found. Creating new...")
        run_command(f'flutter create "{POS_DIR}" --platforms=windows')
        # 생성 후 다시 소스 덮어쓰기
        run_command(f'"{sys.executable}" "{REPAIR_SCRIPT}"')

    # 3. 앱 실행 (Launch)
    print("\n[*] Step 3: Launching POS App...")
    print("    (Please wait for the build to finish...)")
    run_command("flutter run -d windows", cwd=POS_DIR)

if __name__ == "__main__":
    main()