import os
import shutil
import sys
import subprocess
from pathlib import Path

# 경로 설정
ROOT_DIR = Path(__file__).resolve().parent
POS_DIR = ROOT_DIR / "tg_pos_app"
BUILD_DIR = POS_DIR / "build"
LIB_DIR = POS_DIR / "lib"
REPAIR_SCRIPT = ROOT_DIR / "scripts" / "repair_pos_project.py"

def force_delete(path):
    """권한 문제 무시하고 강제 삭제"""
    if path.exists():
        print(f"[-] Deleting {path}...")
        try:
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                os.remove(path)
        except Exception as e:
            print(f"[!] Delete failed: {e}")

def verify_files():
    """핵심 파일 존재 여부 검증"""
    print("\n[*] Verifying Source Files...")
    required = [
        "lib/main.dart",
        "lib/screens/login_screen.dart",
        "lib/screens/pos_screen_v3.dart",
        "pubspec.yaml"
    ]
    missing = []
    for f in required:
        p = POS_DIR / f
        if not p.exists():
            print(f"    [MISSING] {f}")
            missing.append(f)
        else:
            print(f"    [OK] {f} ({p.stat().st_size} bytes)")
    
    if missing:
        print("[!] Critical files are missing. Attempting repair...")
        return False
    return True

def main():
    print("=== TG-POS FORCE REBUILD SYSTEM ===\n")

    # 1. 빌드 캐시 강제 삭제 (flutter clean보다 강력함)
    print("[*] Step 1: Nuke Build Cache")
    force_delete(BUILD_DIR)
    force_delete(POS_DIR / ".dart_tool")
    force_delete(POS_DIR / "windows/flutter/ephemeral")

    # 2. 소스 코드 복구 (Repair Script 실행)
    print("\n[*] Step 2: Restore Source Code")
    subprocess.call([sys.executable, str(REPAIR_SCRIPT)])

    # 3. 파일 검증
    if not verify_files():
        print("[!] Repair failed. Please check 'repair_pos_project.py'")
        sys.exit(1)

    # 4. 의존성 재설치 및 플랫폼 파일 복구
    print("\n[*] Step 3: Re-configure Flutter")
    os.chdir(POS_DIR)
    
    # Windows 설정 강제 활성화
    subprocess.call("flutter config --enable-windows-desktop", shell=True)
    
    # 플랫폼 파일 재생성 (중요)
    if not (POS_DIR / "windows").exists():
        subprocess.call("flutter create . --platforms=windows", shell=True)
    
    subprocess.call("flutter pub get", shell=True)

    # 5. 실행
    print("\n[*] Step 4: LAUNCHING APP...")
    print("    (This will take a while. Do not close window.)")
    ret = subprocess.call("flutter run -d windows -v", shell=True) # -v 옵션으로 상세 로그 출력

    if ret != 0:
        print("\n[ERROR] Build Failed again.")
        print("Tip: If error persists, try moving the project to 'C:\\src' to avoid long paths.")
        input("Press Enter to exit...")

if __name__ == "__main__":
    main()