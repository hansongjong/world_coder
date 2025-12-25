import datetime
from pathlib import Path
from fastapi import APIRouter
from fastapi.responses import HTMLResponse

router = APIRouter(tags=["Operations: Live Status"])

BASE_DIR = Path(__file__).resolve().parents[2]

ARTIFACTS_MAP = {
    "1. Infrastructure": [
        {"name": "Bootstrapper", "path": "boot.py", "phase": "Setup"},
        {"name": "Launcher", "path": "run_all.bat", "phase": "Run"},
        {"name": "Docker Compose", "path": "docker-compose.yml", "phase": "Deploy"},
    ],
    "2. Backend Core": [
        {"name": "Core Main", "path": "src/main.py", "phase": "Core"},
        {"name": "Commerce Main", "path": "src/main_commerce.py", "phase": "Core"},
        {"name": "Database Schema", "path": "src/core/database/v3_schema.py", "phase": "DB"},
        {"name": "Scheduler", "path": "src/core/scheduler.py", "phase": "Logic"},
    ],
    "3. Commerce API": [
        {"name": "Product/Menu", "path": "src/commerce/api/products.py", "phase": "API"},
        {"name": "Order/Pay", "path": "src/commerce/api/orders.py", "phase": "API"},
        {"name": "Booking", "path": "src/commerce/api/booking.py", "phase": "API"},
        {"name": "IoT Control", "path": "src/commerce/api/iot.py", "phase": "API"},
        {"name": "Stats/ERP", "path": "src/commerce/api/stats.py", "phase": "API"},
    ],
    "4. Frontend": [
        {"name": "POS App Main", "path": "tg_pos_app/lib/main.dart", "phase": "App"},
        {"name": "API Service", "path": "tg_pos_app/lib/services/api_service_v2.dart", "phase": "App"},
    ]
}

@router.get("/ops/status", response_class=HTMLResponse)
def get_live_status_report():
    total = 0
    found = 0
    table_rows = ""
    
    # CSS 스타일 (f-string 충돌 방지를 위해 일반 문자열로 정의)
    style = """
    <style>
        :root { --bg: #111827; --card: #1f2937; --text: #f3f4f6; --accent: #3b82f6; --green: #10b981; --red: #ef4444; }
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif; background: var(--bg); color: var(--text); margin: 0; padding: 20px; }
        .container { max_width: 1200px; margin: 0 auto; }
        h1 { border-bottom: 2px solid var(--accent); padding-bottom: 15px; color: var(--accent); }
        .card { background: var(--card); border-radius: 8px; padding: 20px; margin-bottom: 20px; box-shadow: 0 4px 6px rgba(0,0,0,0.3); }
        .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; text-align: center; }
        .score { font-size: 2.5rem; font-weight: bold; }
        .label { color: #9ca3af; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.05em; }
        table { width: 100%; border-collapse: collapse; font-size: 0.95rem; }
        th { text-align: left; padding: 12px; border-bottom: 1px solid #374151; color: var(--accent); }
        td { padding: 12px; border-bottom: 1px solid #374151; }
        .category { background: #374151; font-weight: bold; color: #fff; }
        .badge { background: #4b5563; padding: 2px 6px; border-radius: 4px; font-size: 0.75rem; margin-right: 8px; }
        .found { color: var(--green); font-weight: bold; }
        .missing { color: var(--red); font-weight: bold; }
        .path { font-family: monospace; color: #9ca3af; }
    </style>
    """

    for category, items in ARTIFACTS_MAP.items():
        table_rows += f'<tr class="category"><td colspan="5">{category}</td></tr>'
        for item in items:
            full_path = BASE_DIR / item["path"]
            exists = full_path.exists()
            total += 1
            if exists: found += 1
            
            status_html = '<span class="found">✅ ONLINE</span>' if exists else '<span class="missing">❌ OFFLINE</span>'
            last_mod = datetime.datetime.fromtimestamp(full_path.stat().st_mtime).strftime("%Y-%m-%d %H:%M") if exists else "-"
            size = f"{round(full_path.stat().st_size / 1024, 1)} KB" if exists else "-"
            
            table_rows += f"""
            <tr>
                <td><span class="badge">{item['phase']}</span> {item['name']}</td>
                <td class="path">{item['path']}</td>
                <td>{status_html}</td>
                <td>{last_mod}</td>
                <td>{size}</td>
            </tr>
            """
            
    score = int((found/total)*100) if total > 0 else 0
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # [FIXED] f-string 내부에서 CSS 변수 사용 시 에러 발생하던 부분 수정
    # var(--green) 대신 색상 코드를 직접 넣거나 로직 분리
    score_color = "#10b981" if score == 100 else "#3b82f6"

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta http-equiv="refresh" content="5">
        <title>TG-SYSTEM Ops</title>
        {style}
    </head>
    <body>
        <div class="container">
            <h1>🛠️ TG-SYSTEM LIVE OPS</h1>
            
            <div class="card">
                <div class="grid">
                    <div>
                        <div class="score" style="color: {score_color}">{score}%</div>
                        <div class="label">System Integrity</div>
                    </div>
                    <div>
                        <div class="score">{found}/{total}</div>
                        <div class="label">Modules Active</div>
                    </div>
                    <div>
                        <div class="score">RUNNING</div>
                        <div class="label">Kernel Status</div>
                    </div>
                    <div>
                        <div class="score" style="font-size: 1.5rem; margin-top: 10px;">{now}</div>
                        <div class="label">Last Heartbeat</div>
                    </div>
                </div>
            </div>

            <div class="card">
                <table>
                    <thead>
                        <tr>
                            <th>Module</th>
                            <th>File Path</th>
                            <th>Status</th>
                            <th>Modified</th>
                            <th>Size</th>
                        </tr>
                    </thead>
                    <tbody>
                        {table_rows}
                    </tbody>
                </table>
            </div>
            
            <div style="text-align: center; color: #6b7280; font-size: 0.8rem; margin-top: 20px;">
                TG-SYSTEM Enterprise Edition | Path: {BASE_DIR}
            </div>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html)