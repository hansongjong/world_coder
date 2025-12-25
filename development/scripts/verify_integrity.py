import os
from pathlib import Path
from rich.console import Console
from rich.table import Table

console = Console()

# 프로젝트 루트
BASE_DIR = Path(__file__).resolve().parents[2]

# 검증할 핵심 파일 목록 (Critical Artifacts)
CHECK_LIST = {
    "1. Core Backend": [
        "src/main.py",
        "src/core/config.py",
        "src/core/database/v3_schema.py",
        "src/api/routes_report.py"
    ],
    "2. Commerce Backend": [
        "src/main_commerce.py",
        "src/commerce/api/orders.py",
        "src/commerce/api/booking.py",
        "src/commerce/auth/routes.py"
    ],
    "3. POS App (Flutter)": [
        "tg_pos_app/pubspec.yaml",
        "tg_pos_app/lib/main.dart",
        "tg_pos_app/lib/services/api_service.dart",
        "tg_pos_app/lib/providers/cart_provider.dart",
        # [중요] 누락 이슈가 있었던 파일들 집중 점검
        "tg_pos_app/lib/screens/login_screen.dart",
        "tg_pos_app/lib/screens/pos_screen_v3.dart",
        "tg_pos_app/lib/screens/reservation_screen.dart",
        "tg_pos_app/lib/widgets/payment_modal.dart",
        "tg_pos_app/lib/widgets/receipt_dialog.dart"
    ],
    "4. Infrastructure": [
        "Dockerfile",
        "docker-compose.yml",
        "run_all.bat",
        "run_pos.bat"
    ]
}

def verify_files():
    console.print(f"[bold cyan]🔍 TG-SYSTEM File Integrity Check[/bold cyan]")
    console.print(f"Root: {BASE_DIR}\n")
    
    all_passed = True
    
    for category, files in CHECK_LIST.items():
        table = Table(title=category, show_header=True, header_style="bold magenta", expand=True)
        table.add_column("File Path")
        table.add_column("Status", justify="center")
        table.add_column("Size", justify="right")
        
        for file_rel_path in files:
            full_path = BASE_DIR / file_rel_path
            
            if full_path.exists():
                size = full_path.stat().st_size
                status = "[green]OK[/green]"
                size_str = f"{size} B"
                
                # 파일이 비어있는지 확인 (0 바이트면 문제)
                if size == 0:
                    status = "[yellow]EMPTY[/yellow]"
                    all_passed = False
            else:
                status = "[red]MISSING[/red]"
                size_str = "-"
                all_passed = False
            
            table.add_row(str(file_rel_path), status, size_str)
            
        console.print(table)
        console.print()

    if all_passed:
        console.print("[bold green]✅ SYSTEM INTEGRITY VERIFIED[/bold green]")
        console.print("All critical files are present and valid.")
    else:
        console.print("[bold red]❌ INTEGRITY CHECK FAILED[/bold red]")
        console.print("Some files are missing or empty. Please re-run build scripts.")

if __name__ == "__main__":
    verify_files()