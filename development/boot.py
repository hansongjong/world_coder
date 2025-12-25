import sys
import subprocess
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
REQ_FILE = BASE_DIR / "requirements.txt"
MIGRATE_SCRIPT = BASE_DIR / "src" / "database" / "auto_migrate.py"
MAIN_SCRIPT = BASE_DIR / "src" / "main.py"

def install_dependencies():
    print(f"[*] [Step 1] Checking dependencies...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", str(REQ_FILE)
        ])
    except subprocess.CalledProcessError:
        print("[!] Dependency installation failed.")
        sys.exit(1)

def run_migrations():
    print(f"[*] [Step 2] Checking Database Schema...")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BASE_DIR)
    try:
        subprocess.run([sys.executable, str(MIGRATE_SCRIPT)], env=env, check=True)
    except subprocess.CalledProcessError:
        print("[!] DB Migration failed.")
        sys.exit(1)

def run_server():
    print(f"[*] [Step 3] Starting TG-SYSTEM Kernel...")
    env = os.environ.copy()
    env["PYTHONPATH"] = str(BASE_DIR)
    try:
        subprocess.run([sys.executable, str(MAIN_SCRIPT)], env=env)
    except KeyboardInterrupt:
        print("\n[!] Server stopped.")

if __name__ == "__main__":
    # 인자 확인
    mode = "run"
    if len(sys.argv) > 1 and sys.argv[1] == "setup":
        mode = "setup"

    print(f"=== TG-SYSTEM BOOTSTRAPPER ({mode.upper()} MODE) ===")
    
    install_dependencies()
    run_migrations()
    
    if mode == "setup":
        print("[+] Setup Complete. Exiting...")
        sys.exit(0)
    else:
        run_server()